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
in the |project|-ecosystem to load *run-time* configuration for applications
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

   >>> print(f"a = {configuration.a}\nb = {configuration.b}")
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
   >>> print(f"a = {configuration.a} \nb = {configuration.b} \nc = {configuration.c}") # doctest: +NORMALIZE_WHITESPACE
   a = 1
   b = 6
   c = 4


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


.. _bob.extension.config.resource:

Resource Loading
================

The function :py:func:`bob.extension.config.load` can also only return
variables from paths. To do this, you need provide a attribute_name. For
example, given the following config file:

.. literalinclude:: ../bob/extension/data/resource_config2.py
   :caption: "resource_config2.py" with two variables inside
   :language: python
   :linenos:

The loaded value can be either 1 or 2:

.. doctest:: load_resource

   >>> group = 'bob.extension.test_config_load'  # the group name of entry points
   >>> attribute_name = 'a'  # the common variable name
   >>> value = load(['bob.extension.data.resource_config2'], entry_point_group=group, attribute_name=attribute_name)
   >>> value == 1
   True
   >>> # attribute_name can be ovverriden using the `path:attribute_name` syntax
   >>> value = load(['bob.extension.data.resource_config2:b'], entry_point_group=group, attribute_name=attribute_name)
   >>> value == 2
   True


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


This command line is implemented using click_. You can extend the commands of
this script through setuptools entry points (this is implemented using
`click-plugins`_). To do so you implement your command-line using click_
independently; then, advertise it as a command under bob script using the
``bob.cli`` entry point.

.. note::

   If you are still not sure how this must be done, maybe you don't know how
   to use click_ and `click-plugins`_ yet.

For a best practice example, please look at how the ``bob config`` command is
implemented:

.. literalinclude:: ../bob/extension/scripts/config.py
   :caption: "bob/extension/scripts/config.py" implementation of the ``bob config`` command.
   :language: python


.. _bob.extension.cli.config:

Command line interfaces with configurations
===========================================

Sometimes your command line interface takes so many parameters and you want to
be able to accept this parameters as both in command-line options and through
configuration files. |project| can help you with that. See below for an
example:

.. literalinclude:: ./annotate.py
   :caption: A command line application that takes several complex parameters.
   :language: python

This will produce the following help message to the users::

  Usage: bob bio annotate [OPTIONS] [CONFIG]...

    Annotates a database.

    The annotations are written in text file (json) format which can be read
    back using :any:`bob.bio.base.utils.annotations.read_annotation_file`
    (annotation_type='json')

    It is possible to pass one or several Python files (or names of
    ``bob.bio.config`` entry points or module names) as CONFIG arguments to
    the command line which contain the parameters listed below as Python
    variables. The options through the command-line (see below) will override
    the values of configuration files. You can run this command with
    ``<COMMAND> -H example_config.py`` to create a template config file.

  Options:
    -d, --database TEXT             The database that you want to annotate. Can
                                    be a ``bob.bio.database`` entry point, a
                                    module name, or a path to a Python file
                                    which contains a variable named `database`.
    -a, --annotator TEXT            A callable that takes the database and a
                                    sample (biofile) of the database and returns
                                    the annotations in a dictionary. Can be a
                                    ``bob.bio.annotator`` entry point, a module
                                    name, or a path to a Python file which
                                    contains a variable named `annotator`.
    -o, --output-dir TEXT           The directory to save the annotations.
    -f, --force                     Whether to overwrite existing annotations.
    --array INTEGER                 Use this option alongside gridtk to submit
                                    this script as an array job.
                                    databases.
    -v, --verbose                   Increase the verbosity level from 0 (only
                                    error messages) to 1 (warnings), 2 (log
                                    messages), 3 (debug information) by adding
                                    the --verbose option as often as desired
                                    (e.g. '-vvv' for debug).
    -H, --dump-config FILENAME      Name of the config file to be generated
    -?, -h, --help                  Show this message and exit.

    Examples:

      $ bob bio annotate -vvv -d <database> -a <annotator> -o /tmp/annotations
      $ jman submit --array 64 -- bob bio annotate ... --array 64


This script takes configuration files (``CONFIG``) and command line options
(e.g. ``--force``) as input and resolves the *Parameters* from the input.
Command line options, if given, override the values of Parameters that may
exist in configuration files. Configuration files are loaded through the
:ref:`bob.extension.config` mechanism so chain loading is supported.

``CONFIG`` can be a path to a file (e.g. ``/path/to/config.py``), a module name
(e.g. ``bob.package.config2``), or setuptools entry points with a specified
group name of the entry points. For example in the annotate script given above,
``CONFIG`` can be the name of ``bob.bio.config`` entry points.

Some command line options (e.g. ``--database`` in the example above) can be
complex Python objects. The way to specify them in the command line is like
``--database atnt`` and this string will be treated as a setuptools entry point
here (``bob.bio.database`` entry points in this example). The mechanism to load
this options is the same as loading ``CONFIG``'s but the entry point name is
different for each option.

By the time, the code enters into the implemented ``annotate`` function, all
variables are resolved and validated and everything is ready to use.

Below you can see several ways that this script can be invoked:

.. code-block:: sh

    # below, atnt is a bob.bio.database entry point
    # below, face is a bob.bio.annotator entry point
    $ bob annotate -d atnt -a face -o /tmp --force -vvv
    # below, bob.db.atnt.config is a module name that resolves to a path to a config file
    $ bob annotate -d bob.db.atnt.config -a face -o /tmp --force -vvv
    # below, all parameters are inside a Python file and the path to that file is provided.
    # If the configuration file has for example database defined as ``database = 'atnt'``
    # the atnt name will be treated as a bob.bio.database entry point and will be loaded.
    $ bob annotate /path/to/config_with_all_parameters.py
    # below, the path of the config file is given as a module name
    $ bob annotate bob.package.config_with_all_parameters
    # below, the output will be /tmp even if there is an ``output`` variable inside the config file.
    $ bob annotate bob.package.config_with_all_parameters -o /tmp
    # below, each resource option can be loaded through config loading mechanism too.
    $ bob annotate -d /path/to/config/database.py -a bob.package.annotate.config --output /tmp
    # Using the command below users can generate a template config file
    $ bob annotate -H example_config.py

As you can see the command line interface can accept its inputs through several
different mechanism. Normally to keep things simple, you would encourage users
to just provide one or several configuration files as entry point names or as
module names and maybe have them provide simple options like ``--verbose`` or
``--force`` through the command line options.


.. include:: links.rst
