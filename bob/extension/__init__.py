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
from distutils.file_util import copy_file

from pkg_resources import resource_filename

from .pkgconfig import pkgconfig
from .boost import boost
from .utils import uniq

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

    internal_libraries : {package_directory: [string]}

      A list of libraries that is build inside the given ``package_directory``,
      which this Extension depends on. For bob packages, this is usually the
      libraries containing the pure C++ code.

    internal_library_builder : {package_name : func(build_directory) -> libraries}

      A set of functions to compile the ``internal_libraries`` given above.
      This function takes as parameter the temporary build directory. It must
      return the list of generated libraries including full paths.
      If ``internal_library_builder`` is not specified, it is assumed that a
      normal ``Extension`` is used for this.

    """

    packages = []

    if 'packages' in kwargs and kwargs['packages']:
      if isinstance(kwargs['packages'], str):
        packages.append(kwargs['packages'])
      else:
        packages.extend(kwargs['packages'])

    if 'packages' in kwargs: del kwargs['packages']

    # check if we have to link against internal libraries
    if 'internal_libraries' in kwargs and kwargs['internal_libraries']:
      self.internal_libraries = kwargs['internal_libraries']
      del kwargs['internal_libraries']
    else:
      self.internal_libraries = None

    if 'internal_library_builder' in kwargs:
      self.internal_library_builder = kwargs['internal_library_builder']
      del kwargs['internal_library_builder']
    else:
      self.internal_library_builder = None

    # uniformize packages
    packages = normalize_requirements([k.strip().lower() for k in packages])

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
        'library_dirs': [],
        'libraries': [],
        }

    # Compilation options
    if platform.system() == 'Darwin':
      parameters['extra_compile_args'] += ['-Wno-#warnings']

    user_includes = kwargs.get('include_dirs', [])
    pkg_includes = []

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
        pkg_includes.append(boost_pkg.include_directory)

      # Adds specific boost libraries requested by the user
      if boost_modules:
        boost_libdirs, boost_libraries = boost_pkg.libconfig(boost_modules)
        parameters['library_dirs'].extend(boost_libdirs)
        parameters['libraries'].extend(boost_libraries)

    # Checks all other pkg-config requirements
    pkgs = check_packages(packages)

    for pkg in pkgs:

      # Adds parameters for each package, in order
      parameters['define_macros'] += pkg.package_macros()

      # Include directories are added with a special path
      for k in pkg.include_directories():
        if k in user_includes or k in pkg_includes: continue
        parameters['extra_compile_args'].extend(['-isystem', k])
        pkg_includes.append(k)

      parameters['define_macros'] += pkg.package_macros()
      parameters['library_dirs'] += pkg.library_directories()

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

    # add internal libraries
    if self.internal_libraries:
      for v in self.internal_libraries.values():
        parameters['libraries'] += v

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
      if self.internal_libraries:
        kwargs['runtime_library_dirs'] += [k for k in self.internal_libraries]
      kwargs['runtime_library_dirs'] = uniq(kwargs['runtime_library_dirs'])

    # Run the constructor for the base class
    DistutilsExtension.__init__(self, name, sources, **kwargs)

    # post-process the options since
    # there is an erroneous '-Wstrict-prototypes' in the environment options
    # see http://stackoverflow.com/questions/8106258/cc1plus-warning-command-line-option-wstrict-prototypes-is-valid-for-ada-c-o
    # note: this seems to work for python 2 only; for python 3, we still get the warnings...
    import distutils.sysconfig
    opt = distutils.sysconfig.get_config_var('OPT')
    os.environ['OPT'] = " ".join(flag for flag in opt.split() if flag != '-Wstrict-prototypes')


class build_ext(_build_ext):
  """Compile the C++ Extensions by adding information about the build path, if
  required.

  See the documentation for :py:class:`distutils.command.build_ext` for more
  information.
  """

  def run(self):
    """Iterates through the list of Extension packages and:

    * compiles the code using an external function, if provided
    * copies generated libraries to the package directory
    * adapts the linker path, if internal packages are linked
    """
    # iterate through the extensions
    for ext in self.extensions:
      # check if it is our type of extension
      if isinstance(ext, Extension) and ext.internal_libraries:

        lib_dirs = []
        if ext.internal_library_builder is not None:
          # build libraries using the provided functions
          for name, builder_function in ext.internal_library_builder.items():
            build_dir = os.path.join(self.build_lib, name)
            if not os.path.exists(build_dir): os.makedirs(build_dir)
            libraries = builder_function(build_dir)

            # copy libraries to place
            fullname = self.get_ext_fullname(ext.name)
            package = '.'.join(fullname.split('.')[:-1])
            build_py = self.get_finalized_command('build_py')
            package_dir = build_py.get_package_dir(package)

            for lib in libraries: copy_file(lib, package_dir)
            lib_dirs.append(package_dir)

        else:
          lib_dirs = [os.path.join(self.build_lib, os.sep.join(ext.name.split('.')[:-1]))]

        # add library path so that the extension is found during linking
        if not ext.library_dirs: ext.library_dirs = []
        ext.library_dirs += lib_dirs

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
