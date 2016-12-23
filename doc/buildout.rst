By far, the easiest and best supported installation method for Bob
packages uses `zc.buildout`_.
Using buildout requires you define a configuration file, normally named
``buildout.cfg``, which describes which packages are supposed to be
installed on the current environment. `Our custom buildout
extension <https://pypi.python.org/pypi/bob.buildout>`__ will hook-in
externally compiled software from that configuration file.

For any of the supported installation methods the key-idea is always the
same: for every project, you create a new environment that contains the
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
    prefer-final = false
    ; use prefer-final = false **only** to get betas and pre-releases
    eggs = bob.io.image
           bob.learn.linear

    ; options for bob.buildout
    debug = false
    ; debug = false will compile bob packages in release mode
    verbose = true
    newest = false
    ; newest = false to avoid re-installing new versions of packages

    [scripts]
    recipe = bob.buildout:scripts
    dependent-scripts = true

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

    you can specify a different config file with the ``-c`` option:

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

    ; the order that you develop things matter. Dependencies should be first
    develop = src/bob.blitz

    [sources]
    bob.blitz = git git@gitlab.idiap.ch:bob/bob.blitz
    ; you can also specify a branch
    ; bob.blitz = git git@gitlab.idiap.ch:bob/bob.blitz branch=mybranch01
    ; Note: all sources will be checked out even if they are not in "develop ="
    ;You can also develop a local package (localized in your file system)
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

Order of eggs, develop
----------------------

When private packages (ones that can' t be found at the PyPy) are
installed, the order in which they are listed in the eggs and develop is
important. E.g. I want to use package ``bob.bio.vein``. It has a
dependency to the ``bob.bio.db``, that isn't public yet. Whereas the
``bob.bio.db`` is dependent on the ``bob.db.biowave_test``, that for the
moment also isn't located in the PyPy. The correct order to add these
dependencies in the eggs is:

::

    eggs = bob.db.biowave_test
           bob.bio.db
           bob.bio.vein
    ...
    develop = src/bob.db.biowave_test
              src/bob.bio.db
              src/bob.bio.vein

First, the installer *gets to know* packages order in the beginning of the
list. If one would list packages in different order, lets say,
``bob.bio.vein`` first, then the installer would notice, that it has a
dependency on a package (``bob.bio.db``) which can't be found in the
PyPy and an **error** would be raised:

::

   Couldn't find index page for 'bob.bio.db' (maybe misspelled?)

If you see such errors, that means, that the ``eggs``, ``develop`` and
``sources`` needs to be appended with the missing packages (**of course,
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
