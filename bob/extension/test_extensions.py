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
  local_file = os.path.realpath(os.path.join(pkg_resources.resource_filename('bob.extension', '../../examples'), 'bob.example.%s.tar.bz2'%package))
  if os.path.exists(local_file):
    example_url = 'file://' + local_file
  else:
    example_url = "https://github.com/bioidiap/bob.extension/raw/master/examples/bob.example.%s.tar.bz2"%package
  temp_dir = tempfile.mkdtemp(prefix="bob_test")
  local_archive = os.path.join(temp_dir, "bob.example.%s.tar.bz2"%package)
  print ("Downloading package '%s'" % example_url)

  # redirect output of functions to /dev/null to avoid spamming the console
  devnull = open(os.devnull, 'w')

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
  subprocess.call([sys.executable, "bootstrap-buildout.py"], cwd=package_dir, stdout=devnull, stderr=devnull)
  assert os.path.exists(os.path.join(package_dir, "bin", "buildout"))

  # buildout
  # if we have a setup.py in our current directory, we develop both (as we might be in the current source directory of bob.extension and use it),
  # otherwise we only develop the downloaded source package
  develop = '%s\n.'%os.getcwd() if os.path.exists("setup.py") else '.'
  subprocess.call(['./bin/buildout', 'buildout:prefer-final=false', 'buildout:develop=%s'%develop], cwd=package_dir, stdout=devnull)
  assert os.path.exists(os.path.join(package_dir, "bin", "python"))

  # nosetests
  subprocess.call(['./bin/nosetests', '-sv'], cwd=package_dir, stdout=devnull, stderr=devnull)

  # check that the call is working
  subprocess.call(run_call, cwd=package_dir, stdout=devnull)

  subprocess.call(['./bin/sphinx-build', 'doc', 'sphinx'], cwd=package_dir, stdout=devnull)
  assert os.path.exists(os.path.join(package_dir, "sphinx", "index.html"))

  subprocess.call('./bin/python -c "import pkg_resources; from bob.example.%s import get_config; print(get_config())"'%package, cwd=package_dir, stdout=devnull, shell=True)

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
