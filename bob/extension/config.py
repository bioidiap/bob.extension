#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Functionality to implement config file parsing and loading'''

import os
import imp
import collections


RCFILENAME = '.bobrc.py'
"""Default name to be used for the RC file to load"""


def _load_module(path, variables):
  '''Loads the Python file as module, returns a proper Python module

  This function is implemented in a way that is both Python 2 and Python 3
  compatible. It does not directly load the python file, but reads its contents
  in memory before Python-compiling it. It leaves no traces on the file system.


  Parameters:

    path (str): The full path of the Python file to load the module contents
      from

    variables (dict): A mapping which indicates name -> object relationship to
      be established within the file before loading it


  Returns:

    module: A valid Python module you can use in an Algorithm or Library.

  '''

  retval = imp.new_module('config')

  # defines symbols
  for k, v in variables.items(): retval.__dict__[k] = v

  # executes the module code on the context of previously import modules
  exec(compile(open(path, "rb").read(), path, 'exec'), retval.__dict__)

  return retval


def update(d, u):
  '''Updates dictionary ``d`` with sparse values from ``u``

  This function updates the base dictionary ``d`` with values from the
  dictionary ``u``, with possible dictionary nesting. Matching keys that
  existing in ``d`` and ``u`` will be updated. Others will be added to ``d``.

  If the type of value in ``u`` is not the same as in ``d``, ``d``'s value is
  *overriden* with the new value from ``u``.

  This procedure does **not** delete any existing keys in ``d``


  Parameters:

    d (dict): Dictionary that will be updated

    u (dict): Dictionary with the updates.


  Returns:

    dict: The input dictionary ``d``, updated

  '''

  for k, v in u.items():
    if isinstance(v, collections.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      d[k] = v

  return d


def load(path=None):
  '''Loads the default configuration file, or an override if provided

  This method will load **exactly** one configuration file in this order or
  preference:

  1. The value passed in ``path``, if it exists
  2. A file named :py:attr:`RCFILENAME` on the current directory
  3. A file named :py:attr:`RCFILENAME` on your HOME directory

  This function will be available in the global context of the loaded
  configuration file. You can use it by calling ``load(path)`` to load objects
  from another configuration file.

  Parameters:

    path (:py:class:`str`, Optional): The full path of the Python file to load
      the module contents from.


  Returns:

    dict: A dictionary of key-values after loading the provided module and
    resolving all variables.

  '''

  if path is None:
    if os.path.exists(RCFILENAME):
      path = os.path.realpath(RCFILENAME)
    elif os.path.exists(os.path.expanduser('~' + os.sep + RCFILENAME)):
      path = os.path.expanduser('~' + os.sep + RCFILENAME)
  else:
    # if path is relative, make it relative to the current module
    if not os.path.isabs(path):
      import inspect
      f = inspect.currentframe().f_back
      if f.f_back is not None:
        # this is a call from another module, use that as base for relpath
        basedir = os.path.dirname(f.f_code.co_filename)
        path = os.path.join(basedir, path)

  if path is None: return {}

  # symbols that will exist (even if not imported) in every config file
  symbols = {
      'load': load,
      'update': update,
      'defaults': {},
      }

  mod = _load_module(os.path.realpath(os.path.expanduser(path)), symbols)
  retval = mod.__dict__

  # cleans-up
  for key in symbols:
    if key == 'defaults': continue
    if key in retval: del retval[key]
  for key in list(retval.keys()):
    if key.startswith('_'): del retval[key]

  return retval
