.. _bob.extension.config:

======================
 Configuration System
======================

This package also provides a configuration system that can be used by packages
in the |project|-echosystem. The configuration system is pretty simple and uses
Python itself to load and validate input files, making no *a priori*
requirements on the amount or complexity of data that needs to be configured.
Since configuration files are written in Python, you can execute full python
programs while configuring, import modules, create classes and more.

The configuration system is centered around a single function called
:py:func:`bob.extension.config.load`. You call it to load the configuration
objects from a given configuration file, like this:

.. testsetup:: *

   import os
   import pkg_resources
   path = pkg_resources.resource_filename('bob.extension', 'data')
   import json

.. doctest:: basic-config

   >>> from bob.extension.config import load
   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> configuration = load(os.path.join(path, 'basic-config.py'))


If the function :py:func:`bob.extension.config.load` succeeds, it returns a
python dictionary containing strings as keys and objects (of any kind) which
represent the configuration resource. For example, if the file
``example-config.py`` contained:

.. literalinclude:: ../bob/extension/data/basic-config.py
   :language: python
   :linenos:
   :caption: "basic-config.py"


Then, the object ``configuration`` would look like this:

.. doctest:: basic-config

   >>> print(json.dumps(configuration, indent=2, sort_keys=True))
   {
     "a": 1,
     "b": 3,
     "defaults": {}
   }


The configuration file does not have to limit itself to simple Pythonic
operations, you can import modules and more.


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

   from bob.extension.config import load, update


When loaded, this configuration file produces the result:

.. doctest:: defaults-config

   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> configuration = load(os.path.join(path, 'defaults-config.py'))
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


Value Overrides
---------------

It is possible to implement chain configuration loading and overriding by
either calling :py:func:`bob.extension.config.load` many times or by nesting
calls to ``load()`` within the same configuration file. Here is an example of
the latter:

.. literalinclude:: ../bob/extension/data/load-config.py
   :caption: "load-config.py"
   :language: python
   :linenos:


The function :py:func:`bob.extension.config.update` is also bound to the
configuration readout and appears as an object called ``update`` within the
configuration file. It provides an easier handle to update the ``defaults``
dictionary.

This would produce the following result:

.. doctest:: defaults-config

   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> configuration = load(os.path.join(path, 'load-config.py'))
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

It is possible to implement the same override technique programmatically. For
example, suppose a program that receives various configuration files to read as
input and must override values set, one after the other:

.. code-block:: sh

   # example application call
   $ ./my-application.py config1.py config2.py


The configuration files contain settings like these:

.. literalinclude:: ../bob/extension/data/config1.py
   :caption: "config1.py"
   :language: python
   :linenos:


.. literalinclude:: ../bob/extension/data/config2.py
   :caption: "config2.py"
   :language: python
   :linenos:


Programmatically, the application and implement the update of the configuration
using :py:func:`bob.extension.config.update`:

.. doctest:: defaults-config

   >>> #the variable `path` points to <path-to-bob.extension's root>/data
   >>> configuration = load(os.path.join(path, 'config1.py'))
   >>> _ = update(configuration, load(os.path.join(path, 'config2.py')))
   >>> print(json.dumps(configuration, indent=2, sort_keys=True)) # doctest: +NORMALIZE_WHITESPACE
   {
     "defaults": {
       "bob.core": {
         "verbosity": 30
       },
       "bob.db.atnt": {
         "extension": ".jpg"
       }
     },
     "var1": "howdy",
     "var2": "world",
     "var3": "foo"
   }
