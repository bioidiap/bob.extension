#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 28 Jan 2013 16:40:27 CET

"""A custom build class for Pkg-config based extensions
"""

import sys
import os
import platform
import pkg_resources
from setuptools.extension import Extension as DistutilsExtension
from setuptools.command.build_ext import build_ext as _build_ext

from pkg_resources import resource_filename

from .pkgconfig import pkgconfig
from .boost import boost
from .utils import uniq, find_executable, find_library
from .cmake import CMakeListsGenerator

__version__ = pkg_resources.require(__name__)[0].version

def check_packages(packages):
  """Checks if the requirements for the given packages are satisfied.

  Raises a :py:class:`RuntimeError` in case requirements are not satisfied.
  This means either not finding a package if no version number is specified or
  verifying that the package version does not match the required version by the
  builder.

  Package requirements can be set like this::

    "pkg > VERSION"

  In this case, the package version should be greater than the given version
  number. Comparisons are done using :py:mod:`distutils.version.LooseVersion`.
  You can use other comparators such as ``<``, ``<=``, ``>=`` or ``==``. If no
  version number is given, then we only require that the package is installed.
  """

  from re import split

  used = set()
  retval = []

  for requirement in uniq(packages):

    splitreq = split(r'\s*(?P<cmp>[<>=]+)\s*', requirement)

    if len(splitreq) not in (1, 3):

      raise RuntimeError("cannot parse requirement `%s'", requirement)

    p = pkgconfig(splitreq[0])

    if len(splitreq) == 3: # package + version number

      if splitreq[1] == '>':
        assert p > splitreq[2], "%s version is not > `%s'" % (p.name, splitreq[2])
      elif splitreq[1] == '>=':
        assert p >= splitreq[2], "%s version is not >= `%s'" % (p.name, splitreq[2])
      elif splitreq[1] == '<':
        assert p < splitreq[2], "%s version is not < `%s'" % (p, splitreq[2])
      elif splitreq[1] == '<=':
        assert p <= splitreq[2], "%s version is not <= `%s'" % (p, splitreq[2])
      elif splitreq[1] == '==':
        assert p <= splitreq[2], "%s version is not == `%s'" % (p, splitreq[2])
      else:
        raise RuntimeError("cannot parse requirement `%s'", requirement)

    retval.append(p)

    if p.name in used:
      raise RuntimeError("package `%s' had already been requested - cannot (currently) handle recurring requirements")
    used.add(p.name)

  return retval

def generate_self_macros(extname, version):
  """Generates standard macros with library, module names and prefix"""

  if version is None:
    return []

  s = extname.rsplit('.', 1)

  retval = [
      ('BOB_EXT_MODULE_PREFIX', '"%s"' % s[0]),
      ('BOB_EXT_MODULE_NAME', '"%s"' % s[1]),
      ]

  if sys.version_info[0] >= 3:
    retval.append(('BOB_EXT_ENTRY_NAME', 'PyInit_%s' % s[1]))
  else:
    retval.append(('BOB_EXT_ENTRY_NAME', 'init%s' % s[1]))

  if version: retval.append(('BOB_EXT_MODULE_VERSION', '"%s"' % version))

  return retval

def reorganize_isystem(args):
  """Re-organizes the -isystem includes so that more specific paths come
  first"""

  remainder = []
  includes = []

  skip = False
  for i in range(len(args)):
    if skip:
      skip = False
      continue
    if args[i] == '-isystem':
      includes.append(args[i+1])
      skip = True
    else:
      remainder.append(args[i])

  includes = uniq(includes[::-1])[::-1]

  # sort includes so that the shortest system includes go last
  # this algorithm will ensure '/usr/include' comes after other
  # overwrites
  includes.sort(key=lambda item: (-len(item), item))

  retval = [tuple(remainder)] + [('-isystem', k) for k in includes]
  from itertools import chain
  return list(chain.from_iterable(retval))

def normalize_requirements(requirements):
  """Normalizes the requirements keeping only the most tight"""

  from re import split

  parsed = {}

  for requirement in requirements:
    splitreq = split(r'\s*(?P<cmp>[<>=]+)\s*', requirement)

    if len(splitreq) not in (1, 3):

      raise RuntimeError("cannot parse requirement `%s'", requirement)

    if len(splitreq) == 1: # only package

      parsed.setdefault(splitreq[0], [])

    if len(splitreq) == 3: # package + version number

      parsed.setdefault(splitreq[0], []).append(tuple(splitreq[1:]))

  # at this point, all requirements are organised:
  # requirement -> [(op, version), (op, version), ...]

  leftovers = []

  for key, value in parsed.items():
    value = uniq(value)

    if not value:
      leftovers.append(key)
      continue

    for v in value:
      leftovers.append(' '.join((key, v[0], v[1])))

  return leftovers


