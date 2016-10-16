.. vim: set fileencoding=utf-8 :
.. Thu 04 Aug 2016 16:39:57 CEST

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.extension/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bob/bob.extension/master/index.html
.. image:: https://gitlab.idiap.ch/bob/bob.extension/badges/v2.3.3/build.svg
   :target: https://gitlab.idiap.ch/bob/bob.extension/commits/v2.3.3
.. image:: https://img.shields.io/badge/gitlab-project-0000c0.svg
   :target: https://gitlab.idiap.ch/bob/bob.extension
.. image:: http://img.shields.io/pypi/v/bob.extension.png
   :target: https://pypi.python.org/pypi/bob.extension
.. image:: http://img.shields.io/pypi/dm/bob.extension.png
   :target: https://pypi.python.org/pypi/bob.extension

===========================================
 Python/C++ Bob Extension Building Support
===========================================

This package is part of the signal-processing and machine learning toolbox
Bob_. It provides a simple mechanism for extending Bob_ by building packages
using either pure python or a mix of C++ and python.

Installation
------------

Follow our `installation`_ instructions. Then, using the Python interpreter
inside that distribution, bootstrap and buildout this package::

  $ python bootstrap-buildout.py
  $ ./bin/buildout


Contact
-------

For questions or reporting issues to this software package, contact our
development `mailing list`_.


.. Place your references here:
.. _bob: https://www.idiap.ch/software/bob
.. _installation: https://gitlab.idiap.ch/bob/bob/wikis/Installation
.. _mailing list: https://groups.google.com/forum/?fromgroups#!forum/bob-devel
