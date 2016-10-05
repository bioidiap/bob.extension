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
  If you are not familiar with Python's ``setuptools``, ``distutils`` or PyPI, it can be beneficial to `learn about those <https://docs.python.org/2/distutils/>`_ before you start.
  Python's `Setuptools`_ and `Distutils`_ are mechanisms to *define and distribute* Python code in a packaged format, optionally through `PyPI`_, a web-based Python package index and distribution portal.

  `zc.buildout`_ is a tool to *deploy* Python packages locally, automatically setting up and encapsulating your work environment.


Anatomy of a buildout Python package
------------------------------------

The best way to create your package is to download one of the skeletons that are described in this tutorial and build on it, modifying what you need.
Fire-up a shell window and than do this:

.. code-block:: sh

  $ wget https://gitlab.idiap.ch/bob/bob.extension/raw/master/examples/bob.example.project.tar.bz2
  $ tar -xjf bob.example.project.tar.bz2
  $ cd bob.example.project

We now recommend you read the file ``README.rst``, which is written in `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ format, situated at the root of the just downloaded material.
It contains important information on other functionality such as document generation and unit testing, which will not be covered on this introductory material.

The anatomy of a minimal package should look like the following:

.. code-block:: sh

  .
  +-- MANIFEST.in            # extras to be installed, besides the Python files
  +-- README.rst             # a description of the package, in reStructuredText format
  +-- bootstrap-buildout.py  # stock script downloaded from zc.buildout's website
  +-- buildout.cfg           # buildout configuration
  +-- setup.py               # installation + requirements for this particular package
  +-- version.txt            # the (current) version of your package
  +-- doc                    # documentation directory
  |   +-- conf.py            # Sphinx configuration
  |   +-- index.rst          # Documentation starting point for Sphinx
  +-- bob                    # Python package (a.k.a. "the code")
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

In the remainder of this document, we explain how to setup the ``setup.py`` and the ``buildout.cfg`` so you can work in different operational modes - the ones which are more common development scenarios.

Pure-Python Packages
--------------------

Pure-Python packages are the most common.
They contain code that is exclusively written in Python.
This contrasts to packages that are written in a mixture of Python and C/C++, which are explained in more detail below.

The package you cloned above is a pure-Python example package and contains all
elements to get you started.  It defines a single library module called
``bob.example.project``, which declares a simple script, called ``version.py``
that prints out the version of the dependent library :ref:`bob.blitz`.  When
you clone the package, you will not find any executable as ``buildout`` needs
to check all dependencies and install missing ones before you can execute
anything.  Particularly, it inspects the ``setup.py`` file in the root
directory of the package, which contains all required information to build the
package, all of which is contained in the ``setup`` function:

.. code-block:: python

  setup(
    name = 'bob.example.project',
    version = open("version.txt").read().rstrip(),
    ...
    packages = find_packages(),
    ...
    install_requires = [
      'setuptools',
      'bob.blitz'
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

  $ python bootstrap-buildout.py
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
  If you just want to get things rolling, using ``python bootstrap-buildout.py`` will, in most cases, do the right thing.

.. note::
   When you have installed an older version of |project| -- i.e. |project| v1.x, you might need to uninstall it first, see https://gitlab.idiap.ch/bob/bob/wikis/Installation.



.. _idiap_note:

.. warning::

  **Using Bob 2.0 at Idiap**

  At Idiap_, we provide a pre-installed version of the latest stable version of the packages.
  To use these packages, you just have to bootstrap your package with the following command:

  .. code-block:: sh

     $ /idiap/group/torch5spro/releases/bob-stable/py27/bin/python bootstrap-buildout.py

  or

  .. code-block:: sh

     $ /idiap/group/torch5spro/releases/bob-stable/py34/bin/python bootstrap-buildout.py

  if you prefer Python 3.

  On the other hand, when you want to use the latest (unstable) versions of the |project| packages in your satellite package, you might want to use:

  .. code-block:: sh

    $ /idiap/group/torch5spro/nightlies/last/bob/linux-x86_64-release/bin/python bootstrap-buildout.py

  .. warning::
     This python version is replaced every night.
     Do not use it in any over-night calculations.

  Sometimes, you don't want to use the packages that are published on PyPI_, but the latest (nightly compiled) versions of all our packages.
  In this case, use:

  .. code-block:: sh

    $ ./bin/buildout buildout:find-links=https://www.idiap.ch/software/bob/packages/nightlies/last buildout:prefer-final=false

  .. note::
     You can freely mix the all possible ways to obtain packages.
     For example, you can use the ``bob-stable`` installations, and hand-select some packages to be downloaded from PyPI_ or from the nightlies packages (see above), e.g., using ``mr.developer`` (see below).


Using buildout
==============

Buildout has set up you local environment with packages that it finds from different sources.
It is initialized by the ``buildout.cfg`` file, which is part of the package that you unzipped above.
Let's have a look inside it:

.. code-block:: guess

   [buildout]
   parts = scripts
   eggs = bob.example.project
   extensions = bob.buildout

   develop = .

   ; options for bob.buildout
   debug = true
   verbose = true
   newest = false

   [scripts]
   recipe = bob.buildout:scripts

It is organized in several *sections*, which are indicated by ``[]``, where the default section ``[buildout]`` is always required.
Some of the entries need attention.

* The first entry are the ``eggs``.
  In there, you can list all python packages that should be installed, additionally to the ones specified in the ``install_requires`` section of the ``setup.py`` (see below).
  These packages can contain other |project| packages (like any database package such as ``bob.db.mobio``), but also other Python packages such as ``gridtk``.
  These packages will be available to be used in your environment.
  At least, the current package needs to be in the ``eggs`` list.

* The ``extensions`` list includes all extensions that are required in the buildout process.
  By default, only ``bob.buildout`` is required, but more extensions can be added (see ``mr.developer`` below).

* The next entry is the ``develop`` list.
  There, you can list directories that contain Python packages, which will be build in exactly the order that you specified there.
  With this option, you can tell buildout particularly, in which directories it should look for some packages.
  Note that the ``develop``ed packages are not automatically included into the ``eggs``.
  Of course, you need to develop the current package, which is stored in ``.`` i.e, the current directory.

The remaining options define, how the packages are build.
For example, the ``debug`` flag defined, how the :ref:`C++ code <extension-c++>` in all the packages is built.
The ``verbose`` options handles the verbosity of the build.
When the ``newest`` flag is set to ``true``, buildout will install all packages in the latest versions, even if an older version is already available.


Using mr.developer
==================

One extension that is regularly used in most of |project|'s packages is `mr.developer`_.
It can be used to automatically check out packages from git repositories, and places them into the ``./src`` directory.
It can be simply set up:

.. code-block:: guess

   [buildout]
   ...

   extensions = bob.buildout
                mr.developer

   auto-checkout = *

   develop = src/bob.blitz
             .

   [sources]
   bob.blitz = git https://gitlab.idiap.ch/bob/bob.blitz

   ...

A new section called ``[sources]`` appears, where the package information for `mr.developer`_ is initialized, for more details, please read it's documentation.
Again, ``mr.developer`` does not automatically place the packages into the ``develop`` list (and neither in the ``eggs``), so you have to do that yourself.


Running buildout
================

Finally, running buildout is a two-step process, which is detailed above.
The command line ``./bin/buildout`` will actually run buildout and build your local environment.
All options in the buildout.cfg can be overwritten on command line, by specifying ``buildout:option=...``, where ``option`` can be any entry in the ``buildout.cfg``.
Finally, buildout will perform the following steps:

1. It checks out the packages that you specified using ``mr.developer``.
2. It develops all packages in the ``develop`` section.
3. It will go through the list of ``eggs`` and search for according packages in the following order:

   a) In one of the already developed directories.
   b) In the python environment, e.g., packages installed with ``pip``.
   c) Online, i.e., in the ``find-links`` directory, or by default on PyPI_.

4. It will populate the ``./bin`` directory with all the ``console_scripts`` that you have specified in the ``setup.py``.
In our example, this is ``./bin/version.py``.

Your local environment
======================

After buildout has finished, you should now be able to execute ``./bin/version.py``:

.. code-block:: sh

   $ ./bin/version.py
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

.. code-block:: guess

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

To allow the database to be hooked to the ``bob_dbmanage.py`` you must implement a non-virtual Python class that inherits from :py:class:`bob.db.base.driver.Interface`.
Your concrete implementation should then be described at the ``setup.py`` file with a special ``bob.db`` entry point:

.. code-block:: python

    # bob database declaration
    'bob.db': [
      'example = bob.db.example.driver:Interface',
    ],

At present, there is no formal design guide for databases.
Nevertheless, it is considered a good practice to follow the design of currently existing database `satellite packages`_.
This should ease migration in case of future changes.



Documentation Generation and Unit Testing
-----------------------------------------

If you intend to distribute your newly created package, please consider carefully documenting and creating unit tests for your package.
Documentation is a great starting point for users and unit tests can be used to check functionality in unexpected circumstances such as variations in package versions.


Documentation
=============

To write documentation, use the `Sphinx`_ Documentation Generator.
A template has been setup for you under the ``doc`` directory.
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

  If the code you are distributing corresponds to the work described in a publication, don't forget to mention it in your ``doc/index.rst`` file.


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

To distribute a package, we recommend you use PyPI_.
`The Hitchhiker’s Guide to Packaging <http://guide.python-distribute.org/>`_ contains details and good examples on how to achieve this.
Particularly, you should edit your ``README.rst`` file to have a proper description of your package.
This file will be used to generate the front page of your package on PyPI_ and will, hence, be the first contact point of the world with your package.