def get_bob_libraries(bob_packages):
  """Returns a list of include directories, libraries and library directories
  for the given bob libraries."""
  includes = []
  libraries = []
  library_directories = []
  # iterate through the list of bob packages
  if bob_packages is not None:
    # TODO: need to handle versions?
    bob_packages = normalize_requirements([k.strip().lower() for k in bob_packages])
    for package in bob_packages:
      includes.append(resource_filename(package, 'include'))

      lib_name = package.replace('.', '_')
      libs = find_library(lib_name, prefixes=[resource_filename(package, '.')])
      # add the FIRST lib that we found, if any
      if len(libs):
        libraries.append(lib_name)
        library_directories.append(os.path.dirname(libs[0]))

  return includes, libraries, library_directories




class Extension(DistutilsExtension):
  """Extension building with pkg-config packages.

  See the documentation for :py:class:`distutils.extension.Extension` for more
  details on input parameters.
  """

  def __init__(self, name, sources, **kwargs):
    """Initialize the extension with parameters.

    External package extensions (mostly coming from pkg-config), adds a single
    parameter to the standard arguments of the constructor:

    packages : [string]

      This should be a list of strings indicating the name of the bob
      (pkg-config) modules you would like to have linked to your extension
      **additionally** to ``bob-python``. Candidates are module names like
      "bob-machine" or "bob-math".

      For convenience, you can also specify "opencv" or other 'pkg-config'
      registered packages as a dependencies.

    bob_packages: [string]

      A list of bob libraries (such as ``'bob.core'``) containing C++ code
      that should be included and linked

    """

    packages = []

    if 'packages' in kwargs and kwargs['packages']:
      if isinstance(kwargs['packages'], str):
        packages.append(kwargs['packages'])
      else:
        packages.extend(kwargs['packages'])
    if 'packages' in kwargs: del kwargs['packages']

    # uniformize packages
    packages = normalize_requirements([k.strip().lower() for k in packages])

    # check if we have bob libraries to link against
    if 'bob_packages' in kwargs and kwargs['bob_packages']:
      self.bob_packages = kwargs['bob_packages']
      del kwargs['bob_packages']
    else:
      self.bob_packages = None

    bob_includes, bob_libraries, bob_library_dirs = get_bob_libraries(self.bob_packages)

    # Boost requires a special treatment
    boost_req = ''
    for i, pkg in enumerate(packages):
      if pkg.startswith('boost'):
        boost_req = pkg
        del packages[i]

    # We still look for the keyword 'boost_modules'
    boost_modules = []
    if 'boost_modules' in kwargs and kwargs['boost_modules']:
      if isinstance(kwargs['boost_modules'], str):
        boost_modules.append(kwargs['boost_modules'])
      else:
        boost_modules.extend(kwargs['boost_modules'])

    if 'boost_modules' in kwargs: del kwargs['boost_modules']

    if boost_modules and not boost_req: boost_req = 'boost >= 1.0'

    # Was a version parameter given?
    version = None
    if 'version' in kwargs:
      version = kwargs['version']
      del kwargs['version']

    # Mixing
    parameters = {
        'define_macros': generate_self_macros(name, version),
        'extra_compile_args': ['-std=c++0x'], #synomym for c++11?
        'library_dirs': bob_library_dirs,
        'libraries': bob_libraries,
        }

    # Compilation options
    if platform.system() == 'Darwin':
      parameters['extra_compile_args'] += ['-Wno-#warnings']

    user_includes = kwargs.get('include_dirs', [])
    self.pkg_includes = []
    self.pkg_libraries = []
    self.pkg_library_directories = []
    self.pkg_macros = []

    # Updates for boost
    if boost_req:

      boost_pkg = boost(boost_req.replace('boost', '').strip())

      # Adds macros
      parameters['define_macros'] += boost_pkg.macros()

      # Adds the include directory (enough for using just the template library)
      if boost_pkg.include_directory not in user_includes:
        parameters['extra_compile_args'].extend([
          '-isystem', boost_pkg.include_directory
          ])
        self.pkg_includes.append(boost_pkg.include_directory)

      # Adds specific boost libraries requested by the user
      if boost_modules:
        boost_libdirs, boost_libraries = boost_pkg.libconfig(boost_modules)
        parameters['library_dirs'].extend(boost_libdirs)
        self.pkg_library_directories.extend(boost_libdirs)
        parameters['libraries'].extend(boost_libraries)
        self.pkg_libraries.extend(boost_libraries)

    # Checks all other pkg-config requirements
    pkgs = check_packages(packages)

    for pkg in pkgs:

      # Adds parameters for each package, in order
      parameters['define_macros'] += pkg.package_macros()
      self.pkg_macros += pkg.package_macros()

      # Include directories are added with a special path
      for k in pkg.include_directories():
        if k in user_includes or k in self.pkg_includes: continue
        parameters['extra_compile_args'].extend(['-isystem', k])
        self.pkg_includes.append(k)

      parameters['library_dirs'] += pkg.library_directories()
      self.pkg_library_directories += pkg.library_directories()

      if pkg.name.find('bob-') == 0: # one of bob's packages

        # make-up the names of versioned Bob libraries we must link against

        if platform.system() == 'Darwin':
          libs = ['%s.%s' % (k, pkg.version) for k in pkg.libraries()]
        elif platform.system() == 'Linux':
          libs = [':lib%s.so.%s' % (k, pkg.version) for k in pkg.libraries()]
        else:
          raise RuntimeError("supports only MacOSX and Linux builds")

      else:

        libs = pkg.libraries()

      parameters['libraries'] += libs
      self.pkg_libraries += libs

    # Filter and make unique
    for key in parameters.keys():

      # Tune input parameters if they were set
      if key in kwargs:
        kwargs[key] = list(kwargs[key]) #deep copy
        kwargs[key].extend(parameters[key])
      else: kwargs[key] = parameters[key]

      if key in ('extra_compile_args'): continue

      kwargs[key] = uniq(kwargs[key])

    # add our include dir by default
    self_include_dir = resource_filename(__name__, 'include')
    kwargs.setdefault('include_dirs', []).append(self_include_dir)
    kwargs['include_dirs'] = user_includes + bob_includes + kwargs['include_dirs']

    # Uniq'fy parameters that are not on our parameter list
    kwargs['include_dirs'] = uniq(kwargs['include_dirs'])

    # Stream-line '-isystem' includes
    kwargs['extra_compile_args'] = reorganize_isystem(kwargs['extra_compile_args'])

    # Make sure the language is correctly set to C++
    kwargs['language'] = 'c++'

    # On Linux, set the runtime path
    if platform.system() == 'Linux':
      kwargs.setdefault('runtime_library_dirs', [])
      kwargs['runtime_library_dirs'] += kwargs['library_dirs']
      kwargs['runtime_library_dirs'] = uniq(kwargs['runtime_library_dirs'])

    # Run the constructor for the base class
    DistutilsExtension.__init__(self, name, sources, **kwargs)


