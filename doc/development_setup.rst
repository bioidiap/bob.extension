.. bob.extension.development_setup:

===============================
Local development environement
===============================

The first thing that you want to do is setup your local development
environement so you can start developing. Thanks to conda_ this is quite easy.
Here are the instrunctions:

* Install conda_ and learn about it a bit.
* Add our `conda channel`_ to your channels.

.. code-block:: sh

    $ conda config --set show_channel_urls True
    $ conda config --add channels https://www.idiap.ch/software/bob/conda

.. note::

    Make sure you are using **only** our channel (with the highest priority)
    and ``defaults`` (with the second highest priority). If you use any other
    channel like ``conda-forge``, you may end-up with broken environements.
    To see which channels you are using run:

    .. code-block:: sh

        $ conda config --get channels

* Create a new environment that you will use for development.

.. note::

    We recommend creating a new conda_ environment for every project or task
    that you work on. This way you can have several isolated development
    environments which can be very different form each other.

.. code-block:: sh

    $ mkdir awesome-project
    $ conda create --copy -p awesome-project/conda-env \
      python=3 bob-devel bob.extension
    $ source activate awesome-project/conda-env

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

.. include:: links.rst
