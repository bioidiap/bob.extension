.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Thu 30 Jan 08:46:53 2014 CET

.. image:: https://travis-ci.org/bioidiap/bob.extension.svg?branch=master
   :target: https://travis-ci.org/bioidiap/bob.extension
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.extension/master/index.html
.. image:: https://coveralls.io/repos/bioidiap/bob.extension/badge.png
   :target: https://coveralls.io/r/bioidiap/bob.extension
.. image:: http://img.shields.io/github/tag/bioidiap/bob.extension.png
   :target: https://github.com/bioidiap/bob.extension
.. image:: http://img.shields.io/pypi/v/bob.extension.png
   :target: https://pypi.python.org/pypi/bob.extension
.. image:: http://img.shields.io/pypi/dm/bob.extension.png
   :target: https://pypi.python.org/pypi/bob.extension

===========================================
 Python/C++ Bob Extension Building Support
===========================================

This package provides a simple mechanims for building Python/C++ extensions for
`Bob <http://www.idiap.ch/software/bob/>`_. You use this package by including
it in your ``setup.py`` file.

Building with ``zc.buildout`` is possible using the ``develop`` recipe in
`bob.buildout <http://pypi.python.org/pypi/bob.buildout>`_. Follow the
instructions described on that package for this recipe.

Further documentation on this package can be found `here <https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.extension/master/index.html>`_.

Preparing for C++ Compilation
-----------------------------

Creating C++/Python bindings should be trivial. Firstly, edit your ``setup.py``
so that you include the following::

  from setuptools import dist
  dist.Distribution(dict(setup_requires=['bob.extension']))
  from bob.extension import Extension, Library, build_ext

  ...

  setup(

    name="bob.myext",
    version="1.0.0",
    ...

    setup_requires=[
        'bob.extension',
        ],

    ...
    ext_modules=[
      Extension("bob.myext._myext",
        [
          "bob/myext/ext/file1.cpp",
          "bob/myext/ext/file2.cpp",
          "bob/myext/ext/main.cpp",
        ],
        packages = [ #pkg-config modules to append
          'blitz>=0.10',
        ],
        bob_packages = [ #optionally, bob C++ modules to import
          "bob.core"
        ],
        include_dirs = [ #optionally, include directories
          "bob/myext/ext/headers/",
        ],
      ),
      ... #add more extensions if you wish
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    ...
  )

These modifications will allow you to compile extensions that are linked
against the named ``pkg-config`` modules. Other modules and options can be set
manually using `the standard options for python extensions
<http://docs.python.org/2/extending/building.html>`_.

Adding pure C++ libraries
-------------------------

Most of the bob packages will include pure C++ code that can be used in other packages.
When your package should export a library with pure C++ code as well, you can build it with the ``Library`` extension.
You can simply add this ``Library`` to the list of ``ext_modules`` as follows::

  setup(
    ...
    ext_modules=[
      Library("bob_myext",
        [
          "bob/myext/ext/cpp/cppfile1.cpp",
          "bob/myext/ext/cpp/cppfile2.cpp",
        ],
        package_directory = os.path.dirname(os.path.realpath(__file__)),
        target_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bob', 'myext'),
        version = "1.0.0",
        bob_packages = [...],
        packages = [...],
        ...
      ),
      Extension("bob.my_ext._myext",
        ...
        libraries = ["bob_myext",...]
      )
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    ...
  )

This will compile the given source files of the library using `CMake <http://www.cmake.org>`_.
Please assure that the name of the library ``bob_myext`` is compatible with your package name so that the library can be imported in other packages using the ``bob_packages`` list.

Also, it is assumed that **all** header files that are exported by the C++ library are listed in the *bob/myext/include* directory.
This directory is automatically added to the list of include directories -- in your own package and in all other packages that use the ``bob_packages`` list.

Compiling the module
--------------------

To hook-in the building on the package through ``zc.buildout``, add the following section to your ``buildout.cfg``::

  [bob.myext]
  recipe = bob.buildout:develop
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
  dist.Distribution(dict(setup_requires='bob.extension'))
  from bob.extension.pkgconfig import pkgconfig

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
  dist.Distribution(dict(setup_requires='bob.extension'))
  from bob.extension.boost import boost

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


