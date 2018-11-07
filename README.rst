ProcessController: a kind of replacement for that old pexpect.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Fast Start
==========

.. role:: bash(code)
   :language: bash

.. role:: py(code)
   :language: python

Install the package::

   :bash:`pip install --user processcontroller`

Import the main class::

   :bash:`from processcontroller import ProcessController`


Create a new instance::

   :py:`process_controller = ProcessController()`


The ProcessController() instance
================================

Methods
-------

* The :py:`run()` method::

   :py:`process_controller.run(command, options)`

   Run a program (command and options detailed below)


* The :py:`send()` method::

   :py:`process_controller.send(str|bytes)`

   Send a string or bytearray to the subprogram stdin, you will usually use it inside a callback or in detached state


* The :py:`close()` method::

   :py:`process_controller.close()`

   Close the stdin of the subprogram so it reaches EOF, you will usually use it inside a callback or in detached state


* The :py:`kill()` method::

   :py:`process_controller.kill()`

   Sends signal SIGKILL to the subprogram, the return_value should be (pid, 9) after that.
   (this should not be so used to be honest)

* The :py:`wait()` method::

  :py:`process_controller.wait()`

  Used to synchronise the caller with the detached instance of ProcessController
  Waits for the queue buffer to be handled and emptied.
  If your process reads stdin such as a :bash:`bash` or things like :bash:`cat`, be sure to call :py:`close()` or you'll end up with an infinite loop here



Attributes
----------

* return_value

  is the return value of the subprogram it will be
  - (0, 0) if running
  - (pid, status) if terminated


Function Parameters
===================

ProcessController.run()
-----------------------

command
_______

The command parameter must be an array like::

   :py:`['/usr/bin/python', 'file.py']`

options
_______

Currently, it supports the following keys, :py:`when`, :py:`input`, :py:`echo`, :py:`detached`, :py:`private` and :py:`readmode`


* when:

This key is used to listen to events occuring on the STDOUT of the subprogram
The value have to be an array of events
The "event" is in fact a match for some pattern::

   :py:`
   'when': [
      ['^SomeRegex.*\n', callback],
      ['^An other one.\n', cb]
      ['^prompt>\$ $', cb]
   ]
   `

Be careful about the ending line, the match will be called each time a char is added to the buffer, this helps matching prompts
maybe I'll add an option to avoid such an expansive operation in the future
Every time a '\n' char is found, the line is treated once and reseted to ''


The callbacks will be called with two arguments: the ProcessController instance, and the matched string::

   :py:`def callback(processcontroller, string)`

You can automates user inputs in your callback when required by the subprogram using the *send* function of your ProcessController instance::

   :py:`
   def cb(p, s):
      c.send('some input')
   `


* input:

This key is used to pre-fill the stdin of a subprogram before running it::

   :py:`
   pc = ProcessController()
   pc.run(['/bin/bash'], {
      'input': 'echo test && exit'
   })
   `

You can set an array of input::

   :py:`'input': ['one', 'two', 'three']  # sends "one\ntwo\nthree\n"`

   You can input str or bytes, conversion is handled for you


* echo:

This key is a boolean that defaults to False.
When set to True, the ProcessController will print the input sent to your subprogram where it has been asked


* detached:

This key is used to make the program run in its own thread, making the call to run non-blocking::

   :py:`
   pc = ProcessController()
   pc.run(['/bin/bash'], {
      'detached': True
   })
   pc.send('echo test')  # will print test to stdout
   pc.close()  # close stdin of subprogram, so that bash will read EOF
   `


* private:

This key is used to prevent the writing of your subprogram STDOUT on your main STDOUT,
One can still print what he wants with the help of a :py:`when` event listener, indeed, the outputed lines will remain in the parameters of the callbacks functions


* readmode:

Use this key to read the sub STDOUT char by char, or line by line (default)
It's value can be :py:`'line'` or :py:`'char'`
Useful to read prompts or anything that does not end with an EOL


Don't forget that you have to create a new instance a ProcessController everytime you want to execute a new subprogram

Please feel free to read the tests and code for a better understanding

ENJOY
