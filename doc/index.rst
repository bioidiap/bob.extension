.. vim: set fileencoding=utf-8 :

.. _bob.extension:

========================
 Bob Package Development
========================

.. todolist::

This module contains information on how to build, maintain, and distribute Bob_
packages written in pure Python or a mix of C/C++ and Python.

By following these instructions you will be able to:

* Setup a local development environment.
* Download and install |project| packages and other software into your
  development environment.
* Implement your own package including either pure Python code, a mixture of
  C/C++ and Python code, and even pure C/C++ libraries with clean C/C++
  interfaces.

  .. note::
     If possible, you should try to develop new packages using Python only,
     since they are easier to maintain.

* Distribute your work to others in a clean and organized manner.


Documentation
-------------

.. toctree::
   :maxdepth: 2

   development
   pure_python
   cplusplus_modules
   cplusplus_library
   documenting
   additional
   rc
   framework
   py_api
   cpp_api
   pip

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: links.rst
