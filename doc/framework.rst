.. _bob.extension.framework:

==================================
 Extending packages as frameworks
==================================

It is often required to extend the functionality of your package as a
framework. :ref:`bob.bio.base <bob.bio.base>` is a good example; it provides an
API and other packages build upon it. The utilities provided in this page are
helpful in creating framework packages and building complex
toolchians/pipelines.


.. _bob.extension.config:

Python-based Configuration System
---------------------------------

This package also provides a configuration system that can be used by packages
in the |project|-echosystem to load *run-time* configuration for applications
(for package-level static variable configuration use :ref:`bob.extension.rc`).
It can be used to accept complex configurations from users through
command-line.
The run-time configuration system is pretty simple and uses Python itself to
load and validate input files, making no *a priori* requirements on the amount
or complexity of data that needs to be configured.

The configuration system is centered around a single function called
:py:func:`bob.extension.config.load`. You call it to load the configuration
objects from one or more configuration files, like this:

.. testsetup:: *

   import os
   import pkg_resources
   path = pkg_resources.resource_filename('bob.extension', 'data')
   import json
   from bob.extension.config import load

.. doctest::

   >>> from bob.extension.config import load
   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> configuration = load([os.path.join(path, 'basic_config.py')])


If the function :py:func:`bob.extension.config.load` succeeds, it returns a
python dictionary containing strings as keys and objects (of any kind) which
represent the configuration resource. For example, if the file
``basic_config.py`` contained:

.. literalinclude:: ../bob/extension/data/basic_config.py
   :language: python
   :linenos:
   :caption: "basic_config.py"


Then, the object ``configuration`` would look like this:

.. doctest::

   >>> print("a = %d\nb = %d"%(configuration.a, configuration.b))
   a = 1
   b = 3


The configuration file does not have to limit itself to simple Pythonic
operations, you can import modules, define functions and more.



Chain Loading
=============

It is possible to implement chain configuration loading and overriding by
passing iterables with more than one filename to
:py:func:`bob.extension.config.load`. Suppose we have two configuration files
which must be loaded in sequence:

.. literalinclude:: ../bob/extension/data/basic_config.py
   :caption: "basic_config.py" (first to be loaded)
   :language: python
   :linenos:

.. literalinclude:: ../bob/extension/data/load_config.py
   :caption: "load_config.py" (loaded after basic_config.py)
   :language: python
   :linenos:


Then, one can chain-load them like this:

.. doctest::

   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> file1 = os.path.join(path, 'basic_config.py')
   >>> file2 = os.path.join(path, 'load_config.py')
   >>> configuration = load([file1, file2])
   >>> print("a = %d \nb = %d"%(configuration.a, configuration.b)) # doctest: +NORMALIZE_WHITESPACE
   a = 1
   b = 6


The user wanting to override the values needs to manage the overriding and the
order in which the override happens.


Entry Points
============

The function :py:func:`bob.extension.config.load` can also load config files
through `Setuptools`_ entry points and module names. It is only needed
to provide the group name of the entry points:

.. doctest:: entry_point

   >>> group = 'bob.extension.test_config_load'  # the group name of entry points
   >>> file1 = 'basic_config'  # an entry point name
   >>> file2 = 'bob.extension.data.load_config' # module name
   >>> configuration = load([file1, file2], entry_point_group=group)
   >>> print("a = %d \nb = %d"%(configuration.a, configuration.b)) # doctest: +NORMALIZE_WHITESPACE
   a = 1
   b = 6


.. _bob.extension.processors:

Stacked Processing
------------------

:any:`bob.extension.processors.SequentialProcessor` and
:any:`bob.extension.processors.ParallelProcessor` are provided to help you
build complex processing mechanisms. You can use these processors to apply a
chain of processes on your data. For example,
:any:`bob.extension.processors.SequentialProcessor` accepts a list of callables
and applies them on the data one by one sequentially. :


.. doctest::

   >>> import numpy as np
   >>> from functools import  partial
   >>> from bob.extension.processors import SequentialProcessor
   >>> raw_data = np.array([[1, 2, 3], [1, 2, 3]])
   >>> seq_processor = SequentialProcessor(
   ...     [np.cast['float64'], lambda x: x / 2, partial(np.mean, axis=1)])
   >>> seq_processor(raw_data)
   array([ 1.,  1.])
   >>> np.all(seq_processor(raw_data) ==
   ...        np.mean(np.cast['float64'](raw_data) / 2, axis=1))
   True

