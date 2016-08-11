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
  devnull = open(os.devnull, 'w')

  try:
    # extract archive
    import tarfile
    with tarfile.open(tarball) as tar: tar.extractall(temp_dir)
    package_dir = os.path.join(temp_dir, "bob.example.%s" % package)

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

  finally:
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