class Library (Extension):
  """A class to compile a pure C++ code library used within and outside an extension using CMake."""

  def __init__(self, name, sources, package_directory, target_directory, version, bob_packages = [], packages = [], include_dirs = [], libraries = [], library_dirs = [], define_macros = []):
    """Initializes a pure C++ library that will be compiled with CMake.

    By default, the include directory of this package is automatically added to the ``include_dirs``.
    It is expected to be ``target_directory + '/include'``.

    .. note::
      This directory is also automatically added to **all other** :py:class:`Extension`'s that are compiled within this package.

    .. warning::
      IMPORTANT! To compile this library with CMake, the :py:class:`build_ext` class provided in this module is required.
      Please include::

        cmdclass = {
          'build_ext': build_ext
        },

      as a parameter to the ``setup`` function in your setup.py.

    Keyword parameters:

    name : string
      The name of the library to generate, e.g., ``'bob_core'``

    sources : [string]
      A list of files (relative to the base directory) that should be compiled and linked by CMake

    package_directory : string
      The directory of the package, where the source files can be found

    target_directory : string
      The directory where the generated library should be placed

    version : string
      The version of the library, which is usually identical to the version of the package

    bob_packages : [string]
      A list of bob packages that the pure C++ code relies on.
      Libraries and include directories of these packages will be automatically added.

    packages : [string]
      A list of pkg-config based packages, see :py:class:`Extension`.
      Macros, libraries and include directories of these packages will be automatically added.

    include_dirs : [string]
      An additional list of include directories that is not covered by ``bob_packages`` and ``packages``

    libraries : [string]
      An additional list of libraries that is not covered by ``bob_packages`` and ``packages``

    library_dirs : [string]
      An additional list of library directories that is not covered by ``bob_packages`` and ``packages``

    define_macros : [(string, string)]
      An additional list of preprocessor definitions that is not covered by ``packages``
    """
    self.name = name
    self.package_directory = package_directory
    self.target_directory = target_directory
    self.sources = sources
    self.version = version
    self.include_directories = [os.path.join(target_directory, 'include')] + include_dirs
    self.libraries = libraries[:]
    self.library_directories = library_dirs[:]
    self.define_macros = define_macros[:]

    # add includes and libs for bob packages
    bob_includes, bob_libraries, bob_library_dirs = get_bob_libraries(bob_packages)
    self.include_directories.extend(bob_includes)
    self.libraries.extend(bob_libraries)
    self.library_directories.extend(bob_library_dirs)

    # find the cmake executable
    cmake = find_executable("cmake")
    if not cmake:
      raise IOError("The Library class needs CMake version >= 2.8 to be installed, but CMake cannot be found")
    self.cmake = cmake[0]

    # call base class constructor, i.e., to handle the packages
    Extension.__init__(self, name, sources, packages=packages)

    # add the include directories for the packages as well
    self.include_directories.extend(self.pkg_includes)
    self.libraries.extend(self.pkg_libraries)
    self.library_directories.extend(self.pkg_library_directories)
    self.define_macros.extend(self.pkg_macros)


  def compile(self, build_directory, build_type = "RELEASE", compiler = None):
    """This function will automatically create a CMakeLists.txt file in the ``package_directory`` including the required information.
    Afterwards, the library is built using CMake in the given ``build_directory``.
    By default, the build type is RELEASE, and the compiler is the default CMake compiler.
    To change this, use the ``build_type`` and ``compiler`` parameters.
    """
    # generate CMakeLists.txt makefile
    generator = CMakeListsGenerator(
      name = self.name,
      sources = self.sources,
      target_directory = self.target_directory,
      version = self.version,
      include_directories = uniq(self.include_directories),
      libraries = uniq(self.libraries),
      library_directories = uniq(self.library_directories),
      macros = uniq(self.define_macros)
    )
    generator.generate(self.package_directory)

    # compile in the build directory
    import subprocess
    env = {'VERBOSE' : '1'}
    env.update(os.environ)
    if compiler is not None:
      env['CXX'] = compiler
    # configure cmake
    command = [self.cmake, self.package_directory, '-DCMAKE_BUILD_TYPE=%s' % build_type]
    subprocess.call(command, cwd=build_directory, env=env)
    # run make
    subprocess.call(['make'], cwd=build_directory, env=env)


