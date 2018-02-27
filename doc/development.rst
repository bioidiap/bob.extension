.. _bob.extension.development:

=======================================
Developing existing |project| packages
=======================================

This guide will explain how to develop existing |project| packages from their
source checkout. The sources of packages are hosted on Idiap's gitlab_ and they
are managed by git_. First we will explain how to setup a local environment,
later we will talk about how to checkout and build one or several packages from
their git_ source.


TLDR
----

Suppose you want to develop two packages, ``bob.extension`` and ``bob.blitz``,
locally:

* Install conda_.
* Add our `conda channel`_ to your channels.

.. code-block:: sh

    $ conda config --set show_channel_urls True
    $ conda config --add channels defaults
    $ conda config --add channels https://www.idiap.ch/software/bob/conda

* Create an isolated environment for the task.

.. code-block:: sh

    $ conda create --copy -n awesome-project \
      python=3 bob-devel bob-extras
    # bob-devel has all of our dependencies but no bob packages themselves and
    # bob-extras has all of our bob packages.
    $ source activate awesome-project

* Create a folder with the following buildout configuration file.

.. code-block:: sh

    $ mkdir awesome-project
    $ cd awesome-project
    $ vi buildout.cfg

.. code-block:: guess

    [buildout]
    parts = scripts

    extensions = bob.buildout
                 mr.developer

    newest = false
    verbose = true
    debug = false

    auto-checkout = *

    develop = src/bob.extension
              src/bob.blitz

    eggs = bob.extension
           bob.blitz

    [scripts]
    recipe = bob.buildout:scripts
    dependent-scripts = true

    [sources]
    bob.extension = git https://gitlab.idiap.ch/bob/bob.extension
    bob.blitz = git https://gitlab.idiap.ch/bob/bob.blitz
    ; or
    ; bob.extension = git git@gitlab.idiap.ch:bob/bob.extension.git
    ; bob.blitz = git git@gitlab.idiap.ch:bob/bob.blitz.git

* Run buildout and check if your desired package is being imported from the
  ``awesome-project/src`` folder.

.. code-block:: sh

    $ buildout
    $ ./bin/python  # you should use this python to run things from now on

.. code-block:: python

    >>> import bob.blitz
    >>> bob.blitz # should print from '.../awesome-project/src/bob.blitz/...'
    <module 'bob.blitz' from 'awesome-project/src/bob.blitz/bob/blitz/__init__.py'>
    >>> print(bob.blitz.get_config())
    bob.blitz: 2.0.15b0 [api=0x0202] (awesome-project/src/bob.blitz)
    * C/C++ dependencies:
      - Blitz++: 0.10
      - Boost: 1.61.0
      - Compiler: {'version': '4.8.5', 'name': 'gcc'}
      - NumPy: {'abi': '0x01000009', 'api': '0x0000000A'}
      - Python: 2.7.13
    * Python dependencies:
      - bob.extension: 2.4.6b0 (awesome-project/src/bob.extension)
      - numpy: 1.12.1 (miniconda/envs/bob3py27/lib/python2.7/site-packages)
      - setuptools: 36.4.0 (miniconda/envs/bob3py27/lib/python2.7/site-packages)

Optionally:

* run nosetests (e.g. of bob.extension):

.. code-block:: sh

    $ ./bin/nosetests -sv bob.extension

* build the docs (e.g. of bob.extension):

.. code-block:: sh

    $ export BOB_DOCUMENTATION_SERVER="https://www.idiap.ch/software/bob/docs/bob/%(name)s/master/"
    # or with private docs also available at Idiap. Ask for its path from colleagues.
    $ export BOB_DOCUMENTATION_SERVER="https://www.idiap.ch/software/bob/docs/bob/%(name)s/master/|http://path/to/private/docs/bob/%(name)s/master/"
    $ cd src/bob.extension
    $ ../../bin/sphinx-build -aEn doc sphinx  # make sure it finishes without warnings.
    $ firefox sphinx/index.html  # view the docs.


.. bob.extension.development_setup:

Local development environment
------------------------------

The first thing that you want to do is setup your local development
environment so you can start developing. Thanks to conda_ this is quite easy.
Here are the instructions:

* Install conda_ and learn about it a bit.
* Add our `conda channel`_ to your channels.

.. code-block:: sh

    $ conda config --set show_channel_urls True
    $ conda config --add channels defaults
    $ conda config --add channels https://www.idiap.ch/software/bob/conda

