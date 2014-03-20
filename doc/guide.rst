.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.dos.anjos@gmail.com>
.. Tue 15 Oct 17:41:52 2013

=========================================================
 |project| Satellite Package Development and Maintenance
=========================================================

This tutorial explains how to build and distribute `Python`-based working
environments for |project|. By following these instructions you will be able
to:

* Create a basic working environment using either a stock |project|
  installation or your own compiled (and possibly uninstalled) version of
  |project|;
* Install additional python packages to augment your virtual work environment
  capabilities - e.g., to include a new python package for a specific purpose
  covering functionality that does not necessarily exists in |project| or any
  available Satellite Package;
* Distribute your work to others in a clean and organized manner.

These instructions heavily rely on the use of Python `distutils`_ and
`zc.buildout`_. One important advantage of using `zc.buildout`_ is that it does
**not** require administrator privileges for setting up any of the above.
Furthermore, you will be able to create distributable environments for each
project you have. This is a great way to release code for laboratory exercises
or for a particular publication that depends on |project|.

.. note::
  The core of our strategy is based on standard tools for *defining* and
  *deploying* Python packages. If you are not familiar with Python's
  ``setuptools``, ``distutils`` or PyPI, it can be beneficial to `learn about
  those <http://guide.python-distribute.org/>`_ before you start. Python
  `Setuptools`_ and `Distutils`_ are mechanisms to *define and distribute*
  python code in a packaged format, optionally through `PyPI`_, a web-based
  Python package index and distribution portal.

  `zc.buildout`_ is a tool to *deploy* Python packages locally, automatically
  setting up and encapsulating your work environment.

Anatomy of a buildout Python package
------------------------------------

The best way to create your package is to download a `skeleton from the Idiap
github website <https://github.com/idiap/bob.project.example>`_ and build on
it, modifying what you need. Fire-up a shell window and than do this:

.. code-block:: sh

  $ git clone --depth=1 https://github.com/idiap/bob.project.example.git
  $ cd bob.project.example
  $ rm -rf .git #this is optional - you won't need the .git directory

We now recommend you read the file ``README.rst`` situated at the root of the
just downloaded material. It contains important information on other
functionality such as document generation and unit testing, which will not be
covered on this introductory material.

The anatomy of a minimal package should look like the following:

.. code-block:: sh

  .
  +-- MANIFEST.in   # extras to be installed, besides the python files
  +-- README.rst    # a description of the package, in restructured-text format
  +-- bootstrap.py  # stock script downloaded from zc.buildout's website
  +-- buildout.cfg  # buildout configuration
  +-- setup.py      # installation + requirements for this particular package
  +-- docs          # documentation directory
  |   +-- conf.py   # Sphinx configuration
  |   +-- index.rst # Documentation starting point for Sphinx
  +-- xbob          # python package (a.k.a. "the code")
  |   +-- example
  |   |   +-- script
  |   |   |   +-- __init__.py
  |   |   |   +-- version.py
  |   |   +-- __init__.py
  |   |   +-- test.py
  |   +-- __init__.py

Our example that you just downloaded contains these files and a few extra ones
useful for this tutorial. Inspect the package so you are aware of its contents.
All files are in text format and should be heavily commented. The most
important file that requires your attention is ``setup.py``. This file contains
the basic information for the Python package you will be creating. It defines
scripts the package provides and dependencies it requires for execution. To
customize the package to your needs, you will need to edit this file and modify
it accordingly. Before doing so, it is suggested you go through all of this
tutorial so you are familiar with the whole environment. The example package,
as it is distributed, contains a fully working example.

In the remainder of this document, we explain how to setup ``buildout.cfg`` so
you can work in different operational modes - the ones which are more common
development scenarios.

Pure-Python Packages
--------------------

Pure-Python packages are the most common. They contain code that is exclusively
written in Python. This contrasts to packages that are written in a mixture of
Python and C/C++.

The package you cloned above is a pure-Python example package and contains all
elements to get you started. It defines a single library inside called
``xbob.example``, which declares a simple script, called ``version.py`` that
prints out the version of |project|.  When you clone the package, you will not
find any executable as ``buildout`` needs to check all dependencies and install
missing ones before you can execute anything. Here is how to go from nothing to
everything:

