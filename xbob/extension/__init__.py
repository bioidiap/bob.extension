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
from distutils.extension import Extension as DistutilsExtension
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
      ('XBOB_EXT_MODULE_PREFIX', '"%s"' % s[0]),
      ('XBOB_EXT_MODULE_NAME', '"%s"' % s[1]),
      ]

  if sys.version_info[0] >= 3:
    retval.append(('XBOB_EXT_ENTRY_NAME', 'PyInit_%s' % s[1]))
  else:
    retval.append(('XBOB_EXT_ENTRY_NAME', 'init%s' % s[1]))

  if version: retval.append(('XBOB_EXT_MODULE_VERSION', '"%s"' % version))

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

  def __init__(self, *args, **kwargs):
    """Initialize the extension with parameters.

    External package extensions (mostly comming from pkg-config), adds a single
    parameter to the standard arguments of the constructor:

    packages : [list]

      This should be a list of strings indicating the name of the bob
      (pkg-config) modules you would like to have linked to your extension
      **additionally** to ``bob-python``. Candidates are module names like
      "bob-machine" or "bob-math".

      For convenience, you can also specify "opencv" or other 'pkg-config'
      registered packages as a dependencies.
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
        'define_macros': generate_self_macros(args[0], version),
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
      kwargs['runtime_library_dirs'] = uniq(kwargs['runtime_library_dirs'])

    # Run the constructor for the base class
    DistutilsExtension.__init__(self, *args, **kwargs)

    # post-process the options since
    # there is an erroneous '-Wstrict-prototypes' in the environment options
    # see http://stackoverflow.com/questions/8106258/cc1plus-warning-command-line-option-wstrict-prototypes-is-valid-for-ada-c-o
    # note: this seems to work for python 2 only; for python 3, we still get the warnings...
    import distutils.sysconfig
    opt = distutils.sysconfig.get_config_var('OPT')
    os.environ['OPT'] = " ".join(flag for flag in opt.split() if flag != '-Wstrict-prototypes')

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
