import os
import pty
import re

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
                line = ''
                while not len(line) or line[-1] != '\n':
                    line += os.read(stream, 1).decode()
                queue.put(line)

        self._t = Thread(target=_populateQueue, args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()

    def readline(self, timeout=None):
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
        self.return_value = None

    def __handle_line(self, s):
        print(s, end='')
        if 'when' in self.options:
            for w in self.options['when']:
                pattern = re.compile(w[0])
                if re.match(pattern, s):
                    w[1](self, s)

    def __fork(self, cmd):
        pid = os.fork()
        if pid:
            os.close(self.pipes['parent_to_child'][OUT])
            os.close(self.pipes['child_to_parent'][IN])

            self.reader = _Reader(self.pipes['child_to_parent'][OUT])
            try:
                ret = os.waitpid(pid, os.WNOHANG)
                while ret == (0, 0):
                    s = self.reader.readline(0.1)
                    if s:
                        self.__handle_line(s)
                    ret = os.waitpid(pid, os.WNOHANG)

            except ChildProcessError:
                pass

            finally:
                s = self.reader.readline(0.1)
                while s:
                    self.__handle_line(s)
                    s = self.reader.readline(0.1)
                self.reader.read = False
                return ret

        else:
            os.dup2(self.pipes['parent_to_child'][OUT], pty.STDIN_FILENO)
            os.dup2(self.pipes['child_to_parent'][IN], pty.STDOUT_FILENO)
            os.close(self.pipes['parent_to_child'][IN])
            os.close(self.pipes['child_to_parent'][OUT])
            os.execve(cmd[0], cmd, os.environ)

    def send(self, s):
        if isinstance(s, str):
            s = s.encode()
        elif not isinstance(s, bytes):
            raise TypeError
        if 'echo' in self.options and self.options['echo']:
            print(s.decode())
        os.write(self.pipes['parent_to_child'][IN], s)
        os.write(self.pipes['parent_to_child'][IN], b'\n')

    def run(self, cmd, opt={}):
        self.options = opt
        pid, self.return_value = self.__fork(cmd)
        return self.return_value
