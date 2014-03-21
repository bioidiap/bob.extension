#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Thu Mar 20 12:38:14 CET 2014

"""Helps looking for Boost on stock file-system locations"""

import os
import re
import sys
import glob
from distutils.version import LooseVersion

from .utils import uniq

def boost_version(boost_dir):

  fname = os.path.join(boost_dir, "version.hpp")
  if not os.path.exists(fname):
    fname = os.path.join(boost_dir, "boost/version.hpp")
  if not os.path.exists(fname):
    return None

  try:
    m = re.search("#\s*define\s+BOOST_VERSION\s+(\d+)", open(fname).read())
    if m:
      version_int = int(m.group(1))
      version_tuple = (version_int // 100000, (version_int // 100) % 1000,
                       version_int % 100)
      return '.'.join([str(k) for k in version_tuple])
  except:
    pass

  return None

class boost:
  """A class for capturing configuration information from boost

  Example usage:

  .. doctest::
     :options: +NORMALIZE_WHITESPACE +ELLIPSIS

     >>> from xbob.extension import boost
     >>> boost = boost('>= 1.35')
     >>> boost.include_directories()
     [...]

  You can also use this class to retrieve information about installed Boost
  libraries and link information:

  .. doctest::
     :options: +NORMALIZE_WHITESPACE +ELLIPSIS

     >>> from xbob.extension import boost
     >>> boost = boost('>= 1.35')
     >>> boost.libconfig(['python', 'random'])
     (...)

  """

  def __init__ (self, requirement=''):
    """
    Searches for the Boost library in stock locations. Allows user to override.

    If the user sets the environment variable XBOB_PREFIX_PATH, that prefixes
    the standard path locations.
    """

    default_roots = [
        "/usr",
        "/usr/local",
        "/opt/local",
        ]

    if 'XBOB_PREFIX_PATH' in os.environ:
      roots = os.environ['XBOB_PREFIX_PATH'].split(os.pathsep) + default_roots
    else:
      roots = default_roots

    globs = []
    for k in roots:
      globs += [
          os.path.join(k, 'include', 'boost') + os.sep,
          os.path.join(k, 'include', 'boost?*') + os.sep,
          ]
    valid_globs = [glob.glob(k) for k in globs]
    candidates = [d for k in valid_globs for d in k] #flatten

    if not candidates:
      raise RuntimeError("could not find any version of boost on the file system (looked at: %s)" % (', '.join(candidates)))

    if not requirement:
      self.include_directory = candidates[0]
      self.version = boost_version(self.include_directory)

    else:

      # requirement is 'operator' 'version'
      operator, required = [k.strip() for k in requirement.split(' ', 1)]

      # now check for user requirements
      for path in candidates:
        version = boost_version(path)
        available = LooseVersion(version)
        if (operator == '<' and available < required) or \
           (operator == '<=' and available <= required) or \
           (operator == '>' and available > required) or \
           (operator == '>=' and available >= required) or \
           (operator == '==' and available == required):
          self.include_directory = path
          self.version = version
        else:
          raise RuntimeError("could not find the required (%s) version of boost on the file system (looked at: %s)" % (requirement, ', '.join(candidates)))

    # normalize
    self.include_directory = os.path.normpath(self.include_directory)


  def libconfig(self, modules, only_static=False,
      templates=['boost_%(name)s-mt-%(py)s',
        'boost_%(name)s-mt', 'boost_%(name)s']):
    """Returns a tuple containing the library configuration for requested
    modules.

    This function respects the path location where the include files for Boost
    are installed.

    Parameters:

    modules (list of strings)
      A list of string specifying the requested libraries to search for. For
      example, to search for `libboost_mpi.so`, pass only ``mpi``.

    static (bool)
      A boolean, indicating if we should try only to search for static versions
      of the libraries. If not set, any would do.

    templates (list of template strings)
      A list that defines in which order to search for libraries on the default
      search path, defined by ``self.include_directory``. Tune this list if you
      have compiled specific versions of Boost with support to multi-threading
      (``-mt``), debug (``-g``), STLPORT (``-p``) or required to insert
      compiler, the underlying thread API used or your own namespace.

      Here are the keywords you can use:

      %(name)s
        resolves to the module name you are searching for

      %(version)s
        resolves to the current boost version string (e.g. ``'1.50.0'``)

      %(py)s
        resolves to the string ``'pyXY'`` where ``XY`` represent the major and
        minor versions of the current python interpreter.

      Example templates:

      * ``'boost_%(name)s-mt'``
      * ``'boost_%(name)s'``
      * ``'boost_%(name)s-gcc43-%(version)s'``

    Returns:

    directories (list of strings)
      A list of directories indicating where the libraries are installed

    libs (list of strings)
      A list of strings indicating the names of the libraries you can use
    """

    if only_static:
      extensions = ['.a']
    else:
      if sys.platform == 'darwin':
        extensions = ['.dylib', '.a']
      elif sys.platform == 'win32':
        extensions = ['.dll', '.a']
      else: # linux like
        extensions = ['.so', '.a']

    prefix = os.path.dirname(os.path.dirname(self.include_directory))

    libpaths = [
        os.path.join(prefix, 'lib64'),
        os.path.join(prefix, 'lib32'),
        os.path.join(prefix, 'lib'),
        ]

    py = 'py%d%d' % sys.version_info[:2]

    def paths(module):
      """Yields all possible paths for a module in good order"""

      for extension in extensions:
        for template in templates:
          for libpath in libpaths:
            modname = template % dict(name=module, version=self.version, py=py)
            yield modname, os.path.join(libpath, 'lib' + modname + extension)

    items = {}
    for module in modules:
      for modname, path in paths(module):
        if os.path.exists(path):
          items[module] = (os.path.dirname(path), modname)
          break

    # checks all modules were found, reports
    for module in modules:
      if module not in items:
        raise RuntimeError("cannot find required boost module `%s', searched as `%s'" % (module, ', '.join(paths(module))))

    libpaths, libraries = zip(*items.values())

    return uniq(libpaths), uniq(libraries)

  def macros(self):
    """Returns package availability and version number macros

    This method returns a python list with 2 macros indicating package
    availability and a version number, using standard GNU compatible names. For
    example, if the package is named ``foo`` and its version is ``1.4``, this
    command would return:

    .. doctest::
       :options: +NORMALIZE_WHITESPACE +ELLIPSIS

       >>> from xbob.extension import boost
       >>> pkg = boost('>= 1.34')
       >>> pkg.macros()
       [('HAVE_BOOST', '1'), ('BOOST_VERSION', '"..."')]

    """
    return [('HAVE_BOOST', '1'), ('BOOST_VERSION', '"%s"' % self.version)]

