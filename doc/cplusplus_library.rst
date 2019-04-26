.. vim: set fileencoding=utf-8 :

===============================
C/C++ libraries in your package
===============================

Typically, |project|'s core packages include both a pure C++ library as well as Python bindings for the C++ code.

If you want to provide a library with pure C++ code in your package as well,
you can use the :py:class:`bob.extension.Library` class.  It will automatically
compile your C/C++ code using `CMake <http://www.cmake.org>`_ into a shared
library that you can link to your own C/C++-Python bindings, as well as in the
C++ code of other C++/Python packages. Again, a complete example can be
downloaded via:

.. code-block:: sh

  $ git clone https://gitlab.idiap.ch/bob/bob.extension.git
  $ cp -R bob.extension/bob/extension/data/bob.example.extension ./
  $ rm -rf bob.extension # optionally remove the cloned source of bob.extension
  $ cd bob.example.extension


-----------------------
Setting up your package
-----------------------

If you would like to generate a Library out of your C++ code, simply add it in the list of ``ext_modules``:

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

.. note::
   You can also export a library without bindings, for it to be used in other C++/Python packages.


---------------------
Building your package
---------------------

As shown above, to compile your C++ Python bindings and the pure C++ libraries, you can follow the simple instructions:

.. code-block:: sh

  $ buildout
  ...

This will automatically check out all required ``bob_packages`` and compile them locally.
Afterwards, the C++ code from this package will be compiled, using a newly created ``build`` directory for temporary output.
After compilation, this directory can be safely removed (re-compiling will re-create it).

To get the source code compiled using another build directory, you can define a ``BOB_BUILD_DIRECTORY`` environment variable, e.g.:

.. code-block:: sh

  $ BOB_BUILD_DIRECTORY=/tmp/build_bob buildout
  ...

The C++ code of this package, **and the code of all other** ``bob_packages`` will be compiled using the selected directory.
Again, after compilation this directory can be safely removed.

Another environment variable enables parallel compilation of C or C++ code.
Use ``BOB_BUILD_PARALLEL=X`` (where ``X`` is the number of parallel processes you want) to enable parallel building.

.. note::
   For macOS-based builds, you may need to setup additional environment
   variables **before** successfully building libraries.  Refer to the section
   :ref:`extension-c++` for details.
