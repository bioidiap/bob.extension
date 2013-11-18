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
