.. _bob.extension.rc:

=============================
 Global Configuration System
=============================

|project| provides a global configuration system for package variables. The
configuration file is typically located in ``${HOME}/.bobrc``. The path of the
file can be overridden by an environment variable named ``${BOBRC}``.  This
configuration file should be used to customize global variables used by
|project| libraries. One of the typical use-cases is to specify the location of
raw datasets on the user's computers.

The configuration file is accessible through the ``bob config`` command line:

.. code-block:: sh

   $ bob config --help


You can view the content of the configuration file:

.. code-block:: sh

   $ bob config show


You can view the content of a specific variable in the configuration file:


.. code-block:: sh

   $ bob config get bob.db.atnt.directory
   /home/bobuser/databases/atnt


You can change the value of a specific variable in the configuration file:

.. code-block:: sh

   $ bob config set bob.db.atnt.directory /home/bobuser/databases/orl_faces


The rest of this guide explains how developers of |project| packages can take
advantage of the configuration system on their own packages.


For Developers
--------------

The configuration file is automatically loaded and is available as
:py:attr:`bob.extension.rc`. Here is an example on how the configuration system
can be potentially used to configure the location of a raw dataset on the
user's computer:

.. doctest:: rc-config

   >>> from bob.extension import rc
   >>> class AtntDatabase:
   ...     def __init__(self, directory=rc.get('bob.db.atnt.directory')):
   ...         self.directory = directory


:py:attr:`bob.extension.rc` is a dictionary.

.. note::

   Use :py:attr:`bob.extension.rc` only to get the values of variables that you
   have no way of knowing their value. The directory of datasets is a good
   example. Unless the user specifies where the data is located, you have no
   way of knowing such information in advance. For example, using the global
   configuration system to configure the extension of files in a dataset is
   **not** appropriate. Such value is known in advance and it should not be the
   job of the user to set it.


.. warning::

   In order to avoid chaos, we **strongly recommend** the variables of each
   package start with the name of the package. For example, if the variable is
   used in ``bob.db.atnt``, its name should be ``bob.db.atnt.<name>``. This is
   required to avoid variable name clashes between hundreds of |project|
   packages.


In the documentation of your package you need **not** to explain how the
configuration system works. Just provide an example command on how the variable
should be configured. For example:

.. code-block:: sh

   $ bob config set bob.db.mydatabase.directory /path/to/mydatabase


And refer to this page for more information. You can create a link to this page
using the ``:ref:`` command like this: ``:ref:`bob.extension.rc```.
