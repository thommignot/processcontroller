import os
import pytest
import shutil
import time

from processcontroller import ProcessController, IN, OUT


PROG_PATH = os.path.dirname(__file__)


def path(prog_name):
    return os.path.join(PROG_PATH, prog_name)


def send_input(c, s):
    c.send('somestring')


def send_input_bytes(c, s):
    c.send(b'somestring')


def print_in_flow(c, s):
    print('in flow')


def increment(c, s):
    increment.counter += 1


increment.counter = 0


@pytest.fixture
def py():
    return shutil.which('python')


@pytest.fixture
def pc():
    return ProcessController()


def test_processcontroller_glob(pc):
    assert IN == 1
    assert OUT == 0


def test_processcontroller_no_opt(py, pc, capfd):
    pc.run([py, path('prog1.py')])
    capture = capfd.readouterr()
    assert capture.err == ''
    assert capture.out == 'one\ntwo\n'


def test_processcontroller_no_input(py, pc, capfd):
    pc.run([py, path('prog1.py')], {
        'when': [
            ['^one.*$\n', print_in_flow],
        ]
    })
    capture = capfd.readouterr()
    assert capture.err == ''
    assert capture.out == 'one\nin flow\ntwo\n'


def test_processcontroller_action(py, pc):
    increment.counter = 0
    pc.run([py, path('prog1.py')], {
        'when': [
            ['^one.*$\n', increment],
        ]
    })
    assert increment.counter == 1


def test_processcontroller_action_two(py, pc):
    increment.counter = 0
    pc.run([py, path('prog1.py')], {
        'when': [
            ['^one.*$\n', increment],
            ['^two.*$\n', increment],
        ]
    })
    assert increment.counter == 2


def test_processcontroller_send(py, pc, capfd):
    pc.run([py, path('prog2.py')], {
        'when': [
            ['^Please input.*\n', send_input],
        ]
    })
    capture = capfd.readouterr()
    assert capture.err == ''
    assert capture.out == 'Please input something:\n' + \
                          'Input was: "somestring"\n'


def test_processcontroller_send_bytes(py, pc, capfd):
    pc.run([py, path('prog2.py')], {
        'when': [
            ['^Please input.*\n', send_input_bytes],
        ]
    })
    capture = capfd.readouterr()
    assert capture.err == ''
    assert capture.out == 'Please input something:\n' + \
                          'Input was: "somestring"\n'


def test_processcontroller_send_echo(py, pc, capfd):
    pc.run([py, path('prog2.py')], {
        'echo': True,
        'when': [
            ['^Please input.*\n', send_input],
        ]
    })
    capture = capfd.readouterr()
    assert capture.err == ''
    assert capture.out == 'Please input something:\n' + \
                          'somestring\n' + \
                          'Input was: "somestring"\n'


def test_processcontroller_input(py, pc, capfd):
    pc.run([py, path('prog2.py')], {
        'input': 'somestring'
    })
    capture = capfd.readouterr()
    assert capture.err == ''
    assert capture.out == 'Please input something:\n' + \
                          'Input was: "somestring"\n'


def test_processcontroller_input_multi(py, pc, capfd):
    pc.run([py, path('prog3.py')], {
        'input': [
            'somestring',
            'something else'
        ]
    })
    capture = capfd.readouterr()
    assert capture.err == ''
    assert capture.out == 'Input was: "somestring"\n' + \
                          'Input was: "something else"\n'


def test_processcontroller_input_multi_bytes(py, pc, capfd):
    pc.run([py, path('prog3.py')], {
        'input': [
            b'somestring',
            b'something else'
        ]
    })
    capture = capfd.readouterr()
    assert capture.err == ''
    assert capture.out == 'Input was: "somestring"\n' + \
                          'Input was: "something else"\n'


def test_processcontroller_detached(py, pc):
    pc.run([py, '-i'], {'detached': True})
    assert pc.return_value == (0, 0)
    pc.send('exit()')
    time.sleep(0.2)
    assert pc.return_value == (pc.pid, 0)


def test_processcontroller_detached_close(py, pc):
    pc.run([py, '-i'], {'detached': True})
    assert pc.return_value == (0, 0)
    pc.close()
    time.sleep(1)
    assert pc.return_value == (pc.pid, 0)


def test_processcontroller_detached_kill(py, pc):
    pc.run([py, '-i'], {'detached': True})
    assert pc.return_value == (0, 0)
    pc.kill()
    time.sleep(1)
    assert pc.return_value == (pc.pid, 9)


def test_processcontroller_raise_on_send_dead(py, pc):
    pc.run([py, '-i'], {'detached': True})
    pc.kill()
    time.sleep(1)
    with pytest.raises(ChildProcessError):
        pc.send('test')


def test_processcontroller_raise_on_run_dead(py, pc):
    pc.run([py, '-i'], {'detached': True})
    pc.kill()
    time.sleep(1)
    with pytest.raises(ChildProcessError):
        pc.run([py, '-i'], {'detached': True})
