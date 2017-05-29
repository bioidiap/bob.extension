.. vim: set fileencoding=utf-8 :

.. _bob.extension.pure_python:

===========================
Python package development
===========================

The instructions below heavily rely on the use of Python `setuptools`_ and
`zc.buildout`_.

.. note::
  The core of our strategy is based on standard tools for *defining* and
  *deploying* Python packages. If you are not familiar with Python's
  `setuptools`_ or PyPI_, it can be beneficial to learn about those before you
  start. Python's `Setuptools`_ is a mechanism to *define and distribute*
  Python code in a packaged format, optionally through `PyPI`_, a web-based
  Python package index and distribution portal. `Python packaging guide`_ can
  also be useful to learn about setuptools_.

  `zc.buildout`_ is a tool to *deploy* Python packages locally, automatically
  setting up and encapsulating your work environment.

Anatomy of a package
--------------------

The best way to create your package is to download the skeleton that is
described in this tutorial and build on it, modifying what you need.
Fire-up a shell window, activate your development environment (as explained in
:doc:`development_setup`) and then do this:

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
:ref:`bob.blitz <bob.blitz>`. These information is available in your
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
`Setuptools documentation <https://setuptools.readthedocs.io>`_.

.. warning::

  The (executable) script name should somehow contain the namespace of the package


Building your package
---------------------

To be able to use the package, we first need to build and install it locally.
While developing a package, you need to install your package in *development*
mode so that you do not have to re-install your package after every change that
you do in the source. zc.buildout_ allows you to exactly do that.

.. note::
    zc.buildout_ will create another local environment from your conda_
    environment but unlike conda_ environments this environment is not isolated
    rather it inherits from your conda_ environment. This means you can still
    use the libraries that are installed in your conda_ environment.
    zc.buildout_ also allows you to install PyPI_ packages into your
    environment. You can use it to install some Python library if it is not
    available using conda_. Keep in mind that to install a library you should
    always prefer conda_ but to install your package from source in
    *development* mode, you should use zc.buildout_.

zc.buildout_ provides a ``buildout`` command. ``buildout`` takes as input a
"recipe" that explains how to build a local working environment. The recipe, by
default, is stored in a file called ``buildout.cfg``.

.. important::
    Once ``buildout`` runs, it creates several executable scripts in a local
    ``bin`` folder. Each executable is programmed to use Python from the conda
    environment, but also to consider (prioritarily) your package checkout.
    This means that you need to use the scripts from the ``bin`` folder instead
    of using its equivalence from your conda environment. For example, use
    ``./bin/python`` instead of ``python``.

``buildout`` will examine your ``setup.py`` file using setuptools_ and will
ensure all build and run-time dependencies of your package are available either
through the conda installation or it will install them locally without changing
your conda environment. It is initialized by the ``buildout.cfg`` file, which
is part of the package that you unzipped above. Let\'s have a look inside it:

.. code-block:: guess

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

It is organized in several *sections*, which are indicated by ``[]``, where the default section ``[buildout]`` is always required.
Some of the entries need attention.

* The first entry are the ``eggs``.
  In there, you can list all python packages that should be installed, additionally to the ones specified in the ``requirements.txt``.
  These packages will then be available to be used in your environment.
  Dependencies for those packages will be automatically managed, **as long as you keep** ``bob.buildout`` **in your list of** ``extensions``.
  At least, the current package needs to be in the ``eggs`` list.

* The ``extensions`` list includes all extensions that are required in the buildout process.
  By default, only ``bob.buildout`` is required, but more extensions can be added (more on that later).

* The next entry is the ``develop`` list.
  As a minimal requirement, you need to develop the current package of course, which is stored in ``.``, i.e, the current directory.

The remaining options define how the (dependent) packages are build.
For example, the ``debug`` flag defined, how the :ref:`C++ code <extension-c++>` in all the (dependent) packages is built.
The ``verbose`` options handles the verbosity of the build.
When the ``newest`` flag is set to ``true``, buildout will install all packages in the latest versions, even if an older version is already available.

.. note::

    We normally set ``newest = False`` to avoid downloading already installed dependencies.
    Also, it installs by default the latest stable version of the package, unless
    ``prefer-final = False``, in which case the latest available on PyPI, including betas, will be installed.


.. warning::

    Compiling packages in debug mode (``debug = true``) will make them very
    slow. You should only use this option when you are developing and not for
    running experiments or production.


Finally, run buildout is a single step process by invoking the ``buildout`` command line.
All options in the ``buildout.cfg`` can be overwritten on command line, by specifying
``buildout:option=...``, where ``option`` can be any entry in the ``buildout.cfg``.

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

