ProcessController: a kind of replacement for that old pexpect.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Fast Start
==========

Install the package:

.. code:: bash

   pip install --user processcontroller


Import the main class:

.. code:: python

   from processcontroller import ProcessController


Create a new instance:

.. code:: python

   process_controller = ProcessController()


The ProcessController() instance
================================

Methods
-------

* The run() method:

   Run a program (command and options detailed below)

.. code:: python

   process_controller.run(command, options)



* The send() method:

   Send a string or bytearray to the subprogram stdin, you will usually use it inside a callback or in detached state

.. code:: python

   process_controller.send(str|bytes)


* The close() method:

   Close the stdin of the subprogram so it reaches EOF, you will usually use it inside a callback or in detached state

.. code:: python

   process_controller.close()



* The kill() method:

   Sends signal SIGKILL to the subprogram, the return_value should be (pid, 9) after that.
   (this should not be so used to be honest)

.. code:: python

   process_controller.kill()



* The wait() method:

   Used to synchronise the caller with the detached instance of ProcessController
   Waits for the queue buffer to be handled and emptied.
   If your process reads stdin such as bash or things like cat, be sure to call close() or you'll end up with an infinite loop here

.. code:: python

   process_controller.wait()


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

The command parameter must be an array like:

.. code:: python

   ['/usr/bin/python', 'file.py']


options
_______

Currently, it supports the following keys, 'when', 'input', 'echo' and 'detached'

* when:

This key is used to listen to events occuring on the STDOUT of the subprogram
The value have to be an array of events
The "event" is in fact a match for some pattern:

.. code:: python

   'when': [
      ['^SomeRegex.*\n', callback],
      ['^An other one.\n', cb]
      ['^prompt>\$ $', cb]
   ]

Be careful about the ending line, the match will be called each time a char is added to the buffer, this helps matching prompts
maybe I'll add an option to avoid such an expansive operation in the future
Every time a '\n' char is found, the line is treated once and reseted to ''


The callbacks will be called with two arguments: the ProcessController instance, and the matched string:

.. code:: python

   def callback(processcontroller, string)

You can automates user inputs in your callback when required by the subprogram using the *send* function of your ProcessController instance:

.. code:: python

   def cb(p, s):
      c.send('some input')


* input:

This key is used to pre-fill the stdin of a subprogram before running it:

.. code:: python

   pc = ProcessController()
   pc.run(['/bin/bash'], {
      'input': 'echo test && exit'
   })

You can set an array of input:

.. code:: python

   'input': ['one', 'two', 'three']  # sends "one\ntwo\nthree\n"

You can input str or bytes, conversion is handled for you

* echo:

This key is a boolean that defaults to False.
When set to True, the ProcessController will print the input sent to your subprogram where it has been asked


* detached:

This key is used to make the program run in its own thread, making the call to run non-blocking:

.. code:: python

   process_controller.wait()

   pc = ProcessController()
   pc.run(['/bin/bash'], {
      'detached': True
   })
   pc.send('echo test')  # will print test to stdout
   pc.close()  # close stdin of subprogram, so that bash will read EOF


* private:

This key is used to prevent the writing of your subprogram STDOUT on your main STDOUT,
One can still print what he wants with the help of a when event listener, indeed, the outputed lines will remain in the parameters of the callbacks functions


* readmode:

Use this key to read the sub STDOUT char by char, or line by line (default)
It's value can be 'line' or 'char'
Useful to read prompts or anything that does not end with an EOL


* decode:

This option is used to tell processcontroller to decode or not what is read from the subprogram, True by default


Don't forget that you have to create a new instance a ProcessController everytime you want to execute a new subprogram

Please feel free to read the tests and code for a better understanding

ENJOY
