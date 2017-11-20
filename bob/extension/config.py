#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Functionality to implement config file parsing and loading'''

import os
import imp
import six
import collections


RCFILENAME = '.bobrc.py'
"""Default name to be used for the RC file to load"""


def _load_context(path, context):
  '''Loads the Python file as module, returns a resolved context

  This function is implemented in a way that is both Python 2 and Python 3
  compatible. It does not directly load the python file, but reads its contents
  in memory before Python-compiling it. It leaves no traces on the file system.


  Parameters:

    path (str): The full path of the Python file to load the module contents
      from

    context (dict): A mapping which indicates name -> object relationship to
      be established within the file before loading it. This dictionary
      establishes the context in which the module loading is executed, i.e.,
      previously existing variables when the readout of the new module starts.


  Returns:

    dict: A python dictionary with the new, fully resolved context.

  '''

  retval = imp.new_module('config')

  # defines symbols
  for k, v in context.items(): retval.__dict__[k] = v

  # executes the module code on the context of previously import modules
  exec(compile(open(path, "rb").read(), path, 'exec'), retval.__dict__)

  # notice retval.__dict__ is deleted when we return
  return dict([(k,v) for k,v in retval.__dict__.items() if not k.startswith('_')])


def load(path, context=None):
  '''Loads a set of configuration files, in sequence

  This method will load one or more configuration files. Everytime a
  configuration file is loaded, the context (variables) loaded from the
  previous file is made available, so the new configuration file can override
  or modify this context.

  Parameters:

    path (:py:class:`str`, :py:class:`list`): The full path of the Python file
      to load the module contents from. If an iterable is passed, then it is
      iterated and each configuration file is loaded by creating/modifying the
      context generated after each file readout.

    context (:py:class:`dict`, Optional): If passed, start the readout of the
      first configuration file with the given context. Otherwise, create a new
      internal context.


  Returns:

    dict: A dictionary of key-values representing the resolved context, after
    loading the provided modules and resolving all variables.

  '''

  if isinstance(path, six.string_types):

    if context is None:
      context = dict(defaults={})
    else:
      if 'defaults' not in context:
        context['defaults'] = {}

    retval = _load_context(os.path.realpath(os.path.expanduser(path)), context)

    return retval

  elif isinstance(path, collections.Iterable):

    retval = None
    for k in path: retval = load(k, retval)
    return retval

  else:

    raise TypeError('path must be either a string or iterable over strings')


def loadrc(context=None):
  '''Loads the default configuration file, or an override if provided

  This method will load **exactly** one (global) resource configuration file in
  this fixed order of preference:

  1. A file named :py:attr:`RCFILENAME` on the current directory
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

  if os.path.exists(RCFILENAME):
    path = os.path.realpath(RCFILENAME)
  elif os.path.exists(os.path.expanduser('~' + os.sep + RCFILENAME)):
    path = os.path.expanduser('~' + os.sep + RCFILENAME)
  else:
    return {}

  return load(path, context)
