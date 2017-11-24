#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Tests for the python-based config functionality'''


from .config import load
import os
import pkg_resources
path = pkg_resources.resource_filename('bob.extension', 'data')


def test_basic():

  c = load([os.path.join(path, 'basic-config.py')])
  assert c == {'a': 1, 'b': 3}


def test_basic_with_context():

  c = load([os.path.join(path, 'basic-config.py')], {'d': 35, 'a': 0})
  assert c == {'a': 1, 'b': 3, 'd': 35}


def test_chain_loading():

  file1 = os.path.join(path, 'basic-config.py')
  file2 = os.path.join(path, 'load-config.py')
  c = load([file1, file2])
  assert c == {'a': 1, 'b': 6}
