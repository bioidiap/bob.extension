.. _bob.extension.config:

======================
 Configuration System
======================

This package also provides a configuration system that can be used by packages
in the |project|-echosystem. The configuration system is pretty simple and uses
Python itself to load and validate input files, making no *a priori*
requirements on the amount or complexity of data that needs to be configured.

The configuration system is centered around a single function called
:py:func:`bob.extension.config.load`. You call it to load the configuration
objects from one or more configuration files, like this:

.. testsetup:: *

   import os
   import pkg_resources
   path = pkg_resources.resource_filename('bob.extension', 'data')
   import json

.. doctest:: basic-config

   >>> from bob.extension.config import load
   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> configuration = load([os.path.join(path, 'basic-config.py')])


If the function :py:func:`bob.extension.config.load` succeeds, it returns a
python dictionary containing strings as keys and objects (of any kind) which
represent the configuration resource. For example, if the file
``basic-config.py`` contained:

.. literalinclude:: ../bob/extension/data/basic-config.py
   :language: python
   :linenos:
   :caption: "basic-config.py"


Then, the object ``configuration`` would look like this:

.. doctest:: basic-config

   >>> print(json.dumps(configuration, indent=2, sort_keys=True)) # doctest: +NORMALIZE_WHITESPACE
   {
     "a": 1,
     "b": 3,
     "defaults": {}
   }


The configuration file does not have to limit itself to simple Pythonic
operations, you can import modules and more.

.. note::

   Since configuration files are written in Python, you can execute full python
   programs while configuring, import modules, create classes and more.
   **However**, it is recommended that you keep the configuration files simple.
   Avoid defining classes in the configuration files. A recommended
   configuration file normally would only contain
   ``dict, list, tuple, str, int, float, True, False, None`` Python objects.


There is a special function to load global configuration resources, typically
called *run commands* (or "rc" for short files). The function is called
:py:func:`bob.extension.config.loadrc` file and automatically searches for an
RC file named :py:func:`bob.extension.config.RCFILENAME` on the current
directory and, if that does not exist, reads the file with the same name
located on the root of your home directory (or whatever ``${HOME}/.bobrc.py``
points to). The path of the file that will be loaded can be overridden by an
environment variable named :py:attr:`bob.extension.config.ENVNAME`.

Configurable resources in each |project| package should be clearly named so you
can correctly configure them. The next section hints on how to organize such
global resources so they are configured homogeneously across packages in the
|project| echo-system.


Package Defaults
----------------

While the configuration system by itself does not make assumptions about your
configuration strategy, it does provide some support to better organize
package-based defaults which can be used by |project| echo-system packages.
Package-based defaults may be, for example, the directory where raw data files
for a particular ``bob.db`` are installed or the verbosity-level logging
messages should have.

Package defaults are typically organized dictionary called ``defaults``. The
variable ``defaults`` is **guaranteed** to be defined and to contain no
elements at the start of the configuration file loading. Here is an example:

.. literalinclude:: ../bob/extension/data/defaults-config.py
   :caption: "defaults-config.py"
   :language: python
   :linenos:


.. testsetup:: defaults-config

   from bob.extension.config import load


When loaded, this configuration file produces the result:

.. doctest:: defaults-config

   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> configuration = load([os.path.join(path, 'defaults-config.py')])
   >>> print(json.dumps(configuration, indent=2, sort_keys=True)) # doctest: +NORMALIZE_WHITESPACE
   {
     "defaults": {
       "bob.db.atnt": {
         "directory": "/directory/to/root/of/atnt-database",
         "extension": ".ppm"
       }
     }
   }


.. note::

   Variables starting with an underscore (``_``) are automatically removed from
   the list of returned values by :py:func:`bob.extension.config.load`.

   If you want to use temporary values on your configuration file either name
   them starting with an underscore or delete the object before the end of the
   configuration file.


Chain Loading
-------------

It is possible to implement chain configuration loading and overriding by
passing iterables with more than one filename to
:py:func:`bob.extension.config.load`. Suppose we have two configuration files
which must be loaded in sequence:

.. literalinclude:: ../bob/extension/data/defaults-config.py
   :caption: "defaults-config.py" (first to be loaded)
   :language: python
   :linenos:

.. literalinclude:: ../bob/extension/data/load-config.py
   :caption: "load-config.py" (loaded after defaults-config.py)
   :language: python
   :linenos:


Then, one can chain-load them like this:

.. doctest:: defaults-config

   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> file1 = os.path.join(path, 'defaults-config.py')
   >>> file2 = os.path.join(path, 'load-config.py')
   >>> configuration = load([file1, file2])
   >>> print(json.dumps(configuration, indent=2, sort_keys=True)) # doctest: +NORMALIZE_WHITESPACE
   {
     "defaults": {
       "bob.db.atnt": {
         "directory": "/directory/to/root/of/atnt-database",
         "extension": ".hdf5"
       }
     }
   }

The user wanting to override defaults needs to manage the overriding and the
order in which the override happens.
