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
  example_url = "https://github.com/bioidiap/bob.extension/raw/master/examples/bob.example.%s.tar.bz2"%package
  temp_dir = tempfile.mkdtemp(prefix="bob_test")
  local_archive = os.path.join(temp_dir, "bob.example.%s.tar.bz2"%package)

  # download archive
  if sys.version_info[0] <= 2:
    import urllib2 as urllib
  else:
    import urllib.request as urllib
  # download
  url = urllib.urlopen(example_url)
  tfile = open(local_archive, 'wb')
  tfile.write(url.read())
  tfile.close()

  # extract archive
  import tarfile
  tar = tarfile.open(local_archive)
  tar.extractall(temp_dir)
  os.remove(local_archive)
  package_dir = os.path.join(temp_dir, "bob.example.%s"%package)

  # bootstrap
  subprocess.call([sys.executable, "bootstrap-buildout.py"], cwd=package_dir)
  assert os.path.exists(os.path.join(package_dir, "bin", "buildout"))

  # buildout
  subprocess.call(['./bin/buildout', 'buildout:prefer-final=false'], cwd=package_dir)
  assert os.path.exists(os.path.join(package_dir, "bin", "python"))

  # nosetests
  subprocess.call(['./bin/nosetests', '-sv'], cwd=package_dir)

  # check that the call is working
  subprocess.call(run_call, cwd=package_dir)

  subprocess.call(['./bin/sphinx-build', 'doc', 'sphinx'], cwd=package_dir)
  assert os.path.exists(os.path.join(package_dir, "sphinx", "index.html"))

  shutil.rmtree(temp_dir)


def test_project():
  # Tests that the bob.example.project works
  _run('project', ['./bin/version.py'])


def test_extension():
  # Tests that the bob.example.extension compiles and works
  _run('extension', ['./bin/reverse.py', '1', '2', '3', '4', '5'])


def test_library():
  # Tests that the bob.example.library compiles and works
  _run('library', ['./bin/reverse.py', '1', '2', '3', '4', '5'])

