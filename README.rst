ProcessController: a kind of replacement for that old pexpect.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install the package::

   pip install --user processcontroller

Import the main class::

   from processcontroller import ProcessController


Create a new instance::

   process_controller = ProcessController()


Run a subprogram::

   process_controller.run(command, options)



The command parameter must be an array like::

   ['/usr/bin/python', 'file.py']

options is a bit more complexe:

   Currently, it supports two keys, 'when' and 'echo'.


   * when:

   This key is used to listen to events occuring on the STDOUT of the subprogram
   The value have to be an array of events
   The "event" is in fact a match for some pattern::

      'when': [
         ['^SomeRegex.*$', callback],
         ['^An other one.$', cb]
      ]

   The callbacks will be called with two arguments: the ProcessController instance, and the matched string::

      def callback(processcontroller, string)

   You can automates user inputs in your callback when required by the subprogram using the *send* function of your ProcessController instance::

      def cb(p, s):
         c.send('some input')



   * echo:

   This key is a boolean that defaults to False.
   When set to True, the ProcessController will print the input sent to your subprogram where it has been asked



Don't forget that you have to create a new instance a ProcessController everytime you want to execute a new subprogram

Please feel free to read the tests and code for a better understanding

ENJOY
