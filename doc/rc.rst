.. _bob.extension.rc:

=========================================
 |project|'s Global Configuration System
=========================================

|project| provides a global configuration system for users.
The configuration file is located in ``${HOME}/.bobrc``.
The path of the file can be overridden by an environment variable named
``${BOBRC}``.
This configuration can be used to customize the behavior of |project| libraries
and also to specify the location of extra data on user's computers.
For example, the extra data can be the location of the raw data of a database
that you may want to access in |project|.

The configuration file is accessible through the ``bob config`` command line::

   $ bob config --help

You can view the content of the configuration file::

   $ bob config show

You can view the content of a specific variable in the configuration file::

   $ bob config get bob.db.atnt.directory
   /home/bobuser/databases/atnt

You can change the value of a specific variable in the configuration file::

   $ bob config set bob.db.atnt.directory /home/bobuser/databases/orl_faces


The rest of this guide explains how developers of |project| packages should
take advantage of the configuration system.


For Developers
--------------

The configuration file is automatically loaded and is available as
:py:attr:`bob.extension.rc`.
It's main usage (for now) is to automatically load find where the databases
are located.
Here is an example on how the configuration system can be potentially used:

.. doctest:: rc-config

   >>> from bob.extension import rc
   >>> class AtntDatabase:
   ...     def __init__(self, original_directory=None):
   ...         if original_directory is None:
   ...             original_directory = rc['bob.db.atnt.directory']
   ...         self.original_directory = original_directory

:py:attr:`bob.extension.rc` is a dictionary which returns ``None`` for
non-existing keys so you don't have to worry about exception handling for non-
existing keys.

.. warning::

   The variables of each package **must** start with the name of package. For
   example, if the variable is used in ``bob.db.atnt``, its name should be
   ``bob.db.atnt.<name>``. This is required to avoid variable name clashes
   between hundreds of |project| package. Remember that your package is **not**
   special and **should** follow this rule.

In the documentation of your package do not explain how the configuration
system works. Just provide an example command on how the variable should be
configured::

   $ bob config set bob.db.mydatabase.directory /path/to/mydatabase

And point to this page for more information. You can point to this page using
the ``ref`` command: ``:ref:`bob.extension.rc```
