ProcessController: a kind of replacement for that old pexpect.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Fast Start
==========

Install the package::

   pip install --user processcontroller

Import the main class::

   from processcontroller import ProcessController


Create a new instance::

   process_controller = ProcessController()


The ProcessController() instance
================================

Methods
-------

* The run() method::

   process_controller.run(command, options)

   Run a program (command and options detailed below)


* The send() method::

   process_controller.send(str|bytes)

   Send a string or bytearray to the subprogram stdin, you will usually use it inside a callback or in detached state


* The close() method::

   process_controller.close()

   Close the stdin of the subprogram so it reaches EOF, you will usually use it inside a callback or in detached state


* The kill() method::

   process_controller.kill()

   Sends signal SIGKILL to the subprogram, the return_value should be (pid, 9) after that.
   (this should not be so used to be honest)


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

   ['/usr/bin/python', 'file.py']

options
_______

   Currently, it supports the following keys, 'when', 'input', 'echo' and 'detached'


* when:

   This key is used to listen to events occuring on the STDOUT of the subprogram
   The value have to be an array of events
   The "event" is in fact a match for some pattern::

      'when': [
         ['^SomeRegex.*\n', callback],
         ['^An other one.\n', cb]
         ['^prompt>\$ $', cb]
      ]

   Be careful about the ending line, the match will be called each time a char is added to the buffer, this helps matching prompts
   maybe I'll add an option to avoid such an expansive operation in the future
   Every time a '\n' char is found, the line is treated once and reseted to ''


   The callbacks will be called with two arguments: the ProcessController instance, and the matched string::

      def callback(processcontroller, string)

   You can automates user inputs in your callback when required by the subprogram using the *send* function of your ProcessController instance::

      def cb(p, s):
         c.send('some input')


* input:'

   This key is used to pre-fill the stdin of a subprogram before running it::

      pc = ProcessController()
      pc.run(['/bin/bash'], {
         'input': 'echo test && exit'
      })

   You can set an array of input::

      'input': ['one', 'two', 'three']  # sends "one\ntwo\nthree\n"

      You can input str or bytes, conversion is handled for you

* echo:

   This key is a boolean that defaults to False.
   When set to True, the ProcessController will print the input sent to your subprogram where it has been asked


* detached:

   This key is used to make the program run in its own thread, making the call to run non-blocking::

      pc = ProcessController()
      pc.run(['/bin/bash'], {
         'detached': True
      })
      pc.send('echo test')  # will print test to stdout
      pc.close()  # close stdin of subprogram, so that bash will read EOF


Don't forget that you have to create a new instance a ProcessController everytime you want to execute a new subprogram

Please feel free to read the tests and code for a better understanding

ENJOY
