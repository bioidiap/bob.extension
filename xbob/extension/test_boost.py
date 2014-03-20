#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Mar 2014 12:43:48 CET

"""Tests for boost configuration
"""

import os
import sys
import nose
from .boost import boost
from distutils.version import LooseVersion

def test_boost_version():

  b = boost('>= 1.30')
  assert LooseVersion(b.version) >= '1.30'

def test_boost_simple_modules():

  b = boost()
  directory, libname = b.libconfig(['system'])
  assert directory
  assert os.path.exists(directory)
  assert libname
  assert len(libname) == 1

def test_boost_python_modules():

  b = boost()
  directory, libname = b.libconfig(['python'])
  assert directory
  assert os.path.exists(directory)
  assert libname
  assert len(libname) == 1
  assert libname[0].find('-py%d%d' % sys.version_info[:2]) >= 0

def test_boost_multiple_modules():

  b = boost()
  directory, libname = b.libconfig(['python', 'system'])
  assert directory
  assert os.path.exists(directory)
  assert libname
  assert len(libname) == 2
  assert libname[0].find('-py%d%d' % sys.version_info[:2]) >= 0
  assert libname[1].find('-py%d%d' % sys.version_info[:2]) < 0

def test_common_prefix():

  b = boost()
  directory, libname = b.libconfig(['python', 'system'])
  assert directory
  assert os.path.exists(directory)
  os.path.commonprefix([directory, b.include_directory])
  assert len(os.path.commonprefix([directory, b.include_directory])) > 1