.. code-block:: sh

  $ python bootstrap.py
  Creating directory '/home/user/work/tmp/bob.project.example/bin'.
  Creating directory '/home/user/work/tmp/bob.project.example/parts'.
  Creating directory '/home/user/work/tmp/bob.project.example/eggs'.
  Creating directory '/home/user/work/tmp/bob.project.example/develop-eggs'.
  Generated script '/home/user/work/tmp/bob.project.example/bin/buildout'.
  $ ./bin/buildout
  Develop: '/remote/filer.gx/user.active/aanjos/work/tmp/bob.project.example/.'
  Getting distribution for 'xbob.buildout'.
  Got xbob.buildout 0.2.13.
  Getting distribution for 'zc.recipe.egg>=2.0.0a3'.
  Got zc.recipe.egg 2.0.0.
  Installing scripts.
  ...

.. note::

  The Python shell used in the first line of the previous command set
  determines the Python interpreter that will be used for all scripts developed
  inside this package. To build your environment around a different version of
  Python, just make sure to correctly choose the interpreter you wish to use.
  If you just want to get things rolling, using ``python bootstrap.py`` will,
  in most cases, do the right thing.

You should now be able to execute ``./bin/version.py``:

.. code-block:: sh

  $ ./bin/version.py
  The installed version of xbob.blitz is `2.0.0a0'
  xbob.blitz is installed at `...'
  xbob.blitz depends on the following Python packages:
   * xbob.extension: 0.3.0a0 (...)
   * numpy: 1.6.2 (/usr/lib/python2.7/dist-packages)
   * distribute: 0.6.28dev-r0 (/usr/lib/python2.7/dist-packages)
   * coverage: 3.7.1 (...)
   * sphinx: 1.1.3 (/usr/lib/python2.7/dist-packages)
   * nose: 1.1.2 (/usr/lib/python2.7/dist-packages)
   * docutils: 0.8.1 (/usr/lib/python2.7/dist-packages)
   * jinja2: 2.6 (/usr/lib/python2.7/dist-packages)
   * pygments: 1.5 (/usr/lib/python2.7/dist-packages)
  xbob.blitz depends on the following C/C++ APIs:
   * Python: 2.7.3
   * Boost: 1.50.0
   * Blitz++: 0.10
   * NumPy: 0x01000009
   * Compiler: ('gcc', '4.7.2')

Everything is now setup for you to continue the development of this package.
Modify all required files to setup your own package name, description and
dependencies. Start adding files to your library (or libraries) and, if you
wish, make this package available in a place with public access to make your
research public. We recommend using Github. Optionally, `drop-us a message
<https://groups.google.com/d/forum/bob-devel>`_ talking about the availability
of this package so we can add it to the growing list of `Satellite Packages`_.

C or C++/Python Packages
------------------------

Creating C++/Python bindings should be rather. Firstly, edit your ``setup.py``
so that you include the following:

.. code-block:: python

  from setuptools import setup, find_packages, dist
  dist.Distribution(dict(setup_requires=['xbob.blitz']))
  from xbob.blitz.extension import Extension
  ...

  setup(

    name="xbob.myext",
    version="1.0.0",
    ...
    install_requires=[
      'setuptools',
      'xbob.blitz',
    ],
    ...
    namespace_packages=[
      'xbob',
    ],
    ...
    ext_modules=[
      Extension("xbob.myext._myext",
        [
          "xbob/myext/ext/file1.cpp",
          "xbob/myext/ext/file2.cpp",
          "xbob/myext/ext/main.cpp",
        ],
        packages = [ #other c/c++ api dependences
          'bob-math',
          'bob-sp',
          ]
        ),
      ... #add more extensions if you wish
    ],

    ...
    )

