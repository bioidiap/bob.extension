.. _bob.extension.config:

===================================
 Python-based Configuration System
===================================

This package also provides a configuration system that can be used by packages
in the |project|-echosystem to load *run-time* configuration for applications
(for package-level static variable configuration use :ref:`bob.extension.rc`).
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
-------------

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
------------

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

.. include:: links.rst