.. note::

    Make sure you are using **only** our channel (with the highest priority)
    and ``defaults`` (with the second highest priority). If you use any other
    channel like ``conda-forge``, you may end-up with broken environments.
    To see which channels you are using run:

    .. code-block:: sh

        $ conda config --get channels

* Create a new environment that you will use for development.

.. note::

    We recommend creating a new conda_ environment for every project or task
    that you work on. This way you can have several isolated development
    environments which can be very different form each other.

.. code-block:: sh

    $ conda create --copy -n awesome-project \
      python=3 bob-devel
    $ source activate awesome-project

.. note::

    The ``--copy`` option in the ``conda create`` command copies all files from
    conda's cache folder into your environment. If you don't provide it, it
    will try to create hard links to save up disk space but you will risk
    modifying the files in **all** your environments without knowing. This can
    easily happen if you use pip_ for example to manage your environment.

That's it. Now you have an **isolated** conda environment for your awesome
project! bob-devel_ is a conda meta package that pulls a set of common software
into your environment. To see what is installed, run:

.. code-block:: sh

    $ conda list

You can use conda_ and zc.buildout_ (which we will talk about later) to install
some other libraries that you may require into your environment.

.. important::

    Installing bob-devel_ **will not** install any |project| package. Use
    conda_ to install the |project| packages that you require. For example to
    get all the **core** `Bob packages`_ installed, run:

    .. code-block:: sh

        $ conda install bob

One important advantage of using conda_ and zc.buildout_ is that it does
**not** require administrator privileges for setting up any of the above.
Furthermore, you will be able to create distributable environments for each
project you have. This is a great way to release code for laboratory exercises
or for a particular publication that depends on |project|.

.. _bob.extension.build_locally:

Building packages locally
-------------------------

To be able to develop a package, we first need to build and install it locally.
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
default, is stored in a file called ``buildout.cfg``. Let\'s create an example
one in your project folder that will allow you to develop ``bob.extension``
from source:

.. code-block:: sh

    $ mkdir awesome-project
    $ cd awesome-project
    # checkout bob.extension from source and put it in a folder called `src`
    $ git clone https://gitlab.idiap.ch/bob/bob.extension src/bob.extension

Create a file named ``buildout.cfg`` in the ``awesome-project`` folder with the
following contents:

.. code-block:: guess

    [buildout]
    parts = scripts
    extensions = bob.buildout
    newest = false
    verbose = true
    debug = false

    develop = src/bob.extension
    eggs = bob.extension

    [scripts]
    recipe = bob.buildout:scripts
    dependent-scripts = true

Then, invoke buildout:

.. code-block:: sh

    $ buildout

.. note::

    Buildout by default looks for ``buildout.cfg`` in your current folder and
    uses that configuration file. You can specify a different config file with
    the ``-c`` option:

    .. code:: sh

        $ buildout -c develop.cfg

The buildout command with the configuration file above will install
``bob.extension`` in *development mode* in your local buildout environment.

.. important::
    Once ``buildout`` runs, it creates several executable scripts in a local
    ``bin`` folder. Each executable is programmed to use Python from the conda
    environment, but also to consider (prioritarily) your package checkout.
    This means that you need to use the scripts from the ``bin`` folder instead
    of using its equivalence from your conda environment. For example, use
    ``./bin/python`` instead of ``python``.

``buildout`` will examine the ``setup.py`` file of packages using setuptools_
and will ensure all build and run-time dependencies of packages are available
either through the conda installation or it will install them locally without
changing your conda environment.

The configuration file is organized in several *sections*, which are indicated
by ``[]``, where the default section ``[buildout]`` is always required. Some of
the entries need attention.

* The first entry are the ``eggs``. In there, you can list all python packages
  that should be installed. These packages will then be available to be used in
  your environment. Dependencies for those packages will be automatically
  managed, **as long as you keep** ``bob.buildout`` **in your list of**
  ``extensions``. At least, the current package needs to be in the ``eggs``
  list.

* The ``extensions`` list includes all extensions that are required in the
  buildout process. By default, only ``bob.buildout`` is required, but more
  extensions can be added (more on that later).

* The next entry is the ``develop`` list. These packages will be installed
  *development mode* from the specified folder.

The remaining options define how the (dependent) packages are built. For
example, the ``debug`` flag defined, how the :ref:`C++ code <extension-c++>` in
all the (dependent) packages is built. The ``verbose`` options handles the
verbosity of the build. When the ``newest`` flag is set to ``true``, buildout
will install all packages in the latest versions, even if an older version is
already available.

