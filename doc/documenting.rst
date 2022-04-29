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

.. include:: links.rst
