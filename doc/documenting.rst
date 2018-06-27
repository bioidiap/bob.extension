.. vim: set fileencoding=utf-8 :

.. _docs:

========================
Documenting your package
========================

If you intend to distribute your newly created package, please consider carefully documenting it. 
Documentation is an essential starting point for new users.
Undocumented code tends to be barely re-used and may end up being abandoned.

First you should have a proper README file (such as the one provided in packages previousy provided as examples). 
We made a simple, minimal ``README.rst`` template that you can get by doing:

.. code-block:: sh

  $ curl -k --silent https://gitlab.idiap.ch/bob/bob.admin/raw/master/templates/readme-template.rst > README.rst
  $ sed -i "s/<DATE>/`date`/g" README.rst
  $ sed -i "s/<PACKAGE>/`basename $(pwd)`/g" README.rst
  # example from bob.extension, don't copy verbatim!
  $ sed -i "s%<TITLE>%Python/C++ Bob Extension Building Support%g" README.rst
  $ sed -i s%<SHORTINTRO>%It provides a simple mechanism for extending Bob_ by building packages using either pure python or a mix of C++ and python.%g;" README.rst

Replace the following tags by hand if you don't like/trust the `sed` lines above:

  1. `<DATE>`: To today's date. E.g.: `Mon 08 Aug 2016 09:47:28 CEST`
  2. `<PACKAGE>`: With the name of your package. E.g.: `bob.extension`
  3. `<TITLE>`: Replace the title (and the size of the title delimiters). E.g.: `Python/C++ Bob Extension Building Support`
  4. `<SHORTINTRO>`: With a 1 or 2 lines description of your package (it is OK to
     re-use what you have in `setup.py`). E.g.: `It provides a simple mechanism
     for extending Bob_ by building packages using either pure python or a mix of
     C++ and python.`

Additional information should be made available in the documentation. 
Ideally, you should write a user's guide for your package. There are plenty of examples in the existing bob packages
- and don't hesitate to tell us (either by opening an issue on gitlab or through our mailing list) if some are missing or outdated.


Documenting Python code
-----------------------

To write documentation, use the `Sphinx`_ Documentation Generator.
Get familiar with Sphinx and then unleash the writer in you.

To automatically generate API documentation, we make use of the `Napoleon`_ Sphinx extension 
that enables Sphinx to parse both NumPy and Google style docstrings. It has been agreed
that the style used to document bob packages is the NumPy style. To get familiar on how to document your Python code, 
you can have a look on the `Napoleon`_ website (and the links within) or in existing bob packages. You can also
refer to the official `numpydoc docstring guide`_.

.. note::

   You should start by doing the following: 

   .. code-block:: sh
   
      $ curl -k --silent https://gitlab.idiap.ch/bob/bob.admin/raw/master/templates/sphinx-conf.py > doc/conf.py
      $ mkdir -pv doc/img
      $ curl -k --silent https://gitlab.idiap.ch/bob/bob.admin/raw/master/templates/logo.png > doc/img/logo.png
      $ curl -k --silent https://gitlab.idiap.ch/bob/bob.admin/raw/master/templates/favicon.ico > doc/img/favicon.ico
      $ sed -i "s/<PROJECT>/`basename $(pwd)`/g" doc/conf.py
      # the next line will work if the description in setup.py is correct.
      # Otherwise, you need to need to fix "description" in setup.py first.
      $ sed -i "s%<SHORT_DESCRIPTION>%`python setup.py --description`%g" doc/conf.py

   The new documentation configuration allows for two optional configuration text files to be placed along ``conf.py`` (on the same directory):

    + ``extra-intersphinx.txt``, which lists extra packages that should be cross-linked to the documentation (as with Sphinx's intersphinx extension.
      The format of this text file is simple: it contains the PyPI names of packages to cross-reference. One per line.
    + ``nitpick-exceptions.txt``, which lists which documentation objects to ignore (for warnings and errors).
      The format of this text file is two-column. On the first column, you should refer to Sphinx the object type, e.g. ``py:class``, 
      followed by a space and then the name of the that should be ignored. E.g.: ``bob.bio.base.Database``. 
      The file may optionally contain empty lines. Lines starting with # are ignored (so you can comment on why you're ignoring these objects). 
      Ignoring errors should be used only as a last resource. You should first try to fix the errors as best as you can, so your documentation links are properly working.


Once you have edited ``doc/index.rst`` you can run the documentation generator executing:

.. code-block:: sh

  $ ./bin/sphinx-build -n doc sphinx
  ...

This example generates the output of the sphinx processing in the directory ``sphinx``.
You can find more options for ``sphinx-build`` using the ``-h`` flag:

.. code-block:: sh

  $ ./bin/sphinx-build -h
  ...

You can now admire the result in your favorite browser:

.. code-block:: sh

  $ firefox sphinx/index.html
  ...

.. note::

  If the code you are distributing corresponds to the work described in a publication, don't forget to mention it in your ``doc/index.rst`` file.


Documenting your C/C++ Python Extension
---------------------------------------

One part of the ``bob.extension`` package consist in some functions that makes it easy to generate a proper Python documentation for your bound C/C++ functions.
For the API documentation of the package, please read :ref:`cpp_api`.

One example for a function documentation can be found in the file ``bob/example/library/main.cpp``, which you have downloaded before.
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

.. include:: links.rst
