import copy
import os
import pty
import re
import signal
import time

from queue import Queue, Empty
from threading import Thread


IN = 1
OUT = 0


class _Reader:

    def __init__(self, stream, mode='line', convert_bytes=True):
        self._s = stream
        self._q = Queue()
        self.reading = True
        self.readmode = mode
        self.line = b''

        def _populate_queue(stream, queue):
            if self.readmode == 'line':
                while self.reading:
                    self.line = b''
                    while not len(self.line) or self.line[-1] != 10:
                        self.line += os.read(stream, 1)
                    queue.put((self.line, b'\n'))
            else:
                char = b''
                while self.reading:
                    if char == 10:
                        self.line = b''
                    char = os.read(stream, 1)
                    self.line += char
                    queue.put((self.line, char))

        self._t = Thread(target=_populate_queue, args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()

    def read(self, timeout=None):
        try:
            return self._q.get(block=timeout is not None, timeout=timeout)
        except Empty:
            return None, None


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
        self.private = False
        self.decode = True
        self.environ = copy.copy(os.environ)

    def __handle_line(self, line, char):
        if not self.private:
            if self.readmode == 'line':
                os.write(pty.STDOUT_FILENO, line)
            else:
                os.write(pty.STDOUT_FILENO, char)

        if 'when' in self.options:
            for w in self.options['when']:
                pattern = re.compile(w[0].encode())
                if re.match(pattern, line):
                    if self.decode:
                        w[1](self, line.decode())
                    else:
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

    def __empty_buffer(self):
        line, char = self.reader.read(0.01)
        while line or char:
            self.__handle_line(line, char)
            line, char = self.reader.read(0.01)

    def __loop(self):
        try:
            ret = os.waitpid(self.pid, os.WNOHANG)
            while ret == (0, 0):
                line, char = self.reader.read(0.01)
                if line or char:
                    self.__handle_line(line, char)
                ret = os.waitpid(self.pid, os.WNOHANG)

        except ChildProcessError:
            pass

        finally:
            self.__empty_buffer()
            self.return_value = ret

    def __fork(self, cmd):
        pid = os.fork()
        if pid:
            self.pid = pid
            os.close(self.pipes['parent_to_child'][OUT])
            os.close(self.pipes['child_to_parent'][IN])
            self.reader = _Reader(self.pipes['child_to_parent'][OUT],
                                  self.readmode)
            self.__input()
            self.__loop()

        else:
            os.dup2(self.pipes['parent_to_child'][OUT], pty.STDIN_FILENO)
            os.dup2(self.pipes['child_to_parent'][IN], pty.STDOUT_FILENO)
            os.close(self.pipes['parent_to_child'][IN])
            os.close(self.pipes['child_to_parent'][OUT])
            os.execve(cmd[0], cmd, self.environ)

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

        if 'private' in opt and opt['private']:
            self.private = True

        if 'readmode' in opt and opt['readmode'] == 'char':
            self.readmode = 'char'
        else:
            self.readmode = 'line'

        if 'decode' in opt and not opt['decode']:
            self.decode = False

        if 'detached' in opt and opt['detached'] is True:
            self.thread = Thread(target=self.__fork, args=(cmd,))
            self.thread.daemon = True
            self.thread.start()
        else:
            self.__fork(cmd)
        return self.return_value

    def wait(self):
        while self.return_value == (0, 0):
            time.sleep(0.1)
            continue
        self.__empty_buffer()
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