These modifications will allow you to compile extensions that are linked
against our core Python-C++ bridge ``xbob.blitz``. You can specify any
``pkg-config`` module and that will be linked in (for example, ``bob-ip`` or
``opencv``) using the ``packages`` setting as shown above.  Other modules and
options can be set manually using `the standard options for python extensions
<http://docs.python.org/2/extending/building.html>`_.

Document Generation and Unit Testing
------------------------------------

If you intend to distribute your newly created package, please consider
carefully documenting and creating unit tests for your package. Documentation
is a great starting point for users and unit tests can be used to check
funcionality in unexpected circumstances such as variations in package
versions.

Documentation
=============

To write documentation, use the `Sphinx`_ Document Generator. A template has
been setup for you under the ``docs`` directory. Get familiar with Sphinx and
then unleash the writer in you.

Once you have edited both ``docs/conf.py`` and ``docs/index.rst`` you can run
the document generator executing:

.. code-block:: sh

  $ ./bin/sphinx-build docs sphinx
  ...

This example generates the output of the sphinx processing in the directory
``sphinx``. You can find more options for ``sphinx-build`` using the ``-h``
flag:

.. code-block:: sh

  $ ./bin/sphinx-build -h
  ...

.. note::

  If the code you are distributing corresponds to the work described in a
  publication, don't forget to mention it in your ``README.rst`` file.

Unit Tests
==========

Writing unit tests is an important asset on code that needs to run in different
platforms and a great way to make sure all is OK. Test units are run with
`nose`_. To run the test unitson your package:

.. code-block:: sh

  $ ./bin/nosetests -v
  test_version (xbob.example.test.MyTests) ... ok

  ----------------------------------------------------------------------
  Ran 1 test in 0.001s

  OK

Creating Database Satellite Packages
------------------------------------

Database satellite packages are special satellite packages that can hook-in
|project|'s database manager ``xbob_dbmanage.py``. Except for this detail, they
should look exactly like a normal package.

To allow the database to be hooked to the ``xbob_dbmanage.py`` you must
implement a non-virtual python class that inherits from
:py:class:`bob.db.driver.Interface`. Your concrete implementation should then
be described at the ``setup.py`` file with a special ``bob.db`` entry point:

.. code-block:: python

    # bob database declaration
    'bob.db': [
      'replay = xbob.db.replay.driver:Interface',
      ],

At present, there is no formal design guide for databases. Nevertheless, it is
considered a good practice to follow the design of currently existing database
`satellite packages`_. This should ease migration in case of future changes.

Python Package Namespace
------------------------

We like to make use of namespaces to define combined sets of functionality that
go well together. Python package namespaces are `explained in details here
<http://peak.telecommunity.com/DevCenter/setuptools#namespace-package>`_
together with implementation details. Two basic namespaces are available when
you are operating with |project| or add-ons, such as database access APIs
(shipped separately): the ``bob`` namespace is reserved for utilities built and
shiped with |project|. The namespace ``xbob`` (as for *external* |project|
packages) should be used for all other applications that are meant to be
distributed and augment |project|'s features.

The example package you downloaded creates package inside the ``xbob``
namespace called ``example``. Examine this example in details and understand
how to distributed namespace'd packages in the URL above.

In particular, if you are creating a database access API, please consider
putting all of your package contents *inside* the namespace
``xbob.db.<package>``, therefore declaring two namespaces: ``xbob`` and
``xbob.db``. All standard database access APIs follow this strategy. Just look
at our currently existing database `satellite packages`_ for examples.

Distributing Your Work
----------------------

To distribute a package, we recommend you use PyPI. The `The Hitchhiker’s Guide
to Packaging <http://guide.python-distribute.org/>`_ contains details and good
examples on how to achieve this.

Version Numbering Scheme
------------------------

We recommend you follow |project|'s version numbering scheme using a 3-tier
string: ``M.m.p``. The value of ``M`` is a number starting at 1. This number is
changed in case of a major release that brings new APIs and concepts to the
table. The value of ``m`` is a number starting at 0 (zero). Every time a new
API is available (but no conceptual modifications are done to the platform)
that number is increased. Finally, the value of p represents the patch level,
starting at 0 (zero). Every time we need to post a new version of |project|
that does **not** bring incompatible API modifications, that number is
increased. For example, version 1.0.0 is the first release of |project|.
Version 1.0.1 would be the first patch release.

