Using pip for development
==========================

.. warning::

    This guide is not complete and not recommended. You can just skip this
    page. There are some problems when using pip and conda at the same time
    which may lead to breaking **all your conda environments**. You can look at
    the ``conda develop`` command for an alternative.

Since all |project| packages are distributed with `Setuptools`_, you can easily
develop them using pip_. Additionally, you can use conda_ to create separate
isolated environments for your different tasks.

.. note::

    Keep this in mind: 1 task, 1 environment. Do not mix.

.. note::

    This guide does not aim to duplicate the `pip's user guide`_. Please go
    through that first to make sure you are confident in using pip_ before
    continuing here.

Developing a |project| package with pip_ can be as easy as running the
following command while your current directory is the source of the package
that you want to develop:

.. code-block:: sh

    pip install -e .

This will install the current package in your Python environment in an editable
mode. You can keep changing this package at its source directory and your
changes will be immediately reflected in your environment.

.. warning::

    If you modify the contents of ``setup.py`` such as adding or removing
    console script entry points, you need to run ``pip install -e .`` again.

Developing a C++ Package
------------------------

While developing a C++ package, the same ``pip install -e .`` command can be
used to compile the package again. Also, you may want to export some debugging
flags if you want to debug the current package:

.. code-block:: sh

    export CFLAGS=$CFLAGS -O0 -g -DBOB_DEBUG -DBZ_DEBUG
    export CXXFLAGS=$CXXFLAGS -O0 -g -DBOB_DEBUG -DBZ_DEBUG
    pip install -e .

Developing Several Packages from Source
---------------------------------------

Often it is required not only to develop the current package but also to
develop several dependencies from source too. To do so, you can create a
requirements file (usually named ``requirements.txt``) and run the following
command:

.. code-block:: sh

    pip install -r requirements.txt

while the content of your ``requirements.txt`` file lists the packages that the
current package both depends on and the dependencies that you want to develop.
For example, the following ``requirements.txt`` file can be used to develop
:py:ref:`bob.io.image <bob.io.image>`, together with **all** of its direct and
indirect dependencies::

    setuptools
    -egit+https://gitlab.idiap.ch/bob/bob.extension.git#egg=bob.extension
    -egit+https://gitlab.idiap.ch/bob/bob.blitz.git#egg=bob.blitz
    -egit+https://gitlab.idiap.ch/bob/bob.core.git#egg=bob.core
    -egit+https://gitlab.idiap.ch/bob/bob.io.base.git#egg=bob.io.base
    matplotlib

However because of a limitation of pip_, you need to install the |project|
dependencies that contain C++ code both in order and one by one. This means
that ``pip install -r requirements.txt`` will not work in this case. Instead,
you can run the following command:

.. code-block:: sh

    tr '\n' '\0' < requirements.txt | xargs -0 -n 1 pip install

.. warning::

    For the ``tr '\n' '\0' < requirements.txt | xargs -0 -n 1 pip install``
    command to work, you should not have any spaces in your
    ``requirements.txt`` file (notice that ``-egit+https://...`` has no spaces)
    and your |project| dependencies should be listed in their order of
    dependencies.

.. include:: links.rst
