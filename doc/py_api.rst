.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.dos.anjos@gmail.com>
.. Sat 16 Nov 20:52:58 2013

===========
 Python API
===========

This section includes information for using the Python API of ``bob.extension``.

Summary
-------

Core Functionality
^^^^^^^^^^^^^^^^^^

.. autosummary::
    bob.extension.get_config
    bob.extension.rc
    bob.extension.rc_context
    bob.extension.download.get_file


Utilities
^^^^^^^^^

.. autosummary::
    bob.extension.utils.find_packages
    bob.extension.utils.link_documentation
    bob.extension.utils.load_requirements
    bob.extension.download.get_file
    bob.extension.download.search_file
    bob.extension.download.list_dir

Configuration
^^^^^^^^^^^^^

.. autosummary::
    bob.extension.rc_config.ENVNAME
    bob.extension.rc_config.RCFILENAME
    bob.extension.config.load

Scripts
^^^^^^^

.. autosummary::
    bob.extension.scripts.click_helper.ConfigCommand
    bob.extension.scripts.click_helper.ResourceOption
    bob.extension.scripts.click_helper.verbosity_option
    bob.extension.scripts.click_helper.bool_option
    bob.extension.scripts.click_helper.list_float_option
    bob.extension.scripts.click_helper.open_file_mode_option
    bob.extension.scripts.click_helper.AliasedGroup
    bob.extension.scripts.click_helper.log_parameters
    bob.extension.scripts.click_helper.assert_click_runner_result


Core Functionality
------------------

.. automodule:: bob.extension

Utilities
---------

.. automodule:: bob.extension.utils

.. automodule:: bob.extension.download


Configuration
-------------

.. automodule:: bob.extension.rc_config

.. automodule:: bob.extension.config


Logging
-------

.. automodule:: bob.extension.log


Scripts
-------

.. automodule:: bob.extension.scripts

.. automodule:: bob.extension.scripts.click_helper
