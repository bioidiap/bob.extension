.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Mon Oct 13 16:57:44 CEST 2014

.. _extension-c++:

==================================
 Extending Python with C/C++ code
==================================

|project| massively relies on a mixture between the user-friendly and easy-to-develop Python interface, and a fast implementation of identified bottlenecks using C++.
Typically, |project|'s packages include both a pure C++ library, which can be included and linked in pure C++ code, as well as Python bindings for the C++ code.
Sometimes, even a C-API for the python bindings is available.
But, let's go step by step...

C or C++/Python Packages
------------------------

Creating C++/Python bindings should be rather straightforward.
Only few adaptations need to be performed to get the C/C++ code being compiled and added as an extension.
For simplicity, we created an example package that includes a simple example of a C++ extension.
You can check it out by:

.. code-block:: sh

  $ wget https://gitlab.idiap.ch/bo/bob.extension/raw/master/examples/bob.example.extension.tar.bz2
  $ tar -xjf bob.example.extension.tar.bz2
  $ cd bob.example.extension

One difference to pure Python packages is that now an additional file ``requirements.txt`` can be found in the root directory of the package.
In this file, all packages that are **directly** required to compile the C/C++ code in your package are listed.
For our example, this is only the ``bob.blitz`` package.
**Indirectly** required packages will be downloaded and installed automatically.

The second big difference comes in the ``setup.py``.
To be able to import ``bob.extension`` and ``bob.blitz`` in the setup.py, we need to include some code:

.. code-block:: python

  setup_packages = ['bob.extension', 'bob.blitz']
  bob_packages = []

  from setuptools import setup, find_packages, dist
  dist.Distribution(dict(setup_requires = setup_packages + bob_packages))