.. note::

  The numbering scheme for your package and |project|'s may look the same, but
  should be totally independent of each other. |project| may be on version
  3.4.2 while your package, still compatible with that release could be on
  1.4.5. You should state on your ``setup.py`` file which version of |project|
  your package is compatible with, using the standard notation defined for
  setuptools installation requirements for packages.

You may use version number extenders for alpha, beta, and candidate releases
with the above scheme, by appending ``aN``, ``bN`` or ``cN`` to the version
number. The value of ``N`` should be an integer starting at zero. Python's
setuptools package will correctly classifier package versions following this
simple scheme. For more information on package numbers, consult Python's `PEP
386`_. Here are lists of valid python version numbers following this scheme::

  0.0.1
  0.1.0a35
  1.2.3b44
  2.4.99c32

Release Methodology for Satellite Packages
------------------------------------------

Here is a set of steps we recommend you follow when releasing a new version of
your satellite package:

1. First decide on the new version number your package will get. If you are
   making a minor, API preserving, modification on an existing stable package
   (already published on PyPI), just increment the last digit on the version.
   Bigger changes may require that you signal them to users by changing the
   first digits of the package. Alpha, beta or candidate releases don't need to
   have their main components of the version changed, just bump-up the last
   digit. For example ``1.0.3a3`` would become ``1.0.3a4``;

2. In case you are making an API modification to your package, you should think
   if you would like to branch your repository at this position. You don't have
   to care about this detail with new packages, naturally.

   If required, branching will allow you to still make modifications (patches)
   on the old version of the code and develop on the ``master`` branch for the
   new release, in parallel.  It is important to branch when you break
   functionality on existing code - for example to reach compatibility with an
   upcoming version of |project|.  After a few major releases, your repository
   should look somewhat like this::

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
   The ``x``'s mark places where you decided to release a new version of your
   satellite package on PyPI. The ``-``'s mark commits on your repository. Time
   flies from left to right.

   In this ficticious representation, the ``master`` branch continue under
   development, but one can see older branches don't receive much attention
   anymore.

   Here is an example for creating a branch at github (many of our satellite
   packages are hosted there). Let's create a branch called ``1.1``::

    $ git branch 1.1
    $ git checkout 1.1
    $ git push origin 1.1

3. When you decide to release something publicly, we recommend you **tag** the
   version of the package on your repository, so you have a marker to what code
   you actually published on PyPI. Tagging on github would go like this::

    $ git tag v1.1.0
    $ git push && git push --tags

   Notice use prefix tag names with ``v``.

4. Finally, after branching and tagging, it is time for you to publish your new
   package on PyPI. When the package is ready and you have tested it, just do
   the following::

    $ python setup.py register #if you modified your setup.py or README.rst
    $ python setup.py sdist --formats=zip upload

    .. note::
      You can also check the .zip file that will be uploaded to PyPI before
      actually uploading it. Just call::

        $ python setup.py sdist --formats=zip upload

      and check what was put into the ``dist`` directory.

5. Announce the update on the relevant channels.


Upload Additional Documentation to PythonHosted.org
---------------------------------------------------

In case you have written additional sphinx documentation in your satellite
package that you want to share with the world, there is an easy way to push the
documentation to `PythonHosted.org <http://pythonhosted.org>`_.  More detailed
information are given `here
<http://pythonhosted.org/an_example_pypi_project/buildanduploadsphinx.html>`_,
which translates roughly into:

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
    build-dir  = build/sphinx
    all_files  = 1

    [upload_sphinx]
    upload-dir = build/sphinx/html

3. Create and upload the documentation::

    $ ./bin/python setup.py build_sphinx
    $ ./bin/python setup.py upload_sphinx

The link to the documentation will automatically be added to the PyPI page of
your package. Usually it is a good idea to check the documentation after
building and before uploading.

Satellite Packages Available
----------------------------

Look here for our growing list of `Satellite Packages`_.

.. include:: links.rst
