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

For more detailed instructions on how to achieve this, please see the 
guidelines on `bob.template <https://gitlab.idiap.ch/bob/bob.admin/tree/master/templates>`_.


.. include:: links.rst