We keep the ``setup_packages`` and ``bob_packages`` in separate variables since we will need them later.
The ``bob_packages`` contain a list of bob packages that this extension **directly** depends on.
In our example, we only depend on ``bob.blitz``, and we can leave the list empty.

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
      Extension("bob.example.extension._library",
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

These modifications will allow you to compile extensions that are linked against our core Python-C++ bridge ``bob.blitz`` (be default).
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

Other modules and options can be set manually using `the standard options for Python extensions <http://docs.python.org/2/extending/building.html>`_.

Most of the bob packages come with pure C++ code and Python bindings, where we commonly use the `Python C-API <https://docs.python.org/2/extending/index.html>`_ for the bindings.
When your library compiles and links against the pure C++ code, you can simply use the ``bob_packages`` as above.
This will automatically add the desired include and library directories, as well as the libraries and the required preprocessor options.

.. note::
   Usually we provide one extension ``version`` that deals with versioning.
   One example of such a ``version`` extension can be found in our example.

In our example, we have defined a small C++ function, which also shows the basic bridge between ``numpy.ndarray`` and our C++ pendant ``Blitz++``.
Basically, there are two C++ files for our extension.
``bob/example/extension/Function.cpp`` contains the pure C++ implementation of the function.
In ``bob/example/extension/main.cpp``, we define the Python bindings to that function, including the creation of a complete Python module called ``_library``.
Additionally, we give a short example of how to use our documentation classes provided in this module (see below for more details).
Finally, the function ``reverse`` from the module ``_library`` is imported into our module in the ``bob/example/extension/__init__.py`` file.

.. note::
   In the bindings of the ``reverse`` function in ``bob/example/extension/main.cpp``, we make use of some C++ defines that makes the life easier.

   1. We use a :c:macro:`BOB_TRY` and :c:macro:`BOB_CATCH_FUNCTION` block around the function call, as explained in :ref:`helpers`.

      .. warning::
         By choosing ``debug = true`` in your ``buildout.cfg`` (which is the **default**, see below), the :ref:`C++ exception handling <helpers>` will be disabled (in order to support debuggers like ``gdb`` or ``gdb-python`` to handle these exceptions properly).
         This will result in any C++ exception to be handled by the default C++ exception handler, which reports the exception in the console and stop the program (including any running python shells).

   2. We use a :cpp:class:`bob::extension::FunctionDoc` to generate a proper function documentation in Python, as explained in :ref:`docs`.



To compile your C++ Python bindings and the pure C++ libraries, you can follow the same instructions as shown above:

.. code-block:: sh

  $ python bootstrap-buildout.py
  ...
  $ ./bin/buildout
  ...

.. note::
   By default, we compile the source code (of this and **all dependent packages**, both the ones installed as ``eggs``, and the ones developed using ``mr.developer``) in debug mode.
   If you want to change that, switch the according flag in the ``buildout.cfg`` to ``debug = False``, and the compilation will be done with optimization flags and C++ exception handling enabled.


Now, we can use the script ``./bin/reverse.py`` (that we have registered in the ``setup.py``) to reverse a list of floats, using the C++ implementation of the ``reverse`` function:

.. code-block:: sh

  $ ./bin/reverse.py 1 2 3 4 5
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


Pure C/C++ Libraries Inside your Package
----------------------------------------

If you want to provide a library with pure C++ code in your package as well, you can use the :py:class:`bob.extension.Library` class.
It will automatically compile your C/C++ code using `CMake <http://www.cmake.org>`_ into a shared library that you can import in your own C/C++-Python bindings, as well as in other packages.
Again, a complete example can be downloaded via:

.. code-block:: sh

  $ wget https://gitlab.idiap.ch/bob/bob.extension/raw/master/examples/bob.example.library.tar.bz2
  $ tar -xjf bob.example.library.tar.bz2
  $ cd bob.example.library

To generate a Library, simply add it in the list of ``ext_modules``:

.. code-block:: python

  ...
  # import the Extension and Library classes and the build_ext function from bob.blitz
  from bob.blitz.extension import Extension, Library, build_ext
  ...

  setup(

    ext_modules = [
      # declare a pure C/C++ library just the same way as an extension
      Library("bob.example.library.bob_example_library",
        # list of pure C/C++ files compiled into this library
        [
          "bob/example/library/cpp/Function.cpp",
        ],
        version = version,
        bob_packages = bob_packages,
      ),
      # all other extensions will automatically link against the Library defined above
      Extension("bob.example.library._library",
        # list of files compiled into this extension
        [
          # the Python bindings
          "bob/example/library/main.cpp",
        ],
        version = version,
        bob_packages = bob_packages,
      ),
      ... #add more Extensions if you wish
    ],

    cmdclass = {
      'build_ext': build_ext
    },

    ...
  )

Again, we use the overloaded library class
:py:class:`bob.blitz.extension.Library` instead of the
:py:class:`bob.extension.Library`, but the parameters are identical, and
identical to the ones of the :py:class:`bob.extension.Extension`.  To avoid
later complications, you should follow the guidelines for libraries in bob
packages:

1. The name of the C++ library need to be identical to the name of your package (replacing the '.' by '_').
   Also, the package name need to be part of it.
   For example, to create a library for the ``bob.example.library`` package, it should be called ``bob.example.library.bob_example_library``.
   In this way it is assured that the libraries are found by the ``bob_packages`` parameter (see above).

2. All header files that your C++ library should export need to be placed in the directory ``bob/example/library/include/bob.example.library``.
   Again, this is the default directory, where the ``bob_packages`` expect the includes to be.
   This is also the directory that is added to your own library and to your extensions, so you don't need to specify that by hand.

3. The include directory should contain a ``config.h`` file, which contains C/C++ preprocessor directives that contains the current version of your C/C++ API.
   With this, we make sure that the version of the library that is linked into other packages is the expected one.
   One such file is again given in our ``bob.example.library`` example.

4. To avoid conflicts with other functions, you should put all your exported C++ functions into an appropriate namespace.
   In our example, this should be something like ``bob::example::library``.

The newly generated Library will be automatically linked to **all other** Extensions in the package.
No worries, if the library is not used in the extension, the linker should be able to figure that out...

.. note:
  The clang linker seems not to be smart enough to detect unused libraries...

You can also export your Python bindings to be used in other libraries.
Unfortunately, this is an extremely tedious process and is not explained in detail here.
As an example, you might want (or maybe not) to have a look into `bob.blitz/bob/blitz/include/bob.blitz/capi.h <https://gitlab.idiap.ch/bob/bob.blitz/blob/master/bob/blitz/include/bob.blitz/capi.h>`_.


Compiling your Library and Extension
------------------------------------

As shown above, to compile your C++ Python bindings and the pure C++ libraries, you can follow the simple instructions:

.. code-block:: sh

  $ python bootstrap-buildout.py
  ...
  $ ./bin/buildout
  ...

This will automatically check out all required ``bob_packages`` and compile them locally.
Afterwards, the C++ code from this package will be compiled, using a newly created ``build`` directory for temporary output.
After compilation, this directory can be safely removed (re-compiling will re-create it).

To get the source code compiled using another build directory, you can define a ``BOB_BUILD_DIRECTORY`` environment variable, e.g.:

.. code-block:: sh

  $ python bootstrap-buildout.py
  ...
  $ BOB_BUILD_DIRECTORY=/tmp/build_bob ./bin/buildout
  ...

The C++ code of this package, **and the code of all other** ``bob_packages`` will be compiled using the selected directory.
Again, after compilation this directory can be safely removed.

.. note::
   For Idiapers, the :ref:`Note from above <idiap_note>` applies again.

Another environment variable enables parallel compilation of C or C++ code.
Use ``BOB_BUILD_PARALLEL=X`` (where ``X`` is the number of parallel processes you want) to enable parallel building.

.. _docs:

Documenting your C/C++ Python Extension
---------------------------------------

One part of this package are some functions that makes it easy to generate a proper Python documentation for your bound C/C++ functions.
For the API documentation of the package, please read :ref:`cpp_api`.
One example for a function documentation can be found in the file ``bob/example/library/main.cpp``, which you have downloaded above.
This documentation can be used after:

.. code-block:: c++

   #include <bob.extension/documentation.h>

Function documentation
++++++++++++++++++++++

To generate a properly aligned function documentation, you can use the :cpp:class:`bob::extension::FunctionDoc`:

.. code-block:: c++

   bob::extension::FunctionDoc description(
     "function_name",
     "Short function description",
     "Optional long function description"
   );


.. note::

   If you want to document a member function of a class, you should use set fourth boolean option to true.
   This is required since the default Python class member documentation is indented four more spaces, which we need to balance:

   .. code-block:: c++

      bob::extension::FunctionDoc member_function_description(
        "function_name",
        "Short function description",
        "Optional long function description",
        true
      );

Using this object, you can add several parts of the function that need documentation:

1. ``description.add_prototype("variable1, variable2", "return1, return2");`` can be used to add function definitions (i.e., ways how to use your function).
   This function needs to be called at least once.
   If the function does not define a return value, it can be left out (in which case the default ``"None"`` is used).

2. ``description.add_parameter("variable1, variable2", "datatype", "Variable description");`` should be defined for each variable that you have used in the prototypes.

3. ``description.add_return("return1", "datatype", "Return value description");`` should be defined for each return value that you have used in the prototypes.

.. note::

   All these functions return a reference to the object, so that you can use them in line, e.g.:

   .. code-block:: c++

      static auto description = bob::extension::FunctionDoc(...)
        .add_prototype(...)
        .add_parameter(...)
        .add_return(...)
      ;

A complete working exemplary function documentation from the ``reverse`` function in ``bob.example.library`` package would look like this:

.. code-block:: c++

   static bob::extension::FunctionDoc reverse_doc = bob::extension::FunctionDoc(
     "reverse",
     "This is a simple example of bridging between blitz arrays (C++) and numpy.ndarrays (Python)",
     "Detailed documentation of the function goes here."
   )
   .add_prototype("array", "reversed")
   .add_parameter("array", "array_like (1D, float)", "The array to reverse")
   .add_return("reversed", "array_like (1D, float)", "A copy of the ``array`` with reversed order of entries")
   ;

Finally, when binding you function, you can use:

a. ``description.name()`` to get the name of the function

b. ``description.doc()`` to get the aligned documentation of the function, properly indented and broken at 80 characters (by default).
   This call will check that all parameters and return values are documented, and add a ``.. todo::`` directive if not.

c. ``description.kwlist(index)`` to get the list of keyword arguments for the given prototype ``index`` that can be passed as the ``keywords`` parameter to the :c:func:`PyArg_ParseTupleAndKeywords` function.

which can be used during the binding of the function.
In our example, it would look like:

.. code-block:: c++

   PyMethodDef methods[] = {
    ...
     {
       reverse_doc.name(),
       (PyCFunction)PyBobExampleLibrary_Reverse,
       METH_VARARGS|METH_KEYWORDS,
       reverse_doc.doc()
     },
     ...
     {NULL}  // Sentinel
   };


Sphinx directives like ``.. note::``, ``.. warning::`` or ``.. math::`` will be automatically detected and aligned, when they are used as one-line directive, e.g.:

.. code-block:: c++

   "(more text)\n\n.. note:: This is a note\n\n(more text)"

Also, enumerations and listings (using the ``*`` character to define a list element) are handled automatically:

.. code-block:: c++

   "(more text)\n\n* Point 1\n* Point 2\n\n(more text)"

.. note::

   Please assure that directives are surrounded by double ``\n`` characters (see example above) so that they are put as paragraphs.
   Otherwise, they will not be displayed correctly.

.. note::

   The ``.. todo::`` directive seems not to like being broken at 80 characters.
   If you want to use ``.. todo::``, please call, e.g., ``description.doc(10000)`` to avoid line breaking.

.. note::

   To increase readability, you might want to split your documentation lines, e.g.:

   .. code-block:: c++

      "(more text)\n"
      "\n"
      "* Point 1\n"
      "* Point 2\n"
      "\n"
      "(more text)"

Leading white-spaces in the documentation string are handled correctly, so you can use several layers of indentation.

**Class documentation**
+++++++++++++++++++++++

To document a bound class, you can use the :cpp:class:`bob::extension::ClassDoc` to align and wrap your documentation.
Again, during binding you can use the functions ``description.name()`` and ``description.doc()`` as above.

Additionally, the class documentation has a function to add constructor definitions, which takes an :cpp:class:`bob::extension::FunctionDoc` object.
The shortest way to get a proper class documentation is:

.. code-block:: c++

   auto my_class_doc =
     bob::extension::ClassDoc("class_name", "Short description", "Long Description")
       .add_constructor(
         bob::extension::FunctionDoc("class_name", "Constructor Description")
          .add_prototype("param1", "")
          .add_parameter("param1", "type1", "Description of param1")
       )
   ;

.. note::

   The second parameter ``""`` in ``add_prototype`` prevents the output type (which otherwise defaults to ``"None"``) to be written.

.. note::

   For constructor documentations, there is no need to declare them as member functions.
   This is done automatically for you.

.. note::
   You can use the :cpp:func:`bob::extension::ClassDoc::kwlist` function to retrieve the ``kwlist`` of the constructor documentation.

Currently, the :cpp:class:`bob::extension::ClassDoc` allows to highlight member functions or variables at the beginning of the class documentation.
This highlighting is still under development and might not work as expected.


Possible speed issues
=====================

In order to speed up the loading time of the modules, you might want to reduce the amount of documentation that is generated (though I haven't experienced any speed differences).
For this purpose, just compile your bindings using the ``"-DBOB_SHORT_DOCSTRINGS"`` compiler option, e.g. by simply define an environment variable ``BOB_SHORT_DOCSTRINGS=1`` before invoking ``buildout``.

In any of these cases, only the short descriptions will be returned as the doc string.
