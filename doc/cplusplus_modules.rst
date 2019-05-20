.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Mon Oct 13 16:57:44 CEST 2014

.. _extension-c++:

==============================
 C/C++ modules in your package
==============================

|project| massively relies on a mixture between the user-friendly and easy-to-develop Python interface, and a fast implementation of identified bottlenecks using C++.

Creating C++/Python bindings should be rather straightforward.
Only few adaptations need to be performed to get the C/C++ code being compiled and added as an extension.
For simplicity, we created an example package that includes a simple example of a C++ extension.
You can check it out by:

.. code-block:: sh

  $ git clone https://gitlab.idiap.ch/bob/bob.extension.git
  $ cp -R bob.extension/bob/extension/data/bob.example.extension ./
  $ rm -rf bob.extension # optionally remove the cloned source of bob.extension
  $ cd bob.example.extension


Setting up your package
-----------------------

Typically, Python extensions written in C/C++ for Bob should use a set of standard APIs allowing C++ Blitz++ Arrays to be transparently converted to Python NumPy Arrays.
The build of your package will therefore depend on, at least, two packages: (1) bob.extension (this package): will provide build instructions and resources for defining and building your extension (2) bob.blitz: will provide a bridge between pure C++ code, depending on Blitz++ Arrays and NumPy arrays.
To be able to import ``bob.extension`` and ``bob.blitz`` in the setup.py, we need to include some code:

.. code-block:: python

  setup_packages = ['bob.extension', 'bob.blitz']

  # C++ modules needed at runtime of your package
  bob_packages = []

  from setuptools import setup, find_packages, dist
  dist.Distribution(dict(setup_requires = setup_packages + bob_packages))

We keep the ``setup_packages`` and ``bob_packages`` in separate variables since we will need them later.
The ``bob_packages`` contain a list of bob packages that this extension **directly** depends on.
In our example, we only depend on ``bob.blitz``, and we can leave the list empty.

.. warning::

   ``bob.blitz`` is required in all C++/Python packages since it contains all the mechanisms
   to deal with arrays amongst other things.

As the second step, we need to add some lines in the header of the file to tell the ``setuptools`` system to compile our library with our ``Extension`` class:

.. code-block:: python

  # import the Extension class and the build_ext function from bob.blitz
  from bob.blitz.extension import Extension, build_ext

  # load the requirements.txt for additional requirements
  from bob.extension.utils import load_requirements
  build_requires = setup_packages + bob_packages + load_requirements()

In fact, we don't use the extension from :py:class:`bob.extension.Extension`, but the one from ``bob.blitz.extension``, which is a derivation of this package.
The difference is that in :py:class:`bob.blitz.extension.Extension` all header files and libraries for the ``Blitz++`` library are added.

Third, we have to add an extension using the ``Extension`` class, by listing all C/C++ files that should be compiled into the extension:

.. code-block:: python

  # read version from version.txt file
  version = open("version.txt").read().rstrip()

  setup(
    ...
    setup_requires = build_requires,
    install_requires = build_requires,
    ...
    ext_modules = [
      Extension("bob.example.extension._module",
        [
          # the pure C++ code
          "bob/example/extension/Function.cpp",
          # the Python bindings
          "bob/example/extension/main.cpp",
        ],
        version = version,
        bob_packages = bob_packages
      ),
      ... #add more extensions if you wish
    ],
    ...
  )

These modifications will allow you to compile extensions that are linked against our core Python-C++ bridge ``bob.blitz`` (by default).
You can specify any other ``pkg-config`` module and that will be linked in (for example, ``boost`` or ``opencv``) using the ``packages`` parameter.
For ``boost`` packages, you might need to define, which boost modules are required.
By default, when using boost you should at least add the ``system`` module, i.e., by:

.. code-block:: python

  setup(
    ...
    ext_modules = [
      Extension(
        ...
        packages = ['boost'],
        boost_modules = ['system'],
      ),
      ...
    ],
    ...
  )

Other modules and options can be set manually using `the standard options for Python extensions <https://docs.python.org/2/extending/building.html>`_.

When your module compiles and links against the pure C++ code, you can simply use the ``bob_packages`` to specify dependencies in your C++ code.
This will automatically add the desired include and library directories, as well as the libraries and the required preprocessor options.

In our example, we have defined a small C++ function, which also shows the basic bridge between ``numpy.ndarray`` and our C++ pendant ``Blitz++``.
Basically, there are two C++ files for our extension.
``bob/example/extension/Function.cpp`` contains the pure C++ implementation of the function.
In ``bob/example/extension/main.cpp``, we define the Python bindings to that function.
Finally, the function ``reverse`` from the module ``_library`` is imported into our module in the ``bob/example/extension/__init__.py`` file.

..
  including the creation of a complete Python module called ``_library``.
  Additionally, we give a short example of how to use our documentation classes provided in this module (see below for more details).

.. note::
   In the bindings of the ``reverse`` function in ``bob/example/extension/main.cpp``, we make use of some C++ defines that makes the life easier.
   see :ref:`helpers`


Building your package
---------------------

To compile your C++ Python bindings and the corresponding  C++ implementation,
just do:

.. code-block:: sh

  $ buildout
  ...

.. note::
   By default, we compile the source code (of this and **all dependent packages**, both the ones installed as ``eggs``, and the ones developed using ``mr.developer``) in debug mode.
   If you want to change that, switch the according flag in the ``buildout.cfg`` to ``debug = False``, and the compilation will be done with optimization flags and C++ exception handling enabled.

