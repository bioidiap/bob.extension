.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.dos.anjos@gmail.com>
.. Tue 15 Oct 17:41:52 2013

=========================================================
 |project| Satellite Package Development and Maintenance
=========================================================

This tutorial explains how to build and distribute `Python`-based working environments for |project|.
By following these instructions you will be able to:

* Download and install |project| packages to build a global or local working environment including |project|;
* Install python packages to augment your virtual work environment capabilities -- e.g., to include a new python package for a specific purpose covering functionality that does not necessarily exists in |project| or any available Satellite Package;
* Implement your own satellite package including either pure Python code, a mixture of C/C++ and Python code, and even pure C/C++ libraries with clean C/C++ interfaces that might be used by other researchers;
* Distribute your work to others in a clean and organized manner.

These instructions heavily rely on the use of Python `distutils`_ and `zc.buildout`_.
One important advantage of using `zc.buildout`_ is that it does **not** require administrator privileges for setting up any of the above.
Furthermore, you will be able to create distributable environments for each project you have.
This is a great way to release code for laboratory exercises or for a particular publication that depends on |project|.

.. note::
  The core of our strategy is based on standard tools for *defining* and *deploying* Python packages.
  If you are not familiar with Python's ``setuptools``, ``distutils`` or PyPI, it can be beneficial to `learn about those <http://guide.python-distribute.org/>`_ before you start.
  Python's `Setuptools`_ and `Distutils`_ are mechanisms to *define and distribute* python code in a packaged format, optionally through `PyPI`_, a web-based Python package index and distribution portal.

  `zc.buildout`_ is a tool to *deploy* Python packages locally, automatically  setting up and encapsulating your work environment.


Anatomy of a buildout Python package
------------------------------------

The best way to create your package is to download one of the skeletons that are described in this tutorial and build on it, modifying what you need.
Fire-up a shell window and than do this:

.. code-block:: sh

  $ wget https://github.com/bioidiap/bob.extension/raw/master/examples/bob.example.project.tar.bz2
  $ tar -xjf bob.example.project.tar.bz2
  $ cd bob.example.project

We now recommend you read the file ``README.rst``, which is written in `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ format, situated at the root of the just downloaded material.
It contains important information on other functionality such as document generation and unit testing, which will not be covered on this introductory material.

The anatomy of a minimal package should look like the following:

.. code-block:: sh

  .
  +-- MANIFEST.in       # extras to be installed, besides the python files
  +-- README.rst        # a description of the package, in reStructuredText format
  +-- bootstrap.py      # stock script downloaded from zc.buildout's website
  +-- buildout.cfg      # buildout configuration
  +-- setup.py          # installation + requirements for this particular package
  +-- doc               # documentation directory
  |   +-- conf.py       # Sphinx configuration
  |   +-- index.rst     # Documentation starting point for Sphinx
  +-- bob               # python package (a.k.a. "the code")
  |   +-- example
  |   |   +-- project
  |   |   |   +-- script
  |   |   |   |   +-- __init__.py
  |   |   |   |   +-- version.py
  |   |   |   +-- __init__.py
  |   |   |   +-- test.py
  |   |   +-- __init__.py
  |   +-- __init__.py

Our example that you just downloaded contains these files and a few extra ones useful for this tutorial.
Inspect the package so you are aware of its contents.
All files are in text format and should be heavily commented.
The most important file that requires your attention is ``setup.py``.
This file contains the basic information for the Python package you will be creating.
It defines scripts the package provides and dependencies it requires for execution.
To customize the package to your needs, you will need to edit this file and modify it accordingly.
Before doing so, it is suggested you go through all of this tutorial so you are familiar with the whole environment.
The example package, as it is distributed, contains a fully working example.

In the remainder of this document, we explain how to setup ``buildout.cfg`` so you can work in different operational modes - the ones which are more common development scenarios.


Pure-Python Packages
--------------------

Pure-Python packages are the most common.
They contain code that is exclusively written in Python.
This contrasts to packages that are written in a mixture of Python and C/C++, which are explained in more detail below.

The package you cloned above is a pure-Python example package and contains all elements to get you started.
It defines a single library module called ``bob.example.project``, which declares a simple script, called ``version.py`` that prints out the version of the dependent library ``bob.blitz``.
When you clone the package, you will not find any executable as ``buildout`` needs to check all dependencies and install missing ones before you can execute anything.
Particularly, it inspects the ``setup.py`` file in the root directory of the package, which contains all required information to build the package, all of which is contained in the ``setup`` function:

.. code-block:: python

  setup(
    name = 'bob.example.project',
    version = '0.0.1a0',
    ...
    packages = find_packages(),
    ...
    install_requires = [
      'setuptools',
      'bob.blitz'
    ],
    ...
    namespace_packages = [
      'bob',
      'bob.example',
    ],
    ...
    entry_points = {
      'console_scripts' : [
        'version.py = bob.example.project.script.version:main',
      ],
    },
  )

In detail, it defines the name and the version of this package, which files belong to the package (those files are automatically collected by the ``find_packages`` function), other packages that we depend on, namespaces (see below) and console scripts.
The full set of options can be inspected in the `Setuptools documentation <http://pythonhosted.org/setuptools/setuptools.html>`_.

