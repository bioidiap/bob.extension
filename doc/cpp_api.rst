.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Fri Oct 10 14:03:53 CEST 2014
..
.. Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

.. _helpers:

==================
 Helper utilities
==================

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

.. _cpp_api:

======================================
 C++ API of the Documentation classes
======================================

This section includes information for using the pure C++ API for the documentation classes, which can be accessed after including:

.. code-block:: c++

   # include <bob.extension/documentation.h>

The classes, which are described in more detail below, can be used to format the documentation of your C/C++ functions that are bound to Python.
Any free text that you specify to describe your functions will be interpreted as `reStructuredText <http://docutils.sourceforge.net/rst.html>`_.
Hence, it is possible to use any directives like ``.. note::``, ``.. math::``, and even links inside the documentation like ``:py:class:`` and references as ``[REF]_``.


Function Documentation
----------------------

.. cpp:class:: bob::extension::FunctionDoc

   To document a function (either a stand-alone function or a member function of a class), you should use the :cpp:class:`bob::extension::FunctionDoc`.

   .. cpp:function:: bob::extension::FunctionDoc(\
        const char* const function_name,\
        const char* const short_desctiption,\
        const char* const long_description = NULL,\
        bool is_member_function = false\
      )

      In the constructor, you specify the function name and a short description.
      If wanted, you can define a longer description as well.
      When you use this FunctionDoc to document a member function of a class, please set ``is_member_function = true``.

   .. cpp:function:: FunctionDoc clone(\
        const char* const function_name\
      )

      Returns a copy of this documentation class, where the function name is replaced by the given one.
      This is useful, when a function is bound with several names.

   .. cpp:function:: FunctionDoc& add_prototype(\
        const char* const variables,\
        const char* const return_value = "None"\
      )

      Adds a prototype of the documented function declaration to the function.
      All ``variables`` and all ``return_value``'s listed must be documented using the :cpp:func:`add_parameter` or :cpp:func:`add_return` functions.
      Only the default return value ``None`` does not need documentation.

      ``variables`` is a single string containing a comma-separated list of parameter names.
      Use ``..., [name]`` to indicate that name is ``name`` is an optional parameter.

      ``return_value`` is a single string containing a comma-separated list of return value names.
      If a single name is given, only a single value is returned, otherwise a tuple will be returned by your function.

      .. note::
         Each :cpp:class:`FunctionDoc` needs at least one prototype.
         In opposition to pure Python functions, specifying multiple prototypes is allowed here as well.


   .. cpp:function:: FunctionDoc& add_parameter(\
        const char* const parameter_name,\
        const char* const parameter_type,\
        const char* const parameter_description\
      )

      Adds a description for a given parameter.

      ``parameter_name`` must be one of the names listed in the ``variables`` of the :cpp:func:`add_prototype` function.

      ``parameter_type`` specifies the expected type of this parameter.
      You can use any free text to describe the type.
      When ``:py:class:`` directives or similar are used, they will be interpreted correctly.

      ``parameter_description`` includes free text to describe, what the parameter is used for.


   .. cpp:function:: FunctionDoc& add_return(\
        const char* const return_name,\
        const char* const return_type,\
        const char* const return_description\
      )

      Adds a description for a given return value.

      ``return_name`` must be one of the names listed as a ``return_value`` of the :cpp:func:`add_prototype` function.

      ``return_type`` specifies the type of this return value.
      You can use any free text to describe the type.
      When ``:py:class:`` directives or similar are used, they will be interpreted correctly.

      ``return_description`` includes free text to describe, what the return value contains.


   .. cpp:function:: const char* const name() const

      Returns the name of the function defined in the constructor.


   .. cpp:function:: const char* const doc(const unsigned alignment = 72, const unsigned indent = 0) const

      Generates and returns the documentation string.
      The free text in the documentation is aligned to ``alignment`` characters, by default 72, so that it can be viewed correctly inside of an 80-character Python console.
      The ``indent`` is an internal parameter and should not be changed.


   .. cpp:function:: char** kwlist(unsigned index) const

      Returns the list of keyword arguments for the given prototype index added with the :cpp:func:`add_prototype` function.
      This list is in the desired format to be passed as the ``keywords`` parameter to the :c:func:`PyArg_ParseTupleAndKeywords` function during your bindings.


   .. cpp:function:: void print_usage() const

      Prints a function usage string to console, including all information specified by the member functions above.