.. note::

    We normally set ``newest = False`` to avoid downloading already installed
    dependencies. Also, it installs by default the latest stable version of the
    package, unless ``prefer-final = False``, in which case the latest
    available on PyPI, including betas, will be installed.


.. warning::

    Compiling packages in debug mode (``debug = true``) will make them very
    slow. You should only use this option when you are developing and not for
    running experiments or production.

When the buildout command is invoked it will perform the following steps:

1. It goes through the list of ``eggs``, searched for according packages and
   installed them *locally*.
2. It  populates the ``./bin`` directory with all the ``console_scripts`` that
   you have specified in the ``setup.py``.

.. important::

    One thing to note in package development is that when you change the entry
    points in ``setup.py`` of a package, you need to run ``buildout`` again.


.. _bob.extension.mr.developer:

Using mr.developer
==================

One extension that may be useful is `mr.developer`_. It allows to develop
*several packages* at the same time. This extension will allow
buildout to automatically check out packages from git repositories, and places
them into the ``./src`` directory. It can be simply set up by adding
``mr.developer`` to the extensions section.

In this case, the develop section should be augmented with the packages you
would like to develop. There, you can list directories that contain Python
packages, which will be build in exactly the order that you specified. With
this option, you can tell buildout particularly, in which directories it should
look for some packages.

.. code-block:: guess

    [buildout]
    parts = scripts

    extensions = bob.buildout
                 mr.developer

    newest = false
    verbose = true
    debug = false

    auto-checkout = *

    develop = src/bob.extension
              src/bob.blitz

    eggs = bob.extension
           bob.blitz

    [scripts]
    recipe = bob.buildout:scripts
    dependent-scripts = true

    [sources]
    bob.extension = git https://gitlab.idiap.ch/bob/bob.extension
    bob.blitz = git https://gitlab.idiap.ch/bob/bob.blitz

A new section called ``[sources]`` appears, where the package information for
`mr.developer`_ is initialized. For more details, please read `its
documentation <https://pypi.python.org/pypi/mr.developer>`_. mr.developer does
not automatically place the packages into the ``develop`` list (and neither in
the ``eggs``), so you have to do that yourself.

With this augmented ``buildout.cfg``, the ``buildout`` command will perform the
following steps:



1.  It checks out the packages that you specified using ``mr.developer``.

2.  It develops all packages in the ``develop`` section
    (it links the source of the packages to your local environment).

3.  It will go through the list of ``eggs`` and search for according packages
    in the following order:

    #. In one of the already developed directories.
    #. In the python environment, e.g., packages installed with ``pip``.
    #. Online, i.e. on PyPI_.

4.  It will populate the ``./bin`` directory with all the ``console_scripts``
    that you have specified in the ``setup.py``. In our example, this is
    ``./bin/bob_new_version.py``.

The order of packages that you list in ``eggs`` and ``develop`` are important
and dependencies should be listed first. Especially, when you want to use a
private package and which not available through `pypi`_. If you do not specify
them in order, you might face with some errors like this::

   Could not find index page for 'a.bob.package' (maybe misspelled?)

If you see such errors, you may need to add the missing package to ``eggs`` and
``develop`` and ``sources`` (**of course, respecting the order of
dependencies**).


Your local environment
======================

After buildout has finished, you should now be able to execute
``./bin/python``. When using the newly generated ``./bin/python`` script, you
can access all packages that you have developed, including your own package:

.. code-block:: sh

    $ ./bin/python

.. code-block:: python

    >>> import bob.blitz
    >>> bob.blitz # should print from '.../awesome-project/src/bob.blitz/...'
    <module 'bob.blitz' from 'awesome-project/src/bob.blitz/bob/blitz/__init__.py'>
    >>> print(bob.blitz.get_config())
    bob.blitz: 2.0.15b0 [api=0x0202] (awesome-project/src/bob.blitz)
    * C/C++ dependencies:
      - Blitz++: 0.10
      - Boost: 1.61.0
      - Compiler: {'version': '4.8.5', 'name': 'gcc'}
      - NumPy: {'abi': '0x01000009', 'api': '0x0000000A'}
      - Python: 2.7.13
    * Python dependencies:
      - bob.extension: 2.4.6b0 (awesome-project/src/bob.extension)
      - numpy: 1.12.1 (miniconda/envs/bob3py27/lib/python2.7/site-packages)
      - setuptools: 36.4.0 (miniconda/envs/bob3py27/lib/python2.7/site-packages)


Everything is now setup for you to continue the development of the packages.
Moreover, you can learn more about |project| packages and learn to create new
ones in :doc:`pure_python`.

.. include:: links.rst