To be able to use the package, we first need to build it.
Here is how to go from nothing to everything:

.. code-block:: sh

  $ python bootstrap.py
  Creating directory '/home/user/bob.example.project/bin'.
  Creating directory '/home/user/bob.example.project/parts'.
  Creating directory '/home/user/bob.example.project/eggs'.
  Creating directory '/home/user/bob.example.project/develop-eggs'.
  Generated script '/home/user/bob.example.project/bin/buildout'.
  $ ./bin/buildout
  Getting distribution for 'bob.buildout'.
  Got bob.buildout 2.0.0.
  Getting distribution for 'zc.recipe.egg>=2.0.0a3'.
  Got zc.recipe.egg 2.0.1.
  Develop: '/home/user/bob.example.project/.'
  ...
    Installing scripts.
  Getting distribution for 'bob.extension'.
  Processing bob.blitz-2.0.0.zip
  ...
  Got bob.blitz 2.0.0.
  ...

.. note::
  The Python shell used in the first line of the previous command set determines the Python interpreter that will be used for all scripts developed inside this package.
  To build your environment around a different version of Python, just make sure to correctly choose the interpreter you wish to use.
  If you just want to get things rolling, using ``python bootstrap.py`` will, in most cases, do the right thing.

.. note::
   When you have installed an older version of |project| -- i.e. |project| v1.x, you might need to uninstall it first, see https://github.com/idiap/bob/wiki/Installation.

You should now be able to execute ``./bin/version.py``:

.. code-block:: sh

  $ ./bin/version.py
  bob.blitz: 2.0.0a0 [api=0x0200] (/home/user/bob.example.project/eggs/bob.blitz-2.0.0a0-py2.7-linux-x86_64.egg)
    - c/c++ dependencies:
      - Blitz++: 0.10
      - Boost: 1.55.0
      - Compiler: {'version': '4.7.2', 'name': 'gcc'}
      - NumPy: {'abi': '0x01000009', 'api': '0x00000009'}
      - Python: 2.7.8
    - python dependencies:
      - bob.extension: 0.3.0a0 (/home/user/bob.example.project/eggs/bob.extension-0.3.0a0-py2.7.egg)
      - numpy: 1.8.1 (/usr/lib/python2.7/site-packages)
      - setuptools: 5.4.1 (/home/user/bob.example.project/eggs/setuptools-5.4.1-py2.7.egg)

Everything is now setup for you to continue the development of this package.
Modify all required files to setup your own package name, description and dependencies.
Start adding files to your library (or libraries) and, if you wish, make this package available in a place with public access to make your research public.
We recommend using GitHub.
Optionally, `drop-us a message <https://groups.google.com/d/forum/bob-devel>`_ talking about the availability of this package so we can add it to the growing list of `Satellite Packages`_.


Python Package Namespace
========================

We like to make use of namespaces to define combined sets of functionality that go well together.
Python package namespaces are `explained in details here <http://peak.telecommunity.com/DevCenter/setuptools#namespace-package>`_ together with implementation details.
For bob packages, we usually use the ``bob`` namespace, using several sub-namespaces such as ``bob.io``, ``bob.ip``, ``bob.learn``, ``bob.db`` or (like here) ``bob.example``.

In particular, if you are creating a database access API, please consider putting all of your package contents *inside* the namespace ``bob.db.<package>``, therefore declaring two namespaces: ``bob`` and ``bob.db``.
All standard database access APIs follow this strategy.
Just look at our currently existing database `satellite packages`_ for examples.


Creating Database Satellite Packages
====================================

