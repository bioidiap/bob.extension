.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Thu 30 Jan 08:46:53 2014 CET

.. image:: https://travis-ci.org/bioidiap/xbob.extension.svg?branch=prototype
   :target: https://travis-ci.org/bioidiap/xbob.extension
.. image:: https://coveralls.io/repos/bioidiap/xbob.extension/badge.png?branch=prototype
   :target: https://coveralls.io/r/bioidiap/xbob.extension?branch=prototype
.. image:: http://img.shields.io/github/tag/bioidiap/xbob.extension.png
   :target: https://github.com/bioidiap/xbob.extension
.. image:: http://img.shields.io/pypi/v/xbob.extension.png
   :target: https://pypi.python.org/pypi/xbob.extension
.. image:: http://img.shields.io/pypi/dm/xbob.extension.png
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


Documenting your Python extension
---------------------------------
One part of this package are some functions that makes it easy to generate a proper python documentation for your bound C++ functions.
This documentation can be used after::

  #include <xbob.extension/documentation.h>


Function documentation
======================
To generate a properly aligned function documentation, you can use::

  static xbob::extension::FunctionDoc description(
    "function_name",
    "Short function description",
    "Optional long function description"
  );

.. note::
  Please assure that you define this variable as ``static``.

Using this object, you can add several parts of the function that need documentation:

1. ``description.add_prototype("variable1, variable2", "return1, return2");`` can be used to add function definitions (i.e., ways how to use your function).
   This function needs to be called at least once.
   If the function does not define a return value, it can be left out (in which case the default ``"None"`` is used).

2. ``description.add_parameter("variable1, variable2", "datatype", "Variable description");`` should be defined for each variable that you have used in the prototypes.

3. ``description.add_return("return1", "datatype", "Return value description");`` should be defined for each return value that you have used in the prototypes.

Finally, when binding you function, you can use:

a) ``description.name()`` to get the name of the function

b) ``description.doc()`` to get the aligned documentation of the function, properly indented and broken at 80 characters (by default).
   This call will check that all parameters and return values are documented, and add a ``.. todo`` directive if not.

Sphinx directives like ``.. note::``, ``.. warning::`` or ``.. math::`` will be automatically detected and aligned, when they are used as one-line directive, e.g.::

  "(more text)\n\n.. note:: This is a note\n\n(more text)"

Also, enumerations and listings (using the ``*`` character to define a list element) are handled automatically::

  "(more text)\n\n* Point 1\n* Point 2\n\n(more text)"

.. note::
  Please assure that directives are surrounded by double ``\n`` characters (see example above) so that they are put as paragraphs.
  Otherwise, they will not be displayed correctly.

.. note::
  The ``.. todo::`` directive seems not to like being broken at 80 characters.
  If you want to use ``.. todo::``, please call, e.g., ``description.doc(10000)`` to avoid line breaking.

.. note::
  To increase readability, you might want to split your documentation lines, e.g.::

    "(more text)\n"
    "\n"
    "* Point 1\n"
    "* Point 2\n"
    "\n"
    "(more text)"

Leading white-spaces in the documentation string are handled correctly, so you can use several layers of indentation.


Class documentation
===================
To document a bound C++ class, you can use the ``xbob::extension::ClassDoc("class_name", "Short class description", "Optional long class description")`` function to align and wrap your documentation.
Again, during binding you can use the functions ``description.name()`` and ``description.doc()`` as above.

Additionally, the class documentation has a function to add constructor definitions, which takes an ``xbob::extension::FunctionDoc`` object.
The shortest way to get a proper class documentation is::

  static auto my_class_doc =
      xbob::extension::ClassDoc("class_name", "Short description", "Long Description")
        .add_constructor(
          xbob::extension::FunctionDoc("class_name", "Constructor Description")
           .add_prototype("param1", "")
           .add_parameter("param1", "type1", "Description of param1")
        )
  ;

.. note::
  The second parameter ``""`` in ``add_prototype`` prevents the output type (which otherwise defaults to ``"None"``) to be written.

Currently, the ClassDoc allows to highlight member functions or variables at the beginning of the class documentation.
This highlighting is still under development and might not work as expected.

Possible speed issues
=====================

In order to speed up the loading time of the modules, you might want to reduce the amount of documentation that is generated (though I haven't experienced any speed differences).
For this purpose, just compile your bindings using the "-DXBOB_SHORT_DOCSTRINGS" compiler option, e.g. by adding it to the setup.py as follows (see also above)::

  ...
  ext_modules=[
    Extension("xbob.myext._myext",
      [
        ...
      ],
      ...
      define_macros = [('XBOB_SHORT_DOCSTRINGS',1)],
      ),
  ],
  ...

or simply define an environment variable ``XBOB_SHORT_DOCSTRINGS=1`` before invoking buildout.

In any of these cases, only the short descriptions will be returned as the doc string.