buildout has performed the following steps:

1. It went through the list of ``eggs``, searched for according packages and installed them *locally*
2. It  populated the ``./bin`` directory with all the ``console_scripts`` that you have specified in the ``setup.py``.
   In our example, this is ``./bin/bob_example_project_version.py``.

.. note::

    One thing to note in package development is that when you
    change the entry points in ``setup.py`` of a package, you need to
    run ``buildout`` again.


Using mr.developer
==================

One extension that may be useful is `mr.developer`_. It allows to develop *other packages* alongside your "main" package.
This extension will allow buildout to automatically check out packages from git repositories, and places them into the ``./src`` directory.
It can be simply set up by adding ``mr.developer`` to the extensions section.

In this case, the develop section should be augmented with the packages you would like to develop.
There, you can list directories that contain Python packages, which will be build in exactly the order that you specified.
With this option, you can tell buildout particularly, in which directories it should look for some packages.

.. code-block:: guess

   [buildout]
   ...

   eggs = bob.blitz
          bob.example.project

   extensions = bob.buildout
                mr.developer

   auto-checkout = *

   develop = src/bob.blitz
             .

   [sources]
   bob.blitz = git https://gitlab.idiap.ch/bob/bob.blitz
   ...

A new section called ``[sources]`` appears, where the package information for `mr.developer`_ is initialized. For more details, please read
`its documentation <https://pypi.python.org/pypi/mr.developer>`_.
Again, mr.developer does not automatically place the packages into the ``develop`` list (and neither in the ``eggs``), so you have to do that yourself.

With this augmented ``buildout.cfg``, the ``buildout`` command will perform the following steps:

1.  It checks out the packages that you specified using ``mr.developer``.

2.  It develops all packages in the ``develop`` section
    (it links the source of the packages to your local environment).

3.  It will go through the list of ``eggs`` and search for according packages in the following order:

    #. In one of the already developed directories.
    #. In the python environment, e.g., packages installed with ``pip``.
    #. Online, i.e. on PyPI_.
4.  It will populate the ``./bin`` directory with all the ``console_scripts`` that you have specified in the ``setup.py``.
    In our example, this is ``./bin/bob_example_project_version.py``.

The order of packages that you list in ``eggs`` and ``develop`` are important and dependencies should be listed first.
Especially, when you want to use a private package and which not available through `pypi`_.
If you do not specify them in order, you might face with some errors like this::

   Could not find index page for 'a.bob.package' (maybe misspelled?)

If you see such errors, you may need to add the missing package to ``eggs`` and ``develop`` and ``sources`` (**of course,
respecting the order of dependencies**).

  .. note::

   We advise to *always* have two configuration files to be used with buildout:
    1. A simple minimal ``buildout.cfg`` file, such as the one in bob.example.project
    2. A more complete version, called ``develop.cfg`` that checks out whatever (Bob) packages that your project depend on.

    Buildout by default looks for ``buildout.cfg`` in your current folder and uses that configuration file.
    You can specify a different config file with the ``-c`` option:

    .. code:: sh

      $ buildout -c develop.cfg


Your local environment
======================

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

Also, when using the newly generated ``./bin/python`` script, you can access all packages that you have developed, including your own package:

.. code-block:: sh

   $ ./bin/python
   >>> import bob.example.project
   >>> print (bob.example.project)
   <module 'bob.example.project' from '[PATH]/bob/example/project/__init__.py'>
   >>> print (bob.example.project.get_config())
   bob.example.project: 0.0.1a0 ([PATH]/bob.example.project)
   * Python dependencies:
     - bob.blitz: 2.0.5 ([PATH]/eggs/bob.blitz-2.0.5-py2.7-linux-x86_64.egg)
     - bob.extension: 2.0.7 ([PATH]/bob.example.project/eggs/bob.extension-2.0.7-py2.7.egg)
     - numpy: 1.8.2 (/usr/lib/python2.7/dist-packages)
     - setuptools: 15.1 ([PATH]/bob.example.project/eggs/setuptools-15.1-py2.7.egg)


Everything is now setup for you to continue the development of this package.
Modify all required files to setup your own package name, description and dependencies.
Start adding files to your library (or libraries) and, if you wish, make this package available in a place with public access to make your research public.
We recommend using Gitlab or GitHub.
Optionally, `drop-us a message <discuss_>`_ talking about the availability of this package so we can add it to the growing list of `bob packages`_.

.. include:: links.rst
