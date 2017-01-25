By far, the easiest and best supported installation method for Bob
packages uses `zc.buildout`_.
Using buildout requires you define a configuration file, normally named
``buildout.cfg``, which describes which packages are supposed to be
installed on the current environment. `Our custom buildout
extension <https://pypi.python.org/pypi/bob.buildout>`__ will hook-in
externally compiled software from that configuration file.

The key-idea is that for every project, you create a new environment that contains the
packages you need for the task. A project may be a product you are
working on or a research paper, for you which you will publish
reproducible results. Each environment will be isolated so there is low
risk of interference between your projects.

.. note::

    Keep this in mind: 1 task, 1 environment. Do not mix.


Using ``zc.buildout``
=====================

To start, create an empty work directory on your disk, and ``cd`` into
it:

.. code:: sh

    $ mkdir exp01
    $ cd exp01

Download a stock bootstrap script for ``zc.buildout``:

.. code:: sh

    $ wget https://bootstrap.pypa.io/bootstrap-buildout.py

Create ``buildout.cfg`` file, in the same folder as
``bootstrap-buildout.py``. The contents will depend on which Bob
packages you would like to work with, but it generally looks like this:

.. code:: ini

    [buildout]
    parts = scripts
    extensions = bob.buildout
    prefer-final = true
    ; use prefer-final = false **only** to get betas and pre-releases
    eggs = bob.io.image
           bob.learn.linear

    ; options for bob.buildout
    debug = false
    ; debug = true will compile bob packages in debug mode
    verbose = true
    ; verbose = true will make the build process more verbose
    newest = false
    ; newest = true will install the newest version of all packages

    [scripts]
    recipe = bob.buildout:scripts
    dependent-scripts = true


.. warning::

    Compiling packages in debug mode (``debug = true``) will make them very
    slow. You should only use this option when you are developing and not for
    running experiments or production.

Notice the ``eggs`` entry inside the ``buildout`` section. It defines
all python packages you will directly use on this environment. In this
case, I only need the functionality of loading image files, machines and
trainers for linear systems so, my eggs section contains only two
packages: ``bob.io.image`` and ``bob.learn.linear``. Dependencies for
those packages will be automatically managed, **as long as you keep**
``bob.buildout`` **in your list of** ``extensions``.

Now, bootstrap your new environment and instruct ``zc.buildout`` to
download and install packages (and dependencies) locally:

.. code:: sh

    $ python bootstrap-buildout.py
    $ ./bin/buildout

.. note::

    Buildout by default looks for ``buildout.cfg`` in your current folder and uses that configuration file. You can specify a different config file with the ``-c`` option:

    .. code:: sh

        $ ./bin/buildout -c develop.cfg

That is it! Once the buildout finishes, all packages have been
downloaded and installed locally. Buildout will create a ``python``
script that sets up your environment correctly so it finds the locally
installed packages. Calling it, starts a new Python interpreter with all
the prescribed functionality available. Run a test:

.. code:: sh

    $ ./bin/python
    ...
    >>> import bob.io.image
    >>> print(bob.io.image.get_config())
    ...
    >>> import bob.learn.linear
    >>> print(bob.learn.linear.get_config())
    ...


A Minimal Example
-------------------


Let's assume that `bob`_ is installed following our `Bob's installation`_
instructions. Now you want to use several other `satellite packages`_ such as
``bob.bio.spear``, ``bob.bio.gmm``, and ``bob.db.voxforge``. Here is a minimal
configuration file that will get you started:

.. code:: ini

    [buildout]
    parts = scripts
    extensions = bob.buildout
    prefer-final = true
    eggs = bob.bio.spear
           bob.bio.gmm
           bob.db.voxforge

    debug = false
    verbose = true
    newest = false

    [scripts]
    recipe = bob.buildout:scripts
    dependent-scripts = true

In most cases, only the ``eggs`` section needs to be modified.


Using mr.developer
------------------

One extension that is regularly used in most of Bob‘s packages is
`mr.developer <https://pypi.python.org/pypi/mr.developer>`__. It can be
used to automatically check out packages from git repositories, and
places them into the ./src directory. It can be simply set up:

.. code:: ini

    [buildout]
    ...

    extensions = bob.buildout
                 mr.developer

    auto-checkout = *

    ; The order that you develop things matter: dependencies should be first.
    develop = src/bob.blitz

    [sources]
    bob.blitz = git git@gitlab.idiap.ch:bob/bob.blitz
    ; You can also specify a branch
    ; bob.blitz = git git@gitlab.idiap.ch:bob/bob.blitz branch=mybranch01
    ; Note: all sources will be checked out even if they are not in "develop ="
    ; You can also develop a local package (localized in your file system)
    bob.pkg = fs bob.pkg full-path=/path/to/bob.pkg
    ...

A new section called [sources] appears, where the package information
for `mr.developer <https://pypi.python.org/pypi/mr.developer>`__ is
initialized, for more details, please read it’s documentation. Again,
mr.developer does not automatically place the packages into the
``develop`` list (and neither in the ``eggs``), so you have to do that
yourself.

.. note::

    mr.developer will not update your sources if they are already
    checkedout. If you change your sources and run ``./bin/buildout``
    again, it will not update your sources. You have to do that
    manually.


Order of packages in ``eggs`` and ``develop``
---------------------------------------------

The order of packages that you list in ``eggs`` and ``develop`` are important and dependencies should be listed first.
Especially, when you want to use a private package and is not available through `pypi`_.
For example, you want to use the ``bob.bio.vein`` package and it has a dependency on ``bob.bio.base`` which is not published on `pypi`_.
Also, ``bob.bio.base`` depends on ``bob.db.base`` which is not published on `pypi`_ either.
The correct order to add these dependencies would be:

.. code:: ini

    eggs = bob.db.base
           bob.bio.base
           bob.bio.vein
    ...
    develop = src/bob.db.base
              src/bob.bio.base
              src/bob.bio.vein

If you do not specify them in order, you might face with some errors like this::

   Could not find index page for 'bob.bio.base' (maybe misspelled?)

If you see such errors, you may need to add the missing package to ``eggs`` and ``develop`` and ``sources`` (**of course,
respecting the order of dependencies**).


Hooking-in privately compiled externals
---------------------------------------

If you have placed external libraries outside default search paths, make
sure you set the buildout ``prefixes`` variable to point to the root of
the installation paths for those. Here is an example:

.. code:: ini

    [buildout]
    parts = scripts
    extensions = bob.buildout
    eggs = bob.io.image
           bob.learn.linear
    prefixes = /path/to/my-install
               /path/to/my-other-install

    [scripts]
    recipe = bob.buildout:scripts

.. include:: links.rst
