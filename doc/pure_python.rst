.. vim: set fileencoding=utf-8 :

.. _bob.extension.pure_python:

===========================
Python package development
===========================

The tutorial below will explain the anatomy of |project| packages which can
serve as instructions on how to create a new package or how to modify an
existing one. The guide heavily relies on the use of Python `setuptools`_ and
`zc.buildout`_.

.. note::
  The core of our strategy is based on standard tools for *defining* and
  *deploying* Python packages. If you are not familiar with Python's
  `setuptools`_ or PyPI_, it can be beneficial to learn about those before you
  start. Python's `Setuptools`_ is a mechanism to *define and distribute*
  Python code in a packaged format, optionally through `PyPI`_, a web-based
  Python package index and distribution portal. `Python packaging guide`_ can
  also be useful to learn about setuptools_.

.. note::
  You should also go through the `new package instructions`_ page when creating a new
  package. It is a step-by-step guide on how to setup your package, and in particular
  contains various templates that you must use. Among other stuff, you will find
  templates for ``README.rst``, ``setup.py``, ``buildout.cfg`` files,
  for continuous integration and for the conda recipe of your package.

Anatomy of a package
--------------------

The best way to create your package is to download the skeleton that is
described in this tutorial and build on it, modifying what you need.
Fire-up a shell window, activate your development environment (as explained in
:doc:`development`) and then do this:

.. code-block:: sh

  $ git clone https://gitlab.idiap.ch/bob/bob.extension.git
  $ cp -R bob.extension/bob/extension/examples/bob.example.project ./
  $ rm -rf bob.extension # optionally remove the cloned source of bob.extension
  $ cd bob.example.project
  $ git init # initialize this folder as a git repository.

The anatomy of a minimal package should look like the following:

.. code-block:: sh

  .
  +-- MANIFEST.in       # extras to be installed, besides the Python files
  +-- README.rst        # a minimal description of the package, in reStructuredText format
  +-- buildout.cfg      # buildout configuration
  +-- setup.py          # installation instruction for this particular package
  +-- requirements.txt  # requirements of your package
  +-- version.txt       # the (current) version of your package
  +-- doc               # documentation directory
  |   +-- conf.py       # Sphinx configuration
  |   +-- index.rst     # Documentation starting point for Sphinx
  +-- bob               # Python package (a.k.a. "the code")
  |   +-- example
  |   |   +-- project
  |   |   |   +-- script
  |   |   |   |   +-- __init__.py
  |   |   |   |   +-- version.py
  |   |   |   +-- __init__.py
  |   |   |   +-- test.py
  |   |   +-- __init__.py
  |   +-- __init__.py

Our example that you just downloaded contains exactly these files. All files
are in text format and should be heavily commented. The most important file
that requires your attention is ``setup.py``. This file contains the basic
information for the Python package you will be creating. It defines scripts the
package provides and also loads dependencies it requires for execution.

.. note::
    Note that the dependencies are not specified directly in the ``setup.py``
    file, but are loaded from the ``requirements.txt`` file. This is unique to
    |project| packages and you should always do this.

To customize the package to your needs, you will need to edit this file and
modify it accordingly. Before doing so, it is suggested you go through all of
this tutorial so you are familiar with the whole environment. The example
package, as it is distributed, contains a fully working example.

In the remainder of this document, we mainly explain how to setup the
``setup.py`` and the ``buildout.cfg``, going from minimal working example to
more advanced features.


Setting up your package
-----------------------

The package you cloned above is a pure-Python example package and contains all
elements to get you started.  It defines a single library module called
``bob.example.project``, which declares a simple script, called ``version.py``
that prints out the version of the dependent library
``bob.blitz``. These information is available in your
``setup.py`` file and particularly in its ``setup`` function:

.. code-block:: python

  setup(
    name = 'bob.example.project',
    version = open("version.txt").read().rstrip(),
    ...
    packages = find_packages(),
    ...
    install_requires = install_requires,
    ...
    entry_points = {
      'console_scripts' : [
        'bob_example_project_version.py = bob.example.project.script.version:main',
      ],
    },
  )

In detail, it defines the name and the version of this package, which files
belong to the package (those files are automatically collected by the
``find_packages`` function), other packages that we depend on, namespaces and
console scripts. The full set of options can be inspected in the
`Setuptools documentation`_.

.. warning::

  The (executable) script name should somehow contain the namespace of the
  package


Building your package
---------------------

To be able to use the package, we first need to build and install it locally.
This is explained in detail in `bob development tools`_.
The buildout configuration file of the package looks like:


.. code-block:: ini

   [buildout]
   parts = scripts
   develop = .
   eggs = bob.example.project
   extensions = bob.buildout
   newest = false
   verbose = true
   debug = false

   [scripts]
   recipe = bob.buildout:scripts
   dependent-scripts = true

The ``develop`` option points to ``.`` which is the current directory
(directory of ``bob.example.project``).
Run buildout:

.. code-block:: sh

  $ buildout
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

After buildout has finished, you should now be able to execute ``./bin/bob_example_project_version.py``:

.. code-block:: sh

   $ ./bin/bob_example_project_version.py
   bob.blitz: 2.0.5 [api=0x0201] ([PATH]/eggs/bob.blitz-2.0.5-py2.7-linux-x86_64.egg)
   * C/C++ dependencies:
     - Blitz++: 0.10
     - Boost: 1.55.0
     - Compiler: {'version': '4.9.2', 'name': 'gcc'}
     - NumPy: {'abi': '0x01000009', 'api': '0x00000009'}
     - Python: 2.7.9
   * Python dependencies:
     - bob.extension: 2.0.7 ([PATH]/bob.example.project/eggs/bob.extension-2.0.7-py2.7.egg)
     - numpy: 1.8.2 (/usr/lib/python2.7/dist-packages)
     - setuptools: 15.1 ([PATH]/bob.example.project/eggs/setuptools-15.1-py2.7.egg)


.. note::
    We advise to *always* have two configuration files to be used with
    buildout:

    1. A simple minimal ``buildout.cfg`` file, such as the one in
       bob.example.project
    2. A more complete version, called ``develop.cfg`` that checks out whatever
       (Bob) packages that your project depend on.


Everything is now setup for you to continue the development of this package.
Modify all required files to setup your own package name, description and
dependencies. Start adding files to your library (or libraries) and, if you
wish, make this package available in a place with public access to make your
research public. We recommend using Gitlab or GitHub. Optionally, `drop-us a
message <discuss_>`_ talking about the availability of this package so we can
add it to the growing list of `bob packages`_.

.. include:: links.rst