Database satellite packages are special satellite packages that can hook-in |project|'s database manager ``bob_dbmanage.py``.
Except for this detail, they should look exactly like a normal package.

To allow the database to be hooked to the ``bob_dbmanage.py`` you must implement a non-virtual python class that inherits from :py:class:`bob.db.driver.Interface`.
Your concrete implementation should then be described at the ``setup.py`` file with a special ``bob.db`` entry point:

.. code-block:: python

    # bob database declaration
    'bob.db': [
      'example = bob.db.example.driver:Interface',
    ],

At present, there is no formal design guide for databases.
Nevertheless, it is considered a good practice to follow the design of currently existing database `satellite packages`_.
This should ease migration in case of future changes.


C or C++/Python Packages
------------------------

Creating C++/Python bindings should be rather straightforward.
Only few adaptations need to be performed to get the C/C++ code being compiled and added as an extension.
For simplicity, we created an example package that includes a simple example of a C++ extension.
You can check it out by:

.. code-block:: sh

  $ wget https://github.com/bioidiap/bob.extension/raw/master/examples/bob.example.extension.tar.bz2
  $ tar -xjf bob.example.extension.tar.bz2
  $ cd bob.example.extension

One difference is that now an additional file ``requirements.txt`` can be found in the root directory of the package.
In this file, all packages that are **directly** required to compile the C/C++ code in your package.
**Indirectly** required packages will be downloaded and installed automatically.
For our example, this is only the ``bob.blitz`` package.

The second big difference comes in the ``setup.py``.
To be able to import ``bob.extension`` and ``bob.blitz`` in the setup.py, we need to include some code:

.. code-block:: python

  setup_packages = ['bob.extension', 'bob.blitz']
  bob_packages = []

  from setuptools import setup, find_packages, dist
  dist.Distribution(dict(setup_requires = setup_packages + bob_packages))

We keep the ``setup_packages`` and ``bob_packages`` in separate variables since we will need them later.
The ``bob_packages`` contain a list of bob packages that this extension **directly** depends on.
In our example, we only depend on ``bob.blitz``, and we can leave the list empty.

As the second step, we need to add some lines in the header of the file to tell the ``setuptools`` system to compile our library with our ``Extension`` class:

.. code-block:: python

  # import the Extension class and the build_ext function from bob.blitz
  from bob.blitz.extension import Extension, build_ext

  # load the requirements.txt for additional requirements
  from bob.extension.utils import load_requirements
  build_requires = setup_packages + bob_packages + load_requirements()

In fact, we don't use the extension from :py:class:`bob.extension.Extension`, but the one from ``bob.blitz.extension``, which is a derivation of this package.
The difference is that in :py:class:`bob.blitz.extension.Extension` all header files and libraries for the ``Blitz++`` library are added.

Third, we have to add an extension using the ``Extension`` class, by listing all C/C++ files that should be compiled into the extension:

.. code-block:: python

  setup(
    ...
    setup_requires = build_requires,
    install_requires = build_requires,
    ...
    ext_modules = [
      Extension("bob.myext._myext",
        [
          "bob/myext/ext/file1.cpp",
          "bob/myext/ext/file2.cpp",
          "bob/myext/ext/main.cpp",
        ],
        version = "1.0.0",
        bob_packages = bob_packages
      ),
      ... #add more extensions if you wish
    ],
    ...
  )

These modifications will allow you to compile extensions that are linked against our core Python-C++ bridge ``bob.blitz`` (be default).
You can specify any other ``pkg-config`` module and that will be linked in (for example, ``boost`` or ``opencv``) using the ``packages`` parameter.
For ``boost`` packages, you might need to define, which boost modules are required.
By default, when using boost you should at least add the ``system`` module, i.e., by:

.. code-block:: python

  setup(
    ...
    ext_modules = [
      Extension(
        ...
        packages = ['boost'],
        boost_modules = ['system'],
      ),
      ...
    ],
    ...
  )

Other modules and options can be set manually using `the standard options for python extensions <http://docs.python.org/2/extending/building.html>`_.

Most of the bob packages come with pure C++ code and python bindings.
When your library compiles and links against the pure C++ code, you can simply use the ``bob_packages`` as above.
This will automatically add the desired include and library directories, as well as the libraries and the required preprocessor options.

.. note::
   Usually we provide one extension ``version`` that deals with versioning.
   One example of such a ``version`` extension can be found in our example.

