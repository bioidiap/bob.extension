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
    bob.extension.boost
    bob.extension.build_ext
    bob.extension.check_packages
    bob.extension.CMakeListsGenerator
    bob.extension.construct_search_paths
    bob.extension.DEFAULT_PREFIXES
    bob.extension.Extension
    bob.extension.find_executable
    bob.extension.find_library
    bob.extension.generate_self_macros
    bob.extension.get_bob_libraries
    bob.extension.get_config
    bob.extension.get_full_libname
    bob.extension.Library
    bob.extension.load_bob_library
    bob.extension.normalize_requirements
    bob.extension.pkgconfig
    bob.extension.rc
    bob.extension.reorganize_isystem
    bob.extension.uniq
    bob.extension.uniq_paths
    bob.extension.download.download_file
    bob.extension.download.download_and_unzip


Utilities
^^^^^^^^^

.. autosummary::
    bob.extension.utils.egrep
    bob.extension.utils.find_file
    bob.extension.utils.find_header
    bob.extension.utils.find_packages
    bob.extension.utils.link_documentation
    bob.extension.utils.load_requirements

Configuration
^^^^^^^^^^^^^

.. autosummary::
    bob.extension.rc_config.ENVNAME
    bob.extension.rc_config.RCFILENAME
    bob.extension.config.load

Stacked Processors
^^^^^^^^^^^^^^^^^^

.. autosummary::
    bob.extension.processors.SequentialProcessor
    bob.extension.processors.ParallelProcessor

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
    :exclude-members: find_executable,find_library,uniq,uniq_paths,construct_search_paths

.. automodule:: bob.extension.download


Configuration
-------------

.. automodule:: bob.extension.rc_config

.. automodule:: bob.extension.config


Stacked Processors
------------------

.. autosummary::
    bob.extension.processors.SequentialProcessor
    bob.extension.processors.ParallelProcessor

.. automodule:: bob.extension.processors
    :special-members: __init__, __call__


Logging
-------

.. automodule:: bob.extension.log


Scripts
-------

.. automodule:: bob.extension.scripts

.. automodule:: bob.extension.scripts.click_helper
