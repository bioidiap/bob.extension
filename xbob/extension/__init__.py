#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 28 Jan 2013 16:40:27 CET

"""A custom build class for Pkg-config based extensions
"""

import platform
from .pkgconfig import pkgconfig
from distutils.extension import Extension as DistutilsExtension

__version__ = __import__('pkg_resources').require('xbob.extension')[0].version

def uniq(seq):
  """Uniqu-fy preserving order"""

  seen = set()
  seen_add = seen.add
  return [ x for x in seq if x not in seen and not seen_add(x)]

def check_packages(packages):
  """Checks if the requirements for the given packages are satisfied.

  Raises a :py:class:`RuntimeError` in case requirements are not satisfied.
  This means either not finding a package if no version number is specified or
  veryfing that the package version does not match the required version by the
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
        assert p > splitreq[2], "%s version is not > `%s'" % (p, splitreq[2])
      elif splitreq[1] == '>=': 
        assert p >= splitreq[2], "%s version is not >= `%s'" % (p, splitreq[2])
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


class Extension(DistutilsExtension):
  """Extension building with pkg-config packages.

  See the documentation for :py:class:`distutils.extension.Extension` for more
  details on input parameters.
  """

  def __init__(self, *args, **kwargs):
    """Initialize the extension with parameters.

    Pkg-config extensions adds a single parameter to the standard arguments of
    the constructor:

    pkgconfig : [list]

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

    # Check all requirements
    pkgs = check_packages(packages)

    # Mixing
    parameters = {
        'define_macros': [],
        'extra_compile_args': ['-std=c++11'],
        'library_dirs': [],
        'libraries': [],
        }

    # Compilation options
    if platform.system() == 'Darwin':
      parameters['extra_compile_args'] += ['-Wno-#warnings']

    user_includes = kwargs.get('include_dirs', [])
    pkg_includes = []

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
      if key in kwargs: kwargs[key].extend(parameters[key])
      else: kwargs[key] = parameters[key]

      if key in ('extra_compile_args'): continue

      kwargs[key] = uniq(kwargs[key])

    # Uniq'fy parameters that are not on our parameter list
    kwargs['include_dirs'] = uniq(kwargs.get('include_dirs', []))

    # Make sure the language is correctly set to C++
    kwargs['language'] = 'c++'

    # On Linux, set the runtime path
    if platform.system() == 'Linux':
      kwargs.setdefault('runtime_library_dirs', [])
      kwargs['runtime_library_dirs'] += kwargs['library_dirs']
      kwargs['runtime_library_dirs'] = uniq(kwargs['runtime_library_dirs'])

    # Run the constructor for the base class
    DistutilsExtension.__init__(self, *args, **kwargs)
