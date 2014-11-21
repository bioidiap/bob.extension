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
  example_dir = os.path.realpath(pkg_resources.resource_filename("bob.extension", "../../examples"))
  temp_dir = tempfile.mkdtemp(prefix="bob_test")

  # extract archive
  subprocess.call(["tar", "-xjf", os.path.join(example_dir, "bob.example.%s.tar.bz2"%package), "-C", temp_dir])
  package_dir = os.path.join(temp_dir, "bob.example.%s"%package)
  assert os.path.exists(package_dir)

  # bootstrap
  subprocess.call([sys.executable, "bootstrap.py"], cwd=package_dir)
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

