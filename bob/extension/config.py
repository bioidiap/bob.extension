#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Functionality to implement python-based config file parsing and loading.
'''

import imp
import logging

logger = logging.getLogger(__name__)


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
  if context is not None:
    mod.__dict__.update(context)

  for k in paths:
    logger.debug("Loading configuration file `%s'...", k)
    mod = _load_context(k, mod)

  return mod
