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
     >>> boost = boost('>= 1.47')
     >>> boost.include_directories()
     [...]

  You can also use this class to retrieve information about installed Boost
  libraries and link information:

  .. doctest::
     :options: +NORMALIZE_WHITESPACE +ELLIPSIS

     >>> from xbob.extension import boost
     >>> boost = boost('>= 1.47')
     >>> boost.library_configuration(['python', 'random'])
     (...)

  """

  def __init__ (self, requirement=''):
    """
    Searches for the Boost library in stock locations. Allows user to override.

    If the user sets the environment variable BOOST_PREFIX_PATH, then **only**
    the user defined path locations are searched.
    """

    if 'BOOST_PREFIX_PATH' in os.environ:
      globs = os.environ['BOOST_PREFIX_PATH']
      candidates = [k for k in globs.split(os.pathsep) if os.path.exists(k)]
    else:
      globs = [
        "/usr/include/boost/",
        "/usr/include/boost?*/",
        "/usr/local/boost/",
        "/usr/local/boost?*/",
        "/opt/local/include/boost/",
        "/opt/local/include/boost?*/",
        "/usr/local/include/boost/",
        "/usr/local/include/boost?*/",
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

    directory (string)
      A directory indicating where the libraries are installed

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

    dname = os.path.dirname
    libpath = os.path.join(dname(dname(self.include_directory)), 'lib')

    py = 'py%d%d' % sys.version_info[:2]

    libraries = []
    for k in modules:
      for extension in extensions:
        found = False
        for template in templates:
          modname = template % dict(name=k, version=self.version, py=py)
          path = os.path.join(libpath, 'lib' + modname + extension)
          if os.path.exists(path):
            libraries.append(modname)
            found = True
            break
        if found: break

    return libpath, libraries
