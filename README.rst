.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Thu 30 Jan 08:46:53 2014 CET

.. image:: https://travis-ci.org/bioidiap/xbob.extension.svg?branch=prototype
   :target: https://travis-ci.org/bioidiap/xbob.extension

.. image:: http://img.shields.io/github/tag/bioidiap/xbob.extension.svg
   :target: https://github.com/bioidiap/xbob.extension

.. image:: http://img.shields.io/pypi/v/xbob.extension.svg
   :target: https://pypi.python.org/pypi/xbob.extension

.. image:: http://img.shields.io/pypi/dm/xbob.extension.svg
   :target: https://pypi.python.org/pypi/xbob.extension

===========================================
 Python/C++ Bob Extension Building Support
===========================================

This package provides a simple mechanims for building Python/C++ extensions for
`Bob <http://www.idiap.ch/software/bob/>`_. You use this package by including
it in your ``setup.py`` file.

Building with ``zc.buildout`` is possible using the ``develop`` recipe in
`xbob.buildout <http://pypi.python.org/pypi/xbob.buildout>`_. Follow the
instructions described on that package for this recipe.

Preparing for C++ Compilation
-----------------------------

Creating C++/Python bindings should be trivial. Firstly, edit your ``setup.py``
so that you include the following::

  from setuptools import dist
  dist.Distribution(dict(setup_requires=['xbob.extension']))
  from xbob.extension import Extension

  ...

  setup(

    name="xbob.myext",
    version="1.0.0",
    ...

    setup_requires=[
        'xbob.extension',
        ],

    ...
    ext_modules=[
      Extension("xbob.myext._myext",
        [
          "xbob/myext/ext/file1.cpp",
          "xbob/myext/ext/file2.cpp",
          "xbob/myext/ext/main.cpp",
        ],
        packages = [ #pkg-config modules to append
          'blitz>=0.10',
          'bob-core',
          ],
        include_dirs = [ #optionally, include directories
          "xbob/myext/ext/headers/",
          ],
        ),
      ... #add more extensions if you wish
    ],

    ...
    )

These modifications will allow you to compile extensions that are linked
against the named ``pkg-config`` modules. Other modules and options can be set
manually using `the standard options for python extensions
<http://docs.python.org/2/extending/building.html>`_. To hook-in the building
on the package through ``zc.buildout``, add the following section to your
``buildout.cfg``::

  [xbob.myext]
  recipe = xbob.buildout:develop
  verbose = true ;enables command-line verbosity
  debug = true ;compiles the module in debug mode

If you need to build multiple eggs, you will need **one entry per project** on
your ``buildout.cfg``. This includes, possibly, dependent projects. Currently,
``zc.buildout`` ignores the ``setup_requires`` entry on your ``setup.py`` file.
The recipe above creates a new interpreter that hooks that package in and
builds the project considering variables like ``prefixes`` into consideration.

Python API to pkg-config and Boost
----------------------------------

This package alson contains a set of Pythonic bindings to the popular
pkg-config configuration utility. It allows distutils-based setup files to
query for libraries installed on the current system through that command line
utility.  library.

Using the ``pkgconfig`` class
=============================

To use this package at your ``setup.py`` file, you will need to let distutils
know it needs it before importing it. You can achieve this with the following
trick::

  from setuptools import dist
  dist.Distribution(dict(setup_requires='xbob.extension'))
  from xbob.extension.pkgconfig import pkgconfig

.. note::

   In this case, distutils should automatically download and install this
   package on the environment it is required to setup other package.

After inclusion, you can just instantiate an object of type ``pkgconfig``::

  >>> zlib = pkgconfig('zlib')
  >>> zlib.version # doctest: SKIP
  1.2.8
  >>> zlib.include_directories() # doctest: SKIP
  ['/usr/include']
  >>> zlib.library_dirs # doctest: SKIP
  ['/usr/lib']
  >>> zlib > '1.2.6'
  True
  >>> zlib > '1.2.10'
  False

Using the ``boost`` class
=========================

To use this package at your ``setup.py`` file, you will also need the same
trick as with ``pkgconfig``::

  from setuptools import dist
  dist.Distribution(dict(setup_requires='xbob.extension'))
  from xbob.extension.boost import boost

After inclusion, you can just instantiate an object of type ``boost``::

  >>> boost_pkg = boost('>= 1.47')
  >>> boost.version # doctest: SKIP
  1.50.0
  >>> boost.include_directory # doctest: SKIP
  '/usr/include'
  >>> libpaths, libnames = boost.libconfig(['system', 'python'])
  >>> print(libpaths) # doctest: SKIP
  ['/usr/lib']
  >>> print(libnames) # doctest: SKIP
  ['boost_system-mt', 'boost_python-mt-py27']