All functions adding information to the :cpp:class:`bob::extension::FunctionDoc` return a reference to the current object, so that you can use it inline, like:

.. code-block:: c++

   auto function_doc = bob::extension::FunctionDoc(
     "function_name",
     "Short description of the function",
     "Long description of the function using reStructuredText including directives like :py:class:`bob.blitz.array`."
   )
   .add_prototype("param1, [param2]", "ret")
   .add_parameter("param1", "int", "An int value used for ...")
   .add_parameter("param2", "float", "[Default: ``0.5``] A float value describing ...")
   .add_return("ret", ":py:class:`bob.blitz.array`", "An array ...")
   ;


During the binding of your function, you can use it, like:

.. code-block:: c++

   static PyMethodDef module_methods[] = {
     ...
     {
       function_doc.name(),
       (PyCFunction)function,
       METH_VARARGS|METH_KEYWORDS,
       function_doc.doc()
     },
     ...
   };


Variables Documentation
-----------------------

.. cpp:class:: bob::extension::VariableDoc

   To document a variable (either a stand-alone function or a member function
   of a class), you should use the :cpp:class:`bob::extension::VariableDoc`.

   .. cpp:function:: bob::extension::VariableDoc(\
        const char* const variable_name,\
        const char* const variable_type,\
        const char* const short_desctiption,\
        const char* const long_description = NULL\
      )

      In the constructor, you specify the variable name, its type and a short
      description. The structure is identical to the
      :cpp:func:`FunctionDoc::add_parameter` function. If wanted, you can
      define a longer description as well.


   .. cpp:function:: char* name() const

      Returns the name of the variable defined in the constructor.


   .. cpp:function:: char* doc(const unsigned alignment = 72) const

      Generates and returns the documentation string, which is composed of the
      information provided in the constructor. The free text in the
      documentation is aligned to ``alignment`` characters, by default 72, so
      that it can be viewed correctly inside of an 80-character Python console.


Class Documentation
-------------------

.. cpp:class:: bob::extension::ClassDoc

   To document a class including its constructor, you should use the :cpp:class:`bob::extension::ClassDoc`.

   .. cpp:function:: bob::extension::ClassDoc(\
        const char* const class_name,\
        const char* const short_desctiption,\
        const char* const long_description = NULL\
      )

      In the constructor, you specify the class name and a short description.
      If wanted, you can define a longer description as well.


   .. cpp:function:: ClassDoc& add_constructor(\
        const FunctionDoc& constructor_doc\
      )

      Adds the documentation of the constructor, which itself is a :cpp:class:`FunctionDoc`.

      .. note::
         You should specify the return value of your constructor to be ``""`` to overwrite the default value ``"None"``.

      .. note::
         A class can have only a single constructor documentation.
         Hence, this function can be called only once for each class.


   .. cpp:function:: char* name() const

      Returns the name of the class defined in the constructor.


   .. cpp:function:: char* doc(const unsigned alignment = 72) const

      Generates and returns the documentation string, which is composed of the information provided in the constructor, and the constructor documentation.
      The free text in the documentation is aligned to ``alignment`` characters, by default 72, so that it can be viewed correctly inside of an 80-character Python console.


   .. cpp:function:: char** kwlist(unsigned index) const

      Returns the list of keyword arguments of the constructor for the given prototype index added with the :cpp:func:`FunctionDoc::add_prototype` function.
      This list is in the desired format to be passed as the ``keywords`` parameter to the :c:func:`PyArg_ParseTupleAndKeywords` function during your bindings.


   .. cpp:function:: void print_usage() const

      Prints the usage of the constructor.
      See :cpp:func:`FunctionDoc::print_usage` for details.


As for functions, the :cpp:class:`bob::extension::ClassDoc` is designed to be used inline, like:

.. code-block:: c++

   auto class_doc = bob::extension::ClassDoc(
     "class_name",
     "Short description of the class",
     "Long description of the class using reStructuredText including directives like :py:class:`bob.blitz.array`."
   )
   .add_constructor(
      bob::extension::FunctionDoc(
        "class_name",
        "Short description of the constructor",
        "Long description of the constructor"
        true
      )
     .add_prototype("param1, [param2]", "")
     .add_parameter("param1", "int", "An int value used for ...")
     .add_parameter("param2", "float", "[Default: ``0.5``] A float value describing ...")
   );
