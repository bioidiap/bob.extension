====================
More advanced topics
====================


Python Package Namespace
------------------------

We like to make use of namespaces to define combined sets of functionality that go well together.
Python package namespaces are `explained in details here <http://peak.telecommunity.com/DevCenter/setuptools#namespace-package>`_ together with implementation details.
For bob packages, we usually use the ``bob`` namespace, using several sub-namespaces such as ``bob.io``, ``bob.ip``, ``bob.learn``, ``bob.db`` or (like here) ``bob.example``.


Documentation
-------------

If you intend to distribute your newly created package, please consider carefully documenting and creating unit tests for your package.
Documentation is a great starting point for users and unit tests can be used to check functionality in unexpected circumstances such as variations in package versions.

To write documentation, use the `Sphinx`_ Documentation Generator.
A template has been setup for you under the ``doc`` directory.
Get familiar with Sphinx and then unleash the writer in you.

Once you have edited both ``doc/conf.py`` and ``doc/index.rst`` you can run the documentation generator executing:

.. code-block:: sh

  $ ./bin/sphinx-build -n doc sphinx
  ...

This example generates the output of the sphinx processing in the directory ``sphinx``.
You can find more options for ``sphinx-build`` using the ``-h`` flag:

.. code-block:: sh

  $ ./bin/sphinx-build -h
  ...

.. note::

  If the code you are distributing corresponds to the work described in a publication, don't forget to mention it in your ``doc/index.rst`` file.


Unit Tests
----------

Writing unit tests is an important asset on code that needs to run in different platforms and a great way to make sure all is OK.
Test units are run with nose_.
To run the test units on your package call:

.. code-block:: sh

  $ ./bin/nosetests -sv
  bob.example.library.test.test_reverse ... ok

  ----------------------------------------------------------------------
  Ran 1 test in 0.253s

  OK


You should put additional packages needed for testing (e.g. ``nosetests``) in the ``requirements.txt`` file.

Continuous integration
----------------------

Conda recipe
------------
see ``bob.conda``

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


Release Methodology for Satellite Packages
------------------------------------------

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


Upload Additional Documentation to PythonHosted.org
---------------------------------------------------

In case you have written additional sphinx documentation in your satellite package that you want to share with the world, there is an easy way to push the documentation to `PythonHosted.org <http://pythonhosted.org>`_.
More detailed information are given `here <http://pythonhosted.org/an_example_pypi_project/buildanduploadsphinx.html>`__, which translates roughly into:

.. code-block:: sh

   $ ./bin/python setup.py build_sphinx --source-dir=doc --build-dir=build/doc --all-files
   $ ./bin/python setup.py upload_docs --upload-dir=build/doc/html

The link to the documentation will automatically be added to the PyPI page of
your package.  Usually it is a good idea to check the documentation after
building and before uploading.


Change the Version of your Satellite Package
--------------------------------------------

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

.. include:: links.rst
