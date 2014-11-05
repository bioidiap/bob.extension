#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Mar 2014 12:43:48 CET

"""Tests for file search utilities
"""

import os
import sys
import nose.tools
from .utils import uniq, egrep, find_file, find_header, find_library, \
    load_requirements, link_documentation

def test_uniq():

  a = [1, 2, 3, 7, 3, 2]

  nose.tools.eq_(uniq(a), [1, 2, 3, 7])

def test_find_file():

  f = find_file('array.h', subpaths=[os.path.join('include', 'blitz')])

  assert f

  nose.tools.eq_(os.path.basename(f[0]), 'array.h')

def test_find_header():

  f1 = find_file('array.h', subpaths=[os.path.join('include', 'blitz')])

  assert f1

  nose.tools.eq_(os.path.basename(f1[0]), 'array.h')

  f2 = find_header(os.path.join('blitz', 'array.h'))

  nose.tools.eq_(os.path.basename(f2[0]), 'array.h')

  assert f2

  nose.tools.eq_(f1, f2)

def test_find_library():

  f = find_library('blitz')

  assert f

  assert len(f) >= 1

  for k in f:
    assert k.find('blitz') >= 0

def test_egrep():

  f = find_header('version.hpp', subpaths=['boost', 'boost?*'])

  assert f

  matches = egrep(f[0], r"^#\s*define\s+BOOST_VERSION\s+(\d+)\s*$")

  nose.tools.eq_(len(matches), 1)

def test_find_versioned_library():

  f = find_header('version.hpp', subpaths=['boost', 'boost?*'])

  assert f

  matches = egrep(f[0], r"^#\s*define\s+BOOST_VERSION\s+(\d+)\s*$")

  nose.tools.eq_(len(matches), 1)

  version_int = int(matches[0].group(1))
  version_tuple = (
      version_int // 100000,
      (version_int // 100) % 1000,
      version_int % 100,
      )
  version = '.'.join([str(k) for k in version_tuple])

  lib = find_library('boost_system', version=version)
  lib += find_library('boost_system-mt', version=version)

  assert len(lib) >= 1

  for k in lib:
    assert k.find('boost_system') >= 0

def test_requirement_readout():

  if sys.version_info[0] == 3:
    from io import StringIO as stringio
  else:
    from cStringIO import StringIO as stringio

  f = """ # this is my requirements file
package-a >= 0.42
package-b
package-c
#package-e #not to be included

package-z
--no-index
-e http://example.com/mypackage-1.0.4.zip
"""

  result = load_requirements(stringio(f))
  expected = ['package-a >= 0.42', 'package-b', 'package-c', 'package-z']
  nose.tools.eq_(result, expected)


def test_documentation_generation():
  if sys.version_info[0] == 3:
    from io import StringIO as stringio
  else:
    from cStringIO import StringIO as stringio

  f = """ # this is my requirements file
package-a >= 0.42
package-b
package-c
#package-e #not to be included
setuptools

package-z
--no-index
-e http://example.com/mypackage-1.0.4.zip
"""

  # test NumPy and SciPy docs
  try:
    import numpy
    result = link_documentation(['numpy'], None)
    assert len(result) == 1
    key = list(result.keys())[0]
    assert '/numpy' in key
  except ImportError:
    pass

  try:
    import scipy
    result = link_documentation(['scipy'], None)
    assert len(result) == 1
    key = list(result.keys())[0]
    assert '/scipy' in key
    assert '/reference' in key
  except ImportError:
    pass


  # test pypi packages
  additional_packages = ['python', 'bob.extension', 'gridtk', 'other.bob.package']
  if "BOB_DOCUMENTATION_SERVER" not in os.environ:
    result = link_documentation(additional_packages, stringio(f))
    expected = {'http://docs.python.org/%d.%d' % sys.version_info[:2] : None, 'https://pythonhosted.org/setuptools' : None, 'https://pythonhosted.org/bob.extension' : None, 'https://pythonhosted.org/gridtk' : None}
    nose.tools.eq_(result, expected)

  # test idiap server
  os.environ["BOB_DOCUMENTATION_SERVER"] = "https://www.idiap.ch/software/bob/docs/latest/bioidiap/%s/master"
  result = link_documentation(additional_packages, stringio(f))
  expected = {'http://docs.python.org/%d.%d' % sys.version_info[:2] : None, 'https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.extension/master' : None, 'https://www.idiap.ch/software/bob/docs/latest/idiap/gridtk/master' : None}
  nose.tools.eq_(result, expected)