:any:`bob.extension.processors.ParallelProcessor` accepts a list of callables
and applies each them on the data independently and returns all the results.
For example:

.. doctest::

   >>> import numpy as np
   >>> from functools import  partial
   >>> from bob.extension.processors import ParallelProcessor
   >>> raw_data = np.array([[1, 2, 3], [1, 2, 3]])
   >>> parallel_processor = ParallelProcessor(
   ...     [np.cast['float64'], lambda x: x / 2.0])
   >>> list(parallel_processor(raw_data))
   [array([[ 1.,  2.,  3.],
          [ 1.,  2.,  3.]]), array([[ 0.5,  1. ,  1.5],
          [ 0.5,  1. ,  1.5]])]

The data may be further processed using a
:any:`bob.extension.processors.SequentialProcessor`:

.. doctest::

   >>> from bob.extension.processors import SequentialProcessor
   >>> total_processor = SequentialProcessor(
   ...     [parallel_processor, list, partial(np.concatenate, axis=1)])
   >>> total_processor(raw_data)
   array([[ 1. ,  2. ,  3. ,  0.5,  1. ,  1.5],
          [ 1. ,  2. ,  3. ,  0.5,  1. ,  1.5]])


.. _bob.extension.cli:

Unified Command Line Mechanism
------------------------------

|project| comes with a command line called ``bob`` which provides a set of
commands by default::

    $ bob --help
    Usage: bob [OPTIONS] COMMAND [ARGS]...

      The main command line interface for bob. Look below for available
      commands.

    Options:
      --help  Show this message and exit.

    Commands:
      config  The manager for bob's global configuration.
      ...

.. warning::

   This feature is experimental and most probably will break compatibility.
   If you are not willing to fix your code after changes are made here,
   please do not use this feature.

This command line is implemented using click_. You can extend the commands of
this script through setuptools entry points (this is implemented using
`click-plugins`_). To do so you implement your command-line using click_
independently; then, advertise it as a command under bob script using the
``bob.cli`` entry point.

.. note::

   If you are still not sure how this must be done, maybe you don't know how
   to use click_ yet.

This feature is experimental and may change and break compatibility in future.
For a best practice example, please look at how the ``bob config`` command is
implemented:

.. literalinclude:: ../bob/extension/scripts/config.py
   :caption: "bob/extension/scripts/config.py" implementation of the ``bob
       config`` command.
   :language: python


Command lines with configurations
=================================

Sometimes your command line takes so many parameters and you want to be able to
accept this parameters as both in command-line options and through
configuration files. |project| can help you with that. See below for an
example:

.. literalinclude:: ./annotate.py
   :caption: A command line application that takes several complex parameters.
   :language: python

This will produce the following help message to the users::

   Usage: bob annotate [OPTIONS] [CONFIG]...

     Annotates a database. The annotations are written in text file (json)
     format which can be read back using
     :any:`bob.db.base.read_annotation_file` (annotation_type='json')

     Parameters
     ----------
     database : :any:`bob.bio.database`
         The database that you want to annotate. Can be a ``bob.bio.database``
         entry point or a path to a Python file which contains a variable
         named `database`.
     annotator : callable
         A function that takes the database and a sample (biofile) of the
         database and returns the annotations in a dictionary. Can be a
         ``bob.bio.annotator`` entry point or a path to a Python file which
         contains a variable named `annotator`.
     output_dir : str
         The directory to save the annotations.
     force : bool, optional
         Wether to overwrite existing annotations.
     verbose : int, optional
         Increases verbosity (see help for --verbose).

     [CONFIG]...            Configuration files. It is possible to pass one or
                            several Python files (or names of ``bob.bio.config``
                            entry points) which contain the parameters listed
                            above as Python variables. The options through the
                            command-line (see below) will override the values of
                            configuration files.

   Options:
     -d, --database TEXT
     -a, --annotator TEXT
     -o, --output-dir TEXT
     -f, --force
     -v, --verbose          Increase the verbosity level from 0 (only error
                            messages) to 1 (warnings), 2 (log messages), 3 (debug
                            information) by adding the --verbose option as often
                            as desired (e.g. '-vvv' for debug).
     --help                 Show this message and exit.


You can create a script similar to ``verify.py`` form ``bob.bio.base`` with
minimal boilerplate as you can see.


.. include:: links.rst

