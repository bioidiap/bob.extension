.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Mon 17 Mar 09:23:45 2014 CET
..
.. Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

.. _bob.extension:

========================
 Bob Package Development 
========================

.. todolist::

This module contains information on how to build and maintain |project|
packages written in pure Python or a mix of C/C++ and Python.

.. note::
   This guide assumes that you have installed |project| following the instructions on https://www.idiap.ch/software/bob/install.

This tutorial explains how to build and distribute `Python`-based working environments for |project|.
By following these instructions you will be able to:

* Download and install |project| packages to build a local working environment.
* Install python packages to augment your virtual work environment capabilities 
* Implement your own package including either pure Python code, a mixture of C/C++ and Python code, and even pure C/C++ libraries with clean C/C++ interfaces 
* Distribute your work to others in a clean and organized manner.

These instructions heavily rely on the use of Python `distutils`_ and `zc.buildout`_.
One important advantage of using `zc.buildout`_ is that it does **not** require administrator privileges for setting up any of the above.
Furthermore, you will be able to create distributable environments for each project you have.
This is a great way to release code for laboratory exercises or for a particular publication that depends on |project|.

.. note::
  The core of our strategy is based on standard tools for *defining* and *deploying* Python packages.
  If you are not familiar with Python's ``setuptools``, ``distutils`` or PyPI, it can be beneficial to `learn about those <https://docs.python.org/distutils/>`_ before you start.
  Python's `Setuptools`_ and `Distutils`_ are mechanisms to *define and distribute* Python code in a packaged format, optionally through `PyPI`_, a web-based Python package index and distribution portal.

  `zc.buildout`_ is a tool to *deploy* Python packages locally, automatically setting up and encapsulating your work environment.


Documentation
-------------

.. toctree::
   :maxdepth: 2

   pure_python
   cplusplus
   advanced_topics
   py_api
   cpp_api
   pip

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: links.rst
