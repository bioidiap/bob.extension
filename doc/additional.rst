=========================
Additional considerations
=========================



Unit tests
----------

Writing unit tests is an important asset on code that needs to run in different platforms and a great way to make sure all is OK.
Test units are run with nose_.
To run the test units on your package call:

.. code-block:: sh

  $ ./bin/nosetests -v
  bob.example.library.test.test_reverse ... ok

  ----------------------------------------------------------------------
  Ran 1 test in 0.253s

  OK

This example shows the results of the tests in the ``bob.example.project`` package. Ideally, you should
write test units for each function of your package ...

.. note::

   You should put additional packages needed for testing (e.g. ``nosetests``)
   in the ``test-requirements.txt`` file.


Continuous integration (CI)
---------------------------

.. note::

   This is valid for people at Idiap (or external bob contributors with access to Idiap's gitlab)

.. note::

   Before going into CI, you should make sure that your pacakge has a gitlab repository.
   If not, do the following in your package root folder:

   .. code-block:: sh

      $ git init
      $ git remote add origin git@gitlab.idiap.ch:bob/`basename $(pwd)`
      $ git add bob/ buildout.cfg COPYING doc/ MANIFEST.IN README.rst requirements.txt setup.py version.txt
      $ git commit -m '[Initial commit]'
      $ git push -u origin master


Copy the appropriate yml template for the CI builds:


.. code-block:: sh

  # for pure python
  $ curl -k --silent https://gitlab.idiap.ch/bob/bob.admin/raw/master/templates/ci-for-python-only.yml > .gitlab-ci.yml
  # for c/c++ extensions
  $ curl -k --silent https://gitlab.idiap.ch/bob/bob.admin/raw/master/templates/ci-for-cxx-extensions.yml | tr -d '\r' > .gitlab-ci.yml

Add the file to git:

.. code-block:: sh

  $ git add .gitlab-ci.yml


The ci file should work out of the box. It is long-ish, but generic to any
package in the system.

You also need to enable the following options - through gitlab - on your project:

1. In the project "Settings" page, make sure builds are enabled
2. If you have a private project, check the package settings and make sure that
   the "Deploy Keys" for our builders (all `conda-*` related servers) are
   enabled
3. Visit the "Runners" section of your package settings and enable all conda
   runners, for linux and macosx variants
4. Go into the "Variables" section of your package setup and **add common
   variables** corresponding to the usernames and passwords for uploading
   wheels and documentation tar balls to our (web DAV) server, as well as PyPI
   packages.  You can copy required values from [the "Variables" section of
   bob.admin](https://gitlab.idiap.ch/bob/bob.admin/variables). N.B.: You
   **must** be logged into gitlab to access that page.
5. Make sure to **disable** the service "Build e-mails" (those are very
   annoying)
6. Setup the coverage regular expression under "CI/CD pipelines" to have the
   value `^TOTAL.*\s+(\d+\%)$`, which is adequate for figuring out the output
   of `coverage report`


Python package namespace
------------------------

We like to make use of namespaces to define combined sets of functionality that go well together.
Python package namespaces are `explained in details here <http://peak.telecommunity.com/DevCenter/setuptools#namespace-package>`_ together with implementation details.
For bob packages, we usually use the ``bob`` namespace, using several sub-namespaces such as ``bob.io``, ``bob.ip``, ``bob.learn``, ``bob.db`` or (like here) ``bob.example``.


The scripts you created should also somehow contain the namespace of the package. In our example,
the script is named ``bob_example_project_version.py``, reflecting the  namespace ``bob.example``




Distributing your work
----------------------

To distribute a package, we recommend you use PyPI_.
`Python Packaging User Guide <https://packaging.python.org/>`_ contains details
and good examples on how to achieve this.
Moreover, you can provide a conda_ package for your PyPI_ package for easier
installation. In order to create a conda_ package, you need to create a conda_
recipe for that package.

.. note::

    To ease up your life, we also provide a script to run all steps to publish
    your package. Please read the following sections to understand the steps
    in the ``./bin/bob_new_version.py`` script that will be explained at the
    end of these section.


------------
Conda recipe
------------

If you want to create a new recipe for a package, first:

#. Learn about conda_.
#. Read the official `conda build guide`_.
#. Read `conda-forge's documentation`_.
#. Read the readme of `anaconda-recipes`_.

At Idiap, we provide our own `conda channel`_ to distribute |project| packages
and some other dependencies that are not available in the ``defaults`` channel.
This channel is maintained in `bob.conda`_.

.. note::

    If you are at Idiap, every newly developed |project| package must have a
    conda_ recipe in `bob.conda`_ **before** a new version is tagged. Since our
    conda recipes pull your package source from PyPI and you only get to have a
    PyPI source *after* you tag, there is a little chicken and egg problem. Do
    not worry. To avoid this the first time you create a conda recipe for a new
    |project| package, make sure the builds are skipped for your recipe:

    .. code-block:: yaml

        build:
          skip: true

    Later when you tag a package for the first time, the CI process will
    automatically update your recipe in `bob.conda`_ to the tagged version.
    Then, you can remove the line that says ``skip: true`` to actually start
    building your package in `bob.conda`_. This is only relevant for the
    packages that are being tagged for the first time. In future, you just tag
    and your package will be uploaded to PyPI_ first and then its recipe in
    `bob.conda`_ will be updated through a merge request.


Folder structure in ``bob.conda``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are several folder inside this repository and they are organized like
this:

-  ``dependencies`` A folder to keep the recipes for packages that are
   not part of Bob.
-  ``recipes`` A folder to keep recipes for Bob packages which contain
   C/C++ code.
-  ``skeleton`` A folder to keep recipes for Bob packages that contain Pyhon
   2/3 compatible and platform-independent code. Usually this is the place that
   you want to place your recipe.
-  ``scripts`` Contains some useful scripts.

To add a new recipe, you can start by copying one of the recipes available
in ``bob.conda``. Below is some detailed information about our channel.



A few remarks
^^^^^^^^^^^^^

* Make sure you follow the pinning policies already available inside other
  packages recipes. You need to do a little searching here.
* Clearly mark your name (gitlab id) as maintainer of the recipe
* If the package has some C/C++ code, add following build and run
  requirements into ``meta.yaml``:

.. code:: yaml

    requirements:
      build:
        - toolchain 2.3.2
        - gcc 4.8.5  # [linux]
        - libgcc 4.8.5  # [linux]
      run:
        - libgcc 4.8.5  # [linux]

Testing
^^^^^^^

In order to test the recipe, you'll need to install ``conda-build`` on
your conda root environment. Make sure you have the latest available
version on your system.

.. note::

    You must install conda on your local machine. You cannot use a central
    conda instllation (like the one we provide at Idiap) for this building
    purpose.

You **should** have only these two channels on the top of your channel list:

.. code-block:: yaml

    -  https://www.idiap.ch/software/bob/conda
    -  defaults

This can be achieved with the following commands:

.. code-block:: sh

    $ conda config --add channels defaults
    $ conda config --add channels http://www.idiap.ch/software/bob/conda

Once that is done, you can try to build your new recipe with:

.. code-block:: sh

    $ CONDA_NPY=112 conda build <package>

If that works, upload your changes on this package on a branch and
create a merge request. Wait for the tests to pass on the MR and make
sure everything completes well, by inspecting the log files. If all is
good, assign the branch for merge to one of the package maintainers.

.. warning::

   You should only use the packages from the ``defaults`` channel and our
   channel. The packages from our channel **are not** co-installable with the
   packages from `conda-forge`. If you need to use a package from
   `conda-forge`, you need to first port that package to bob.conda_ first.


------------------------
Version numbering scheme
------------------------

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

--------------------------------
Release methodology for packages
--------------------------------

Here is a set of steps we recommend you follow when releasing a new version of your package:

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

   Here is an example for creating a branch at gitlab (many of our packages are hosted there).
   Let's create a branch called ``1.1``:

   .. code-block:: sh

      $ git branch 1.1
      $ git checkout 1.1
      $ git push origin 1.1

3. When you decide to release something publicly, we recommend you **tag** the version of the package on your repository, so you have a marker to what code you actually published on PyPI.
   Tagging on gitlab would go like this:

   .. code-block:: sh

      $ git tag v1.1.0
      $ git push && git push --tags

   Notice use prefix tag names with ``v``.

4. Finally, after branching and tagging, it is time for you to publish your new package on PyPI.
   When the package is ready and you have tested it, just do the following:

   .. code-block:: sh

      $ ./bin/python setup.py register #if you modified your setup.py or README.rst
      $ ./bin/python setup.py sdist --formats zip upload

   .. note::

      You can also check the .zip file that will be uploaded to PyPI before
      actually uploading it. Just call:

      .. code-block:: sh

         $ ./bin/python setup.py sdist --formats zip

      and check what was put into the ``dist`` directory.

   .. note::
      To be able to upload a package to PyPI_ you have to register at the web
      page using a user name and password.

5. Announce the update on the relevant channels.


----------------------------------
Change the version of your package
----------------------------------

In total, 5 steps need to be performed, in the right order.
These steps are:



  1. Change the value in version.txt
  2. Change links in README.rst so documentation and build tags point to the right version instead of master
  3. Commit, tag and push
  4. Change the value in version.txt to the next possible version tag (beta)

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


----------------------------
Add your package on our wiki
----------------------------

You should also add your package in the list that can be found on
`Bob packages`_.


.. include:: links.rst