.. note::
  If you are writing a package to extend Bob, you might want to follow the README structure of all Bob packages.
  The ``README.rst`` of **this package** (``bob.extension``) is a good example, including all the badges that show the current status of the package and the link to relevant information.

To ease up your life, we also provide a script to run all steps to publish your package.
Please read the following paragraphs to understand the steps in the ``./bin/bob_new_version.py`` script that will be explained at the end of this section.

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
Here are lists of valid Python version numbers following this scheme::

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

   In this fictitious representation, the ``master`` branch continue under development, but one can see older branches don't receive much attention anymore.

   Here is an example for creating a branch at gitlab (many of our satellite packages are hosted there).
   Let's create a branch called ``1.1``::

   .. code-block:: sh

     $ git branch 1.1
     $ git checkout 1.1
     $ git push origin 1.1

3. When you decide to release something publicly, we recommend you **tag** the version of the package on your repository, so you have a marker to what code you actually published on PyPI.
   Tagging on gitlab would go like this::

   .. code-block:: sh

     $ git tag v1.1.0
     $ git push && git push --tags

   Notice use prefix tag names with ``v``.

4. Finally, after branching and tagging, it is time for you to publish your new package on PyPI.
   When the package is ready and you have tested it, just do the following::

   .. code-block:: sh

     $ ./bin/python setup.py register #if you modified your setup.py or README.rst
     $ ./bin/python setup.py sdist --formats zip upload

    .. note::
      You can also check the .zip file that will be uploaded to PyPI before actually uploading it.
      Just call:

      .. code-block:: sh

        $ ./bin/python setup.py sdist --formats zip

      and check what was put into the ``dist`` directory.

   .. note::
      To be able to upload a package to PyPI_ you have to register at the web page using a user name and password.