class build_ext(_build_ext):
  """Compile the C++ :py:class`Library`'s using CMake, and the python extensions afterwards

  See the documentation for :py:class:`distutils.command.build_ext` for more
  information.
  """

  def run(self):
    """Iterates through the list of Extension packages and:

    1. compiles all pure C++ :py:class:`Library`'s
    2. adds the according include and library directories so that other Extensions can find the newly generated libs

       .. note::
         This function **does not** add the library itself.
         To link the generated library into another Extension, add this lib in the list of ``libraries``.

    3. compiles the remaining extensions using the default extension mechanism

    """
    lib_dirs = []
    include_dirs = []
    # iterate through the extensions
    for ext in self.extensions:
      # check if it is our type of extension
      if isinstance(ext, Library):
        # TODO: get compiler and add it to the compiler
        # TODO: get the debug status and add the build_type parameter
        # build libraries using the provided functions
        build_dir = os.path.join(self.build_lib, ext.name)
        if not os.path.exists(build_dir): os.makedirs(build_dir)
        # compile
        ext.compile(build_dir)
        lib_dirs.append(ext.target_directory)
        include_dirs.append(os.path.join(ext.target_directory, 'include'))

    # now, we keep only the extensions that are python extensions
    self.extensions = [ext for ext in self.extensions if not isinstance(ext, Library)]

    # set the DEFAULT library path and include path for all other extensions
    for ext in self.extensions:
      ext.library_dirs = lib_dirs + (ext.library_dirs if ext.library_dirs else [])
      ext.runtime_library_dirs = lib_dirs + (ext.runtime_library_dirs if ext.runtime_library_dirs else [])
      ext.include_dirs = include_dirs + (ext.include_dirs if ext.include_dirs else [])

    # call the base class function
    return _build_ext.run(self)


def get_config():
  """Returns a string containing the configuration information.
  """

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s (%s)\n" % (this.key, this.version, this.location)
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