In our example, we have defined a small C++ function, which also shows the basic bridge between ``numpy.ndarray`` and our C++ pendant ``Blitz++``.
Basically, there are two C++ files for our extension.
``bob/example/extension/Function.cpp`` contains the pure C++ implementation of the function.
In ``bob/example/extension/main.cpp``, we define the Python bindings to that function, including the creation of a complete Python module called ``_library``.
Additionally, we give a short example of how to use our documentation classes provided in this module (see below for more details).
Finally, the function ``reverse`` from the module ``_library`` is imported into our module in the ``bob/example/extension/__init__.py`` file.

To compile your C++ Python bindings and the pure C++ libraries, you can follow the same instructions as shown above:

.. code-block:: sh

  $ python bootstrap.py
  ...
  $ ./bin/buildout
  ...

.. note::

   By default, we compile the source code (of this and all dependent packages) in debug mode.
   If you want to change that, switch the according flag in the ``buildout.cfg`` to ``debug = False``, and the compilation will be done with optimization flags enabled.

Now, we can use the script ``./bin/reverse.py`` (that we have registered in the ``setup.py``) to reverse a list of floats, using the C++ implementation of the ``reverse`` function:

.. code-block:: sh

  $ ./bin/reverse.py 1 2 3 4 5
  [1.0, 2.0, 3.0, 4.0, 5.0] reversed is [ 5.  4.  3.  2.  1.]

We can also see that the function documentation has made it into the module, too:

.. code-block:: sh

  $ ./bin/python
  >>> import bob.example.extension
  >>> help(bob.example.extension)

and that we can list version and the dependencies of our package:

.. code-block:: sh

  >>> print (bob.example.extension.version)
  0.0.1a0
  >>> print (bob.example.extension.get_config())
  ...


Pure C/C++ Libraries Inside your Package
========================================

If you want to provide a library with pure C++ code in your package as well, you can use the :py:class:`bob.extension.Library` class.
It will automatically compile your C/C++ code using `CMake <http://www.cmake.org>`_ into a shared library that you can import in your own C/C++-Python bindings, as well as in other packages.
Again, a complete example can be downloaded via:

.. code-block:: sh

  $ wget https://github.com/bioidiap/bob.extension/raw/master/examples/bob.example.library.tar.bz2
  $ tar -xjf bob.example.library.tar.bz2
  $ cd bob.example.library

To generate a Library, simply add it in the list of ``ext_modules``:

.. code-block:: python

  ...
  # import the Extension and Library classes and the build_ext function from bob.blitz
  from bob.blitz.extension import Extension, Library, build_ext
  ...

  setup(

    ext_modules = [
      # declare a pure C/C++ library just the same way as an extension
      Library("bob.myext.bob_myext",
        [
          "bob/myext/cpp/pure_cpp_file1.cpp",
          "bob/myext/cpp/pure_cpp_file2.cpp",
        ],
        version = "1.0.0",
        bob_packages = bob_packages,
      ),
      ... #add more Extensions if you wish
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    ...
  )

Again, we use the overloaded library class :py:class:`bob.blitz.extension.Library` instead of the :py:class:`bob.extension.Library`, but the parameters are identical, and identical to the ones of the :py:class:`bob.extension.Extension`.
To avoid later complications, you should follow the guidelines for libraries in bob packages:

1. The name of the C++ library need to be identical to the name of your package (replacing the '.' by '_').
   Also, the package name need to be part of it.
   For example, to create a library for the ``bob.myext`` package, it should be called ``bob.myext.bob_myext``.
   In this way it is assured that the libraries are found by the ``bob_packages`` parameter (see above).

2. All header files that your C++ library should export need to be placed in the directory ``bob/myext/include/bob.myext``.
   Again, this is the default directory, where the ``bob_packages`` expect the includes to be.
   This is also the directory that is added to your own library and to your extensions, so you don't need to specify that by hand.

3. The include directory should contain a ``config.h`` file, which contains C/C++ preprocessor directives that contains the current version of your C/C++ API.
   With this, we make sure that the version of the library that is linked into other packages is the expected one.
   One such file is again given in our ``bob.example.library`` example.

4. To avoid conflicts with other functions, you should put all your exported C++ functions into an appropriate namespace.
   In our example, this should be something like ``bob::example::library``.

The newly generated Library will be automatically linked to **all other** Extensions in the package.
No worries, if the library is not used in the extension, the linker should be able to figure that out...

.. note:
  The clang linker seems not to be smart enough to detect unused libraries...

You can also export your Python bindings to be used in other libraries.
Unfortunately, this is an extremely tedious process and is not explained in detail here.
As an example, you might want (or maybe not) to have a look into ``bob.blitz/bob/blitz/include/bob.blitz/capi.h``.


Using boost modules
===================

If your C++ code relies on boost packages, you might need to tell, which boost libraries you are using.
To enable one or several boost packages, the ``Extension`` and ``Library`` classes have a special set of
To use boost modules package at your ``setup.py`` file, you will also need the same trick as with ``pkgconfig``::

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


Compiling your Library and Extension
====================================

As shown above, to compile your C++ Python bindings and the pure C++ libraries, you can follow the simple instructions:

.. code-block:: sh

  $ python bootstrap.py
  ...
  $ ./bin/buildout
  ...

This will automatically check out all required ``bob_packages`` and compile them locally.
Afterwards, the C++ code from this package will be compiled, using a newly created ``build`` directory for temporary output.
After compilation, this directory can be safely removed (re-compiling will re-create it).

To get the source code compiled using another build directory, you can define a ``BOB_BUILD_DIRECTORY`` environment variable, e.g.:

.. code-block:: sh

  $ python bootstrap.py
  ...
  $ BOB_BUILD_DIRECTORY=/tmp/build_bob ./bin/buildout
  ...

The C++ code of this package, **and the code of all other** ``bob_packages`` will be compiled using the selected directory.
Again, after compilation this directory can be safely removed.

Another environment variable enables parallel compilation of C or C++ code.
Use ``BOB_BUILD_PARALLEL=X`` (where x is the number of parallel processes you want) to enable parallel building.


Documenting your C/C++ Python Extension
=======================================

One part of this package are some functions that makes it easy to generate a proper python documentation for your bound C/C++ functions.
This documentation can be used after:

.. code-block:: c++

   #include <bob.extension/documentation.h>

**Function documentation**
++++++++++++++++++++++++++

To generate a properly aligned function documentation, you can use:

.. code-block:: c++

   static bob::extension::FunctionDoc description(
     "function_name",
     "Short function description",
     "Optional long function description"
   );


.. note::

   If you want to document a member function of a class, you should use set fourth boolean option to true.
   This is required since the default python class member documentation is indented four more spaces, which we need to balance:

   .. code-block:: c++

      static bob::extension::FunctionDoc member_function_description(
        "function_name",
        "Short function description",
        "Optional long function description",
        true
      );

Using this object, you can add several parts of the function that need documentation:

1. ``description.add_prototype("variable1, variable2", "return1, return2");`` can be used to add function definitions (i.e., ways how to use yourfunction).
   This function needs to be called at least once.
   If the function does not define a return value, it can be left out (in which case the default ``"None"`` is used).

2. ``description.add_parameter("variable1, variable2", "datatype", "Variable description");`` should be defined for each variable that you have used in the prototypes.

3. ``description.add_return("return1", "datatype", "Return value description");`` should be defined for each return value that you have used in the prototypes.

.. note::

   All these functions return a reference to the object, so that you can use them in line, e.g.:

   .. code-block:: c++

      static auto description = bob::extension::FunctionDoc(...)
        .add_prototype(...)
        .add_parameter(...)
        .add_return(...)
      ;

Finally, when binding you function, you can use:

a. ``description.name()`` to get the name of the function

b. ``description.doc()`` to get the aligned documentation of the function, properly indented and broken at 80 characters (by default).
   This call will check that all parameters and return values are documented, and add a ``.. todo::`` directive if not.

Sphinx directives like ``.. note::``, ``.. warning::`` or ``.. math::`` will be automatically detected and aligned, when they are used as one-line directive, e.g.:

.. code-block:: c++

   "(more text)\n\n.. note:: This is a note\n\n(more text)"

Also, enumerations and listings (using the ``*`` character to define a list element) are handled automatically:

.. code-block:: c++

   "(more text)\n\n* Point 1\n* Point 2\n\n(more text)"

.. note::

   Please assure that directives are surrounded by double ``\n`` characters (see example above) so that they are put as paragraphs.
   Otherwise, they will not be displayed correctly.

.. note::

   The ``.. todo::`` directive seems not to like being broken at 80 characters.
   If you want to use ``.. todo::``, please call, e.g., ``description.doc(10000)`` to avoid line breaking.

.. note::

   To increase readability, you might want to split your documentation lines, e.g.:

   .. code-block:: c++

      "(more text)\n"
      "\n"
      "* Point 1\n"
      "* Point 2\n"
      "\n"
      "(more text)"

Leading white-spaces in the documentation string are handled correctly, so you can use several layers of indentation.

**Class documentation**
+++++++++++++++++++++++

To document a bound class, you can use the ``bob::extension::ClassDoc("class_name", "Short class description", "Optional long class description")`` function to align and wrap your documentation.
Again, during binding you can use the functions ``description.name()`` and ``description.doc()`` as above.

Additionally, the class documentation has a function to add constructor definitions, which takes an ``bob::extension::FunctionDoc`` object.
The shortest way to get a proper class documentation is:

.. code-block:: c++

   auto my_class_doc =
     bob::extension::ClassDoc("class_name", "Short description", "Long Description")
       .add_constructor(
         bob::extension::FunctionDoc("class_name", "Constructor Description")
          .add_prototype("param1", "")
          .add_parameter("param1", "type1", "Description of param1")
       )
   ;

.. note::

   The second parameter ``""`` in ``add_prototype`` prevents the output type (which otherwise defaults to ``"None"``) to be written.

.. note::

   For constructor documentations, there is no need to declare them as member functions.
   This is done automatically for you.

Currently, the ``ClassDoc`` allows to highlight member functions or variables at the beginning of the class documentation.
This highlighting is still under development and might not work as expected.


Possible speed issues
=====================

In order to speed up the loading time of the modules, you might want to reduce the amount of documentation that is generated (though I haven't experienced any speed differences).
For this purpose, just compile your bindings using the ``"-DBOB_SHORT_DOCSTRINGS"`` compiler option, e.g. by simply define an environment variable ``BOB_SHORT_DOCSTRINGS=1`` before invoking ``buildout``.

In any of these cases, only the short descriptions will be returned as the doc string.


Documentation Generation and Unit Testing
-----------------------------------------

If you intend to distribute your newly created package, please consider carefully documenting and creating unit tests for your package.
Documentation is a great starting point for users and unit tests can be used to check functionality in unexpected circumstances such as variations in package versions.


Documentation
=============

To write documentation, use the `Sphinx`_ Documentation Generator.
A template has been setup for you under the ``docs`` directory.
Get familiar with Sphinx and then unleash the writer in you.

Once you have edited both ``doc/conf.py`` and ``doc/index.rst`` you can run the documentation generator executing:

.. code-block:: sh

  $ ./bin/sphinx-build doc sphinx
  ...

This example generates the output of the sphinx processing in the directory ``sphinx``.
You can find more options for ``sphinx-build`` using the ``-h`` flag:

.. code-block:: sh

  $ ./bin/sphinx-build -h
  ...

.. note::

  If the code you are distributing corresponds to the work described in a publication, don't forget to mention it in your ``README.rst`` file.


Unit Tests
==========

Writing unit tests is an important asset on code that needs to run in different platforms and a great way to make sure all is OK.
Test units are run with nose_.
To run the test units on your package call:

.. code-block:: sh

  $ ./bin/nosetests -v
  bob.example.library.test.test_reverse ... ok

  ----------------------------------------------------------------------
  Ran 1 test in 0.253s

  OK


Distributing Your Work
----------------------

To distribute a package, we recommend you use PyPI.
`The Hitchhiker’s Guide to Packaging <http://guide.python-distribute.org/>`_ contains details and good examples on how to achieve this.


Version Numbering Scheme
========================

We recommend you follow |project|'s version numbering scheme using a 3-tier string: ``M.m.p``.
The value of ``M`` is a number starting at 1.
This number is changed in case of a major release that brings new APIs and concepts to the table.
The value of ``m`` is a number starting at 0.
Every time a new API is available (but no conceptual modifications are done to the platform)
that number is increased.
Finally, the value of p represents the patch level, starting at 0.
Every time we need to post a new version of |project| that does **not** bring incompatible API modifications, that number is increased.
For example, version 1.0.0 is the first release of |project|.
Version 1.0.1 would be the first patch release.

.. note::

  The numbering scheme for your package and |project|'s may look the same, but should be totally independent of each other.
  |project| may be on version 3.4.2 while your package, still compatible with that release could be on 1.4.5.
  You should state on your ``setup.py`` file which version of |project| your package is compatible with, using the standard notation defined for setuptools installation requirements for packages.

You may use version number extenders for alpha, beta, and candidate releases with the above scheme, by appending ``aN``, ``bN`` or ``cN`` to the version number.
The value of ``N`` should be an integer starting at zero.
Python's setuptools package will correctly classifier package versions following this simple scheme.
For more information on package numbers, consult Python's `PEP 386`_.
Here are lists of valid python version numbers following this scheme::

  0.0.1
  0.1.0a35
  1.2.3b44
  2.4.99c32


Release Methodology for Satellite Packages
==========================================

Here is a set of steps we recommend you follow when releasing a new version of your satellite package:

1. First decide on the new version number your package will get.
   If you are  making a minor, API preserving, modification on an existing stable package (already published on PyPI), just increment the last digit on the version.
   Bigger changes may require that you signal them to users by changing the first digits of the package.
   Alpha, beta or candidate releases don't need to have their main components of the version changed, just bump-up the last digit.
   For example ``1.0.3a3`` would become ``1.0.3a4``;

2. In case you are making an API modification to your package, you should think if you would like to branch your repository at this position.
   You don't have to care about this detail with new packages, naturally.

   If required, branching will allow you to still make modifications (patches) on the old version of the code and develop on the ``master`` branch for the new release, in parallel.
   It is important to branch when you break functionality on existing code - for example to reach compatibility with an upcoming version of |project|.
   After a few major releases, your repository should look somewhat like this::

      ----> time

      initial commit
      o---------------o---------o-----o-----------------------> master
                      |         |     |
                      |         |     |   v2.0.0
                      |         |     +---x----------> 2.0
                      |         |
                      |         | v1.1.0  v1.1.1
                      |         +-x-------x------> 1.1
                      |
                      |   v1.0.0  v1.0.1a0
                      +---x-------x-------> 1.0

   The ``o``'s mark the points in which you decided to branch your project.
   The ``x``'s mark places where you decided to release a new version of your satellite package on PyPI.
   The ``-``'s mark commits on your repository.
   Time flies from left to right.

   In this ficticious representation, the ``master`` branch continue under development, but one can see older branches don't receive much attention anymore.

   Here is an example for creating a branch at github (many of our satellite packages are hosted there).
   Let's create a branch called ``1.1``::

     $ git branch 1.1
     $ git checkout 1.1
     $ git push origin 1.1

3. When you decide to release something publicly, we recommend you **tag** the version of the package on your repository, so you have a marker to what code you actually published on PyPI.
   Tagging on github would go like this::

     $ git tag v1.1.0
     $ git push && git push --tags

   Notice use prefix tag names with ``v``.

4. Finally, after branching and tagging, it is time for you to publish your new package on PyPI.
   When the package is ready and you have tested it, just do the following::

     $ python setup.py register #if you modified your setup.py or README.rst
     $ python setup.py sdist --formats zip upload

    .. note::
      You can also check the .zip file that will be uploaded to PyPI before actually uploading it.
      Just call::

        $ python setup.py sdist --formats zip

      and check what was put into the ``dist`` directory.

5. Announce the update on the relevant channels.


Upload Additional Documentation to PythonHosted.org
===================================================

In case you have written additional sphinx documentation in your satellite package that you want to share with the world, there is an easy way to push the documentation to `PythonHosted.org <http://pythonhosted.org>`_.
More detailed information are given `here <http://pythonhosted.org/an_example_pypi_project/buildanduploadsphinx.html>`__, which translates roughly into:

1. Edit your setup.py and add the required package ``sphinx-pypi-upload``:

  .. code-block:: python

    setup(
      ...

      setup_requires=[
        ...
        'sphinx-pypi-upload',
      ],

      ...
    )

  And re-run ``buildout``::

    $ ./bin/buildout

2. Create or edit the file ``setup.cfg`` in the root directory of your package.
   The content should be something like:

  .. code-block:: ini

    [build_sphinx]
    source-dir = docs
    build-dir  = sphinx
    all_files  = 1

    [upload_sphinx]
    upload-dir = sphinx/html

3. Create and upload the documentation::

    $ ./bin/python setup.py build_sphinx
    $ ./bin/python setup.py upload_sphinx

The link to the documentation will automatically be added to the PyPI page of your package.
Usually it is a good idea to check the documentation after building and before uploading.


Satellite Packages Available
============================

Look here for our growing list of `Satellite Packages`_.

.. include:: links.rst