5. Announce the update on the relevant channels.


Upload Additional Documentation to PythonHosted.org
===================================================

In case you have written additional sphinx documentation in your satellite package that you want to share with the world, there is an easy way to push the documentation to `PythonHosted.org <http://pythonhosted.org>`_.
More detailed information are given `here <http://pythonhosted.org/an_example_pypi_project/buildanduploadsphinx.html>`__, which translates roughly into:

.. code-block:: sh

  $ ./bin/python setup.py build_sphinx --source-dir=doc --build-dir=build/doc --all-files
  $ ./bin/python setup.py upload_docs --upload-dir=build/doc/html

The link to the documentation will automatically be added to the PyPI page of your package.
Usually it is a good idea to check the documentation after building and before uploading.


Change the Version of your Satellite Package
============================================

It is well understood that it requires quite some work to understand and follow the steps to publish (a new version) of your package.
Especially, when you want to update the .git repository and the version on PyPI_ at the same time.
In total, 5 steps need to be performed, in the right order.
These steps are:

1. Adding a tag in your git repository, possibly after changing the version of your package.
2. Running buildout to build your package.
3. Register and upload your package at PyPI.
4. Upload the documentation of your package to PythonHosted.org.

and, finally, to keep track of new changes:

5. Switch to a new version number.

All these steps are combined in the ``./bin/bob_new_version.py`` script.
This script needs to be run from within the root directory of your package.
By default, it will make an elaborate guess on the version that you want to upload.
Please run:

.. code-block:: sh

  $ ./bin/bob_new_version.py --help

to see a list of options.
Detailed information of what the script is doing, you can get when using the ``--dry-run`` option (a step that you always should consider before actually executing the script):

.. code-block:: sh

  $ ./bin/bob_new_version.py -vv --dry-run


Satellite Packages Available
============================

Look here for our growing list of `Satellite Packages`_.

.. include:: links.rst
