#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Mar 2014 12:43:48 CET

"""Tests that the examples work as expected
"""

import os
import sys
import nose.tools
import tempfile
import shutil
import subprocess
import pkg_resources


def _run(package, run_call):
  tarball = os.path.join(
      pkg_resources.resource_filename('bob.extension', 'data'),
      'bob.example.%s.tar.bz2' % package,
      )
  temp_dir = tempfile.mkdtemp(prefix="bob_test")

  # redirect output of functions to /dev/null to avoid spamming the console
  # devnull = open(os.devnull, 'w')

  try:
    # extract archive
    import tarfile
    with tarfile.open(tarball) as tar: tar.extractall(temp_dir)
    package_dir = os.path.join(temp_dir, "bob.example.%s" % package)

    def _join(*args):
      a = (package_dir,) + args
      return os.path.join(*a)

    def _bin(path):
      return _join('bin', path)

    # buildout
    # if we have a setup.py in our current directory, we develop both (as we might be in the current source directory of bob.extension and use it),
    # otherwise we only develop the downloaded source package
    develop = '%s\n.' % os.getcwd() if os.path.exists('setup.py') else '.'
    subprocess.call(['buildout', 'buildout:prefer-final=false', 'buildout:develop=%s'%develop], cwd=package_dir, shell=True)
    assert os.path.exists(_bin('python'))

    # nosetests
    subprocess.call([_bin('nosetests'), '-sv'])

    # check that the call is working
    subprocess.call([_bin(run_call[0])] + run_call[1:])

    subprocess.call([_bin('sphinx-build'), _join('doc'), _join('sphinx')])
    assert os.path.exists(_join('sphinx', 'index.html'))

    subprocess.call([_bin('python'), '-c', 'import pkg_resources; from bob.example.%s import get_config; print(get_config())'%package])

  finally:
    shutil.rmtree(temp_dir)


def test_project():
  # Tests that the bob.example.project works
  _run('project', ['version.py'])


def test_extension():
  # Tests that the bob.example.extension compiles and works
  _run('extension', ['reverse.py', '1', '2', '3', '4', '5'])


def test_library():
  # Tests that the bob.example.library compiles and works
  _run('library', ['reverse.py', '1', '2', '3', '4', '5'])
