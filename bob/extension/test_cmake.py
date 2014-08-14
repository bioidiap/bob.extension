#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Mar 2014 12:43:48 CET

"""Tests for file search utilities
"""

import os
import sys
import shutil
import nose.tools

import bob.extension
import pkg_resources

import tempfile

def _find(lines, start):
  for i, line in enumerate(lines):
    if line.find(start) == 0:
      return i
  assert False

def test_cmake_list():
  # checks that the CMakeLists.txt file is generated properly

  generator = bob.extension.CMakeListsGenerator(
    name = 'bob_cmake_test',
    sources = ['cmake_test.cpp'],
    target_directory = "test_target",
    version = '3.2.1',
    include_directories = ["/usr/include/test"],
    libraries = ['some_library'],
    library_directories = ["/usr/include/test"],
    macros = [("TEST", "MACRO")]
  )

  temp_dir = tempfile.mkdtemp(prefix="bob_extension_test_")

  generator.generate(temp_dir)

  # read created file
  lines = [line.rstrip() for line in open(os.path.join(temp_dir, "CMakeLists.txt"))]

  # check that all elements are properly written in the file
  assert lines[_find(lines, 'project')] == 'project(bob_cmake_test)'
  assert lines[_find(lines, 'include')] == 'include_directories(SYSTEM /usr/include/test)'
  assert lines[_find(lines, 'link')] == 'link_directories(/usr/include/test)'
  assert lines[_find(lines, 'add')] == 'add_definitions(-DTEST=MACRO)'

  index = _find(lines, 'add_library')
  assert lines[index+1].find('cmake_test.cpp') >= 0

  index = _find(lines, 'set_target_properties')
  assert lines[index].find('3.2') >= 0
  assert lines[index+1].find('test_target') >= 0

  assert lines[_find(lines, 'target_link_libraries')].find('some_library') >= 0

  # finally, clean up the mess
  shutil.rmtree(temp_dir)


def test_library():
  temp_dir = tempfile.mkdtemp(prefix="bob_extension_test_")
  target_dir = os.path.join(temp_dir, 'target')
  os.makedirs(target_dir)
  # check that the library compiles and links properly
  library = bob.extension.Library(
    name = 'bob_cmake_test',
    sources = [pkg_resources.resource_filename(__name__, 'test_documentation.cpp')],
    package_directory = temp_dir,
    target_directory = target_dir,
    include_dirs = [pkg_resources.resource_filename(__name__, 'include')],
    version = '3.2.1'
  )

  # compile
  compile_dir = os.path.join(temp_dir, 'build')
  os.makedirs(compile_dir)
  library.compile(compile_dir)

  # check that the library was generated sucessfully
  lib_name = 'libbob_cmake_test.so'
  # TODO: change lib name for MacOS
  assert os.path.exists(os.path.join(target_dir, lib_name))
  assert os.path.exists(os.path.join(target_dir, lib_name + ".3"))
  assert os.path.exists(os.path.join(target_dir, lib_name + ".3.2"))

  # TODO: compile a test executable to actually link the library

  # finally, clean up the mess
  shutil.rmtree(temp_dir)

