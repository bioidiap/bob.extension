#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Functionality to implement config file parsing and loading'''

import os
import imp
import copy
import logging

logger = logging.getLogger(__name__)

ENVNAME = 'BOBRC'
"""Name of environment variable to look for an alternative for the RC file"""

RCFILENAME = '.bobrc.py'
"""Default name to be used for the RC file to load"""


def _load_context(path, mod):
  '''Loads the Python file as module, returns a resolved context

  This function is implemented in a way that is both Python 2 and Python 3
  compatible. It does not directly load the python file, but reads its contents
  in memory before Python-compiling it. It leaves no traces on the file system.


  Parameters:

    path (str): The full path of the Python file to load the module contents
      from

    mod (module): A preloaded module to use as context for the next module
      loading. You can create a new module using :py:mod:`imp` as in ``m =
      imp.new_module('name'); m.__dict__.update(ctxt)`` where ``ctxt`` is a
      python dictionary with string -> object values representing the contents
      of the module to be created.


  Returns:

    module: A python module with the fully resolved context

  '''

  # executes the module code on the context of previously imported modules
  exec(compile(open(path, "rb").read(), path, 'exec'), mod.__dict__)

  return mod


def load(paths, context=None):
  '''Loads a set of configuration files, in sequence

  This method will load one or more configuration files. Everytime a
  configuration file is loaded, the context (variables) loaded from the
  previous file is made available, so the new configuration file can override
  or modify this context.

  Parameters:

    paths (:py:class:`list`): A list or iterable containing paths (relative or
      absolute) of configuration files that need to be loaded in sequence.
      Each configuration file is loaded by creating/modifying the context
      generated after each file readout.

    context (:py:class:`dict`, Optional): If passed, start the readout of the
      first configuration file with the given context. Otherwise, create a new
      internal context.


  Returns:

    dict: A dictionary of key-values representing the resolved context, after
    loading the provided modules and resolving all variables.

  '''

  mod = imp.new_module('config')
  if context is not None: mod.__dict__.update(context)

  for k in paths:
    logger.debug("Loading configuration file `%s'...", k)
    mod = _load_context(k, mod)

  # notice context.__dict__ will be gone as soon as the module is deleted
  # we need to shallow-copy it to prevent this
  return dict((k,v) for k,v in mod.__dict__.items() if not k.startswith('_'))


def _loadrc(context=None):
  '''Loads the default configuration file, or an override if provided

  This method will load **exactly** one (global) resource configuration file in
  this fixed order of preference:

  1. A path pointed by the environment variable BOBRC
  2. A file named :py:attr:`RCFILENAME` on your HOME directory


  Parameters:

    context (:py:class:`dict`, Optional): A dictionary that establishes the
      context (existing variables) in which the RC file will be loaded. By
      default, this value is set to ``None`` which indicates no previous
      context.


  Returns:

    dict: A dictionary of key-values representing the resolved context, after
    loading the provided modules and resolving all variables.

  '''

  if 'BOBRC' in os.environ:
    path = os.environ['BOBRC']
  elif os.path.exists(os.path.expanduser('~' + os.sep + RCFILENAME)):
    path = os.path.expanduser('~' + os.sep + RCFILENAME)
  else:
    logger.debug("No RC file found")
    return {}

  logger.debug("Loading RC file `%s'...", path)
  mod = imp.new_module('rc')
  if context is not None: mod.__dict__.update(context)
  return _load_context(path, mod)