.. note::
   For macOS-based builds, one also needs to ensure the environment variables
   ``MACOSX_DEPLOYMENT_TARGET``, ``SDKROOT``, and ``CONDA_BUILD_SYSROOT`` are
   properly set.  This is automatically handled for conda-build based runs.  If
   you are using buildout or any other setuptools-based system (such as pip
   installs) to build your package, you should ensure that is the case with one
   of these 2 methods (more to least recommended):

   1. You set the RC variables (see: :ref:`bob.extension.rc`)
      `bob.extension.macosx_deployment_target` and
      `bob.extension.macosx_sdkroot` to suitable values.  Example:

      .. code-block:: sh

         $ bob config get bob.extension.macosx_deployment_target
         Error: The requested key `bob.extension.macosx_deployment_target` does not exist
         $ bob config set bob.extension.macosx_deployment_target "10.9"

         $ bob config get bob.extension.macosx_sdkroot
         Error: The requested key `bob.extension.macosx_sdkroot` does not exist
         $ bob config set bob.extension.macosx_sdkroot "/opt/MacOSX10.9.sdk"

      With this method you set the default for your particular machine.  It is
      the recommended way to set up such variables as those settings do not
      affect builds in other machines and are preserved across package builds,
      guaranteeing uniformity.

      Unfortunately, the variable `CONDA_BUILD_SYSROOT` must be set on the
      environment (conda will preset it otherwise).  Change your login profile
      shell or similar to add the following:

      .. code-block:: sh

         $ export CONDA_BUILD_SYSROOT="/opt/MacOSX10.9.sdk"

   2. You set the environment variables directly on the current environment.
      Example:

      .. code-block:: sh

         $ export MACOSX_DEPLOYMENT_TARGET="10.9"
         $ export SDKROOT="/opt/MacOSX10.9.sdk"
         $ export CONDA_BUILD_SYSROOT="${SDKROOT}"

      Note that this technique is the least ephemeral from all available
      options.  As soon as you leave the current environment, the variables
      will not be available anymore.

   **Precedence**: Values set on the environment have precedence over values
   set on your Bob RC configuration.

   **Compatibility**: We recommend you check our stock
   `conda_build_config.yaml` for ensuring cross-package compatibility
   (currently available through our admin package "bob.devtools").  At the time
   of writing, we use a "10.9" macOS SDK for Bob packages.  That may change in
   the future.

   **Obtaining an SDK**: We recommend `Phracker macOS SDKs available on Github
   <https://github.com/phracker/MacOSX-SDKs>`_.  Install the SDK on
   ``/opt/MacOSX<version>.sdk``.


Now, we can use the script ``./bin/bob_example_extension_reverse.py`` (that we have registered in the ``setup.py``) to reverse a list of floats, using the C++ implementation of the ``reverse`` function:

.. code-block:: sh

  $ ./bin/bob_example_extension_reverse.py 1 2 3 4 5
  [1.0, 2.0, 3.0, 4.0, 5.0] reversed is [ 5.  4.  3.  2.  1.]

We can also see that the function documentation has made it into the module, too:

.. code-block:: sh

  $ ./bin/python
  >>> import bob.example.extension
  >>> help(bob.example.extension)

and that we can list version and the dependencies of our package:

.. code-block:: sh

  >>> print (bob.example.extension.version)
  0.0.1a0
  >>> print (bob.example.extension.get_config())
  ...


.. _helpers:

Helper utilities
----------------

In the header file ``<bob.extension/defines.h>`` we have added some functions that help you to keep your code short and clean.
Particularly, we provide three preprocessor directives:

.. c:macro:: BOB_TRY

   Starts a try-catch block to protect your bound function against exceptions of any kinds (which would lead to a Python interpreter crash otherwise).

.. c:macro:: BOB_CATCH_FUNCTION(char* message, void* ret)

   Catches C++ exceptions of any kind, adds the ``message`` in case an unknown exception is caught, and returns with the given error return (which is usually 0 for normal functions or -1 for constructors and setter functions).
   This macro should be used when binding a stand-alone function, for binding class member functions, please use :c:macro:`BOB_CATCH_MEMBER`.

.. c:macro:: BOB_CATCH_MEMBER(char* message, void* ret)

   Catches C++ exceptions of any kind, adds the ``message`` in case an unknown exception is caught, and returns with the given error return (which is usually 0 for normal functions or -1 for constructors and setter functions).
   This macro should be used when binding a member function of a class, for binding stand-alone functions, please use :c:macro:`BOB_CATCH_FUNCTION`.

These preprocessor directives will catch any C++ exception that is raised inside the C/C++ code that you bind to python and translate them into proper Python exceptions.

.. warning::
   These directives will only be active in **release** mode, when compiling
   with ``debug = true``, they will not do anything.  This is in order to
   support C++ debuggers like ``gdb`` or ``gdb-python`` to be able to handle
   these exceptions.

Additionally, we added some preprocessor directives that help in the bindings:

.. c:macro:: PyBob_NumberCheck(PyObject* o)

   Checks if the given object ``o`` is a number, i.e., an int, a long, a float
   or a complex.

After including the above mentioned header, we also re-define the functions
:c:func:`PyInt_Check`, :c:func:`PyInt_AS_LONG`, :c:func:`PyString_Check` and
:c:func:`PyString_AS_STRING` (which doesn't exist in the bindings for Python3)
so that they can be used in bindings for both Python2 and Python3.
