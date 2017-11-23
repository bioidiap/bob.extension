#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Tests for the config module and functionality'''


import os
import pkg_resources
path = pkg_resources.resource_filename('bob.extension', 'data')

from .config import load, loadrc, ENVNAME


def test_basic():

  c = load([os.path.join(path, 'basic-config.py')])
  assert c == {'a': 1, 'b': 3}


def test_defaults():

  c = load([os.path.join(path, 'defaults-config.py')])
  assert c == {'bob_db_atnt': {'directory': '/directory/to/root/of/atnt-database', 'extension': '.ppm'} }


def test_chain_loading():

  file1 = os.path.join(path, 'defaults-config.py')
  file2 = os.path.join(path, 'load-config.py')
  c = load([file1, file2])
  assert c == {'bob_db_atnt': {'directory': '/directory/to/root/of/atnt-database', 'extension': '.hdf5'} }


def test_rc_env():

  os.environ[ENVNAME] = os.path.join(path, 'basic-config.py')
  c = loadrc() #should load from environment variable
  assert c == {'a': 1, 'b': 3}
