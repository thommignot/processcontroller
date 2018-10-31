import os
import pytest
import shutil

from processcontroller import ProcessController


PROG_PATH = os.path.dirname(__file__)


def path(prog_name):
    return os.path.join(PROG_PATH, prog_name)


def send_input(c, s):
    c.send('somestring')


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


def test_processcontroller_no_opt(py, pc, capsys):
    pc.run([py, path('prog1.py')])
    capture = capsys.readouterr()
    assert capture.out == 'one\ntwo\n'
    assert capture.err == ''


def test_processcontroller_no_input(py, pc, capsys):
    pc.run([py, path('prog1.py')], {
        'when': [
            ['^one.*$', print_in_flow],
        ]
    })
    capture = capsys.readouterr()
    assert capture.out == 'one\nin flow\ntwo\n'
    assert capture.err == ''


def test_processcontroller_action(py, pc):
    increment.counter = 0
    pc.run([py, path('prog1.py')], {
        'when': [
            ['^one.*$', increment],
        ]
    })
    assert increment.counter == 1


def test_processcontroller_action_two(py, pc):
    increment.counter = 0
    pc.run([py, path('prog1.py')], {
        'when': [
            ['^one.*$', increment],
            ['^two.*$', increment],
        ]
    })
    assert increment.counter == 2


def test_processcontroller_input(py, pc, capsys):
    pc.run([py, path('prog2.py')], {
        'when': [
            ['^Please input.*$', send_input],
        ]
    })
    capture = capsys.readouterr()
    assert capture.out == 'Please input something:\n' + \
                          'Input was: "somestring"\n'
    assert capture.err == ''


def test_processcontroller_input_echo(py, pc, capsys):
    pc.run([py, path('prog2.py')], {
        'echo': True,
        'when': [
            ['^Please input.*$', send_input],
        ]
    })
    capture = capsys.readouterr()
    assert capture.out == 'Please input something:\n' + \
                          'somestring\n' + \
                          'Input was: "somestring"\n'
    assert capture.err == ''
