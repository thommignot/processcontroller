import os
import pty
import re
import signal

from queue import Queue, Empty
from threading import Thread


IN = 1
OUT = 0


class _Reader:

    def __init__(self, stream):
        self._s = stream
        self._q = Queue()
        self.read = True

        def _populateQueue(stream, queue):
            while self.read:
                char = os.read(stream, 1).decode()
                queue.put(char)

        self._t = Thread(target=_populateQueue, args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()

    def readchar(self, timeout=None):
        try:
            return self._q.get(block=timeout is not None, timeout=timeout)
        except Empty:
            return None


class ProcessController():
    def __init__(self):
        self.pipes = {
            'parent_to_child': os.pipe(),
            'child_to_parent': os.pipe()
        }
        self.return_value = (0, 0)
        self.thread = self
        self.pid = 0
        self.closed = False

    def __handle_line(self, line, char):
        os.write(pty.STDOUT_FILENO, char.encode())
        if 'when' in self.options:
            for w in self.options['when']:
                pattern = re.compile(w[0])
                if re.match(pattern, line):
                    w[1](self, line)

    def __input(self):
        if 'input' in self.options:
            instr = self.options['input']
            if isinstance(instr, list):
                if len(instr) and isinstance(instr[0], str):
                    instr = '\n'.join(instr)
                elif len(instr) and isinstance(instr[0], bytes):
                    instr = b'\n'.join(instr)

            self.send(instr)

    def __loop(self):
        try:
            ret = os.waitpid(self.pid, os.WNOHANG)
            line = ''
            while ret == (0, 0):
                char = self.reader.readchar(0.01)
                if char:
                    line += char
                    self.__handle_line(line, char)
                if char == '\n':
                    line = ''
                ret = os.waitpid(self.pid, os.WNOHANG)

        except ChildProcessError:
            pass

        finally:
            char = self.reader.readchar(0.01)
            while char:
                line += char
                self.__handle_line(line, char)
                if char == '\n':
                    line == ''
                char = self.reader.readchar(0.01)
            self.reader.read = False
            self.return_value = ret

    def __fork(self, cmd):
        pid = os.fork()
        if pid:
            self.pid = pid
            os.close(self.pipes['parent_to_child'][OUT])
            os.close(self.pipes['child_to_parent'][IN])
            self.reader = _Reader(self.pipes['child_to_parent'][OUT])
            self.__input()
            self.__loop()

        else:
            os.dup2(self.pipes['parent_to_child'][OUT], pty.STDIN_FILENO)
            os.dup2(self.pipes['child_to_parent'][IN], pty.STDOUT_FILENO)
            os.close(self.pipes['parent_to_child'][IN])
            os.close(self.pipes['child_to_parent'][OUT])
            os.execve(cmd[0], cmd, os.environ)

    def send(self, s):
        if self.return_value != (0, 0):
            raise ChildProcessError

        if isinstance(s, str):
            s = s.encode()
        elif not isinstance(s, bytes):
            raise TypeError
        if 'echo' in self.options and self.options['echo']:
            print(s.decode())
        os.write(self.pipes['parent_to_child'][IN], s)
        os.write(self.pipes['parent_to_child'][IN], b'\n')

    def run(self, cmd, opt={}):
        if self.return_value != (0, 0):
            raise ChildProcessError

        self.options = opt

        if 'detached' in opt and opt['detached'] is True:
            self.thread = Thread(target=self.__fork, args=(cmd,))
            self.thread.daemon = True
            self.thread.start()
        else:
            self.__fork(cmd)
        return self.return_value

    def close(self):
        if self.return_value == (0, 0):
            if self.pid:
                os.close(self.pipes['parent_to_child'][IN])
                self.closed = True

    def kill(self):
        if self.return_value == (0, 0):
            if not self.closed:
                self.close()
            if self.pid:
                os.kill(self.pid, signal.SIGKILL)
