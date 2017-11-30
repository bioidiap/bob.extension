#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Tests for the python-based config functionality'''


from .config import load
import os
import pkg_resources
import numpy
path = pkg_resources.resource_filename('bob.extension', 'data')


def test_basic():

  c = load([os.path.join(path, 'basic-config.py')])
  assert hasattr(c, "a") and c.a == 1
  assert hasattr(c, "b") and c.b == 3
  

def test_basic_with_context():

  c = load([os.path.join(path, 'basic-config.py')], {'d': 35, 'a': 0})
  assert hasattr(c, "a") and c.a == 1
  assert hasattr(c, "b") and c.b == 3
  assert hasattr(c, "d") and c.d == 35


def test_chain_loading():

  file1 = os.path.join(path, 'basic-config.py')
  file2 = os.path.join(path, 'load-config.py')
  c = load([file1, file2])
  assert hasattr(c, "a") and c.a == 1
  assert hasattr(c, "b") and c.b == 6

  
def test_config_with_module():

  c = load([os.path.join(path, 'config-with-module.py')])
  assert hasattr(c, "return_zeros") and numpy.allclose(c.return_zeros(), numpy.zeros(shape=(2,)))

