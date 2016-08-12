#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri 21 Mar 2014 10:37:40 CET

'''General utilities for building extensions'''

import os
import re
import sys
import glob
import platform

DEFAULT_PREFIXES = [
    "/opt/local",
    "/usr/local",
    "/usr",
    ]

def find_file(name, subpaths=None, prefixes=None):
  """Finds a generic file on the file system. Returns all candidates.

  This method will find all occurrences of a given name on the file system and
  will return them to the user.

  If the environment variable ``BOB_PREFIX_PATH`` is set, then it is
  considered a unix path list that is prepended to the list of prefixes to
  search for. The environment variable has the highest priority on the search
  order. The order on the variable for each path is respected.

  Parameters:

  name, str
    The name of the file to be found, including extension

  subpaths, str list
    A list of subpaths to be appended to each prefix for the search. For
    example, if you specificy ``['foo', 'bar']`` for this parameter, then
    search on ``os.path.join(prefixes[0], 'foo')``, ``os.path.join(prefixes[0],
    'bar')``, and so on. Globs are accepted in this list and resolved using
    the function :py:func:`glob.glob`.

  prefixes, str list
    A list of prefixes that will be searched prioritarily to the
    ``DEFAULT_PREFIXES`` defined in this module.

  Returns a list of filenames that exist on the filesystem, matching your
  description.
  """

  search = []

  # Priority 1: the environment
  if 'BOB_PREFIX_PATH' in os.environ:
    search += os.environ['BOB_PREFIX_PATH'].split(os.pathsep)

  # Priority 2: user passed paths
  if prefixes:
    search += prefixes

  # Priority 3: the current system executable
  search.append(os.path.dirname(os.path.dirname(sys.executable)))

  # Priority 4: the default search prefixes
  search += DEFAULT_PREFIXES

  # Make unique to avoid searching twice
  search = uniq_paths(search)

  # Exhaustive combination of paths and subpaths
  if subpaths:
    subsearch = []
    for s in search:
      for p in subpaths:
        subsearch.append(os.path.join(s, p))
      subsearch.append(s)
    search = subsearch

  # Before we do a filesystem check, filter out the unexisting paths
  tmp = []
  for k in search: tmp += glob.glob(k)
  search = tmp

  retval = []
  candidates = []
  for path in search:
    candidate = os.path.join(path, name)
    candidates.append(candidate)
    if os.path.exists(candidate): retval.append(candidate)

  return retval

def find_header(name, subpaths=None, prefixes=None):
  """Finds a header file on the file system. Returns all candidates.

  This method will find all occurrences of a given name on the file system and
  will return them to the user.

  If the environment variable ``BOB_PREFIX_PATH`` is set, then it is
  considered a unix path list that is prepended to the list of prefixes to
  search for. The environment variable has the highest priority on the search
  order. The order on the variable for each path is respected.

  Parameters:

  name, str
    The name of the file to be found, including extension

  subpaths, str list
    A list of subpaths to be appended to each prefix for the search. For
    example, if you specificy ``['foo', 'bar']`` for this parameter, then
    search on ``os.path.join(prefixes[0], 'foo')``, ``os.path.join(prefixes[0],
    'bar')``, and so on.

  prefixes, str list
    A list of prefixes that will be searched prioritarily to the
    ``DEFAULT_PREFIXES`` defined in this module.

  Returns a list of filenames that exist on the filesystem, matching your
  description.
  """

  headerpaths = []

  # arm-based system (e.g. raspberry pi 32 or 64-bit)
  if platform.machine().startswith('arm'):
    headerpaths += [os.path.join('include', 'arm-linux-gnueabihf')]

  # else, consider it intel compatible
  elif platform.architecture()[0] == '32bit':
    headerpaths += [os.path.join('include', 'i386-linux-gnu')]
  else:
    headerpaths += [os.path.join('include', 'x86_64-linux-gnu')]

  # Raspberry PI search directory (arch independent) + normal include
  headerpaths += ['include']

  # Exhaustive combination of paths and subpaths
  if subpaths:
    my_subpaths = []
    for hp in headerpaths:
      my_subpaths += [os.path.join(hp, k) for k in subpaths]
  else:
    my_subpaths = headerpaths

  return find_file(name, my_subpaths, prefixes)

def find_library(name, version=None, subpaths=None, prefixes=None,
    only_static=False):
  """Finds a library file on the file system. Returns all candidates.

  This method will find all occurrences of a given name on the file system and
  will return them to the user.

  If the environment variable ``BOB_PREFIX_PATH`` is set, then it is
  considered a unix path list that is prepended to the list of prefixes to
  search for. The environment variable has the highest priority on the search
  order. The order on the variable for each path is respected.

  Parameters:

  name, str
    The name of the module to be found. If you'd like to find libz.so, for
    example, specify ``"z"``. For libmath.so, specify ``"math"``.

  version, str
    The version of the library we are searching for. If not specified, then
    look only for the default names, such as ``libz.so`` and the such.

  subpaths, str list
    A list of subpaths to be appended to each prefix for the search. For
    example, if you specificy ``['foo', 'bar']`` for this parameter, then
    search on ``os.path.join(prefixes[0], 'foo')``, ``os.path.join(prefixes[0],
    'bar')``, and so on.

  prefixes, str list
    A list of prefixes that will be searched prioritarily to the
    ``DEFAULT_PREFIXES`` defined in this module.

  static (bool)
    A boolean, indicating if we should try only to search for static versions
    of the libraries. If not set, any would do.

  Returns a list of filenames that exist on the filesystem, matching your
  description.
  """

  libpaths = []

  # arm-based system (e.g. raspberry pi 32 or 64-bit)
  if platform.machine().startswith('arm'):
    libpaths += [os.path.join('lib', 'arm-linux-gnueabihf')]

  # else, consider it intel compatible
  elif platform.architecture()[0] == '32bit':
    libpaths += [
        os.path.join('lib', 'i386-linux-gnu'),
        os.path.join('lib32'),
        ]
  else:
    libpaths += [
        os.path.join('lib', 'x86_64-linux-gnu'),
        os.path.join('lib64'),
        ]

  libpaths += ['lib']

  # Exhaustive combination of paths and subpaths
  if subpaths:
    my_subpaths = []
    for lp in libpaths:
      my_subpaths += [os.path.join(lp, k) for k in subpaths]
  else:
    my_subpaths = libpaths

  # Extensions to consider
  if only_static:
    extensions = ['.a']
  else:
    if sys.platform == 'darwin':
      extensions = ['.dylib', '.a']
    elif sys.platform == 'win32':
      extensions = ['.dll', '.a']
    else: # linux like
      extensions = ['.so', '.a']

  # The module names can be set with or without version number
  retval = []
  if version:
    for ext in extensions:
      if sys.platform == 'darwin': # version in the middle
        libname = 'lib' + name + '.' + version + ext
      else: # version at the end
        libname = 'lib' + name + ext + '.' + version

      retval += find_file(libname, my_subpaths, prefixes)

  for ext in extensions:
    libname = 'lib' + name + ext
    retval += find_file(libname, my_subpaths, prefixes)

  return retval

def find_executable(name, subpaths=None, prefixes=None):
  """Finds an executable on the file system. Returns all candidates.

  This method will find all occurrences of a given name on the file system and
  will return them to the user.

  If the environment variable ``BOB_PREFIX_PATH`` is set, then it is
  considered a unix path list that is prepended to the list of prefixes to
  search for. The environment variable has the highest priority on the search
  order. The order on the variable for each path is respected.

  Parameters:

  name, str
    The name of the executable to be found.

  subpaths, str list
    A list of subpaths to be appended to each prefix for the search. For
    example, if you specificy ``['foo', 'bar']`` for this parameter, then
    search on ``os.path.join(prefixes[0], 'foo')``, ``os.path.join(prefixes[0],
    'bar')``, and so on.

  prefixes, str list
    A list of prefixes that will be searched prioritarily to the
    ``DEFAULT_PREFIXES`` defined in this module.

  Returns a list of filenames that exist on the filesystem, matching your
  description.
  """

  binpaths = []

  # arm-based system (e.g. raspberry pi 32 or 64-bit)
  if platform.machine().startswith('arm'):
    binpaths += [os.path.join('bin', 'arm-linux-gnueabihf')]

  # else, consider it intel compatible
  elif platform.architecture()[0] == '32bit':
    binpaths += [
        os.path.join('bin', 'i386-linux-gnu'),
        os.path.join('bin32'),
        ]
  else:
    binpaths += [
        os.path.join('bin', 'x86_64-linux-gnu'),
        os.path.join('bin64'),
        ]

  binpaths += ['bin']

  # Exhaustive combination of paths and subpaths
  if subpaths:
    my_subpaths = []
    for lp in binpaths:
      my_subpaths += [os.path.join(lp, k) for k in subpaths]
  else:
    my_subpaths = binpaths

  # The module names can be set with or without version number
  return find_file(name, my_subpaths, prefixes)

def uniq(seq, idfun=None):
  """Very fast, order preserving uniq function"""

  # order preserving
  if idfun is None:
      def idfun(x): return x
  seen = {}
  result = []
  for item in seq:
      marker = idfun(item)
      # in old Python versions:
      # if seen.has_key(marker)
      # but in new ones:
      if marker in seen: continue
      seen[marker] = 1
      result.append(item)
  return result

def uniq_paths(seq):
  """Uniq'fy a list of paths taking into consideration their real paths"""
  return uniq([os.path.realpath(k) for k in seq if os.path.exists(k)])

def egrep(filename, expression):
  """Runs grep for a given expression on each line of the file

  Parameters:

  filename, str
    The name of the file to grep for the expression

  expression
    A regular expression, that will be initialized using :py:func:`re.compile`.

  Returns a list of re matches.
  """

  retval = []

  with open(filename, 'rt') as f:
    rexp = re.compile(expression)
    for line in f:
      p = rexp.match(line)
      if p: retval.append(p)

  return retval

def load_requirements(f=None):
  """Loads the contents of requirements.txt on the given path.

  Defaults to "./requirements.txt"
  """

  def readlines(f):
    retval = [str(k.strip()) for k in f]
    return [k for k in retval if k and k[0] not in ('#', '-')]

  # if f is None, use the default ('requirements.txt')
  if f is None:
    f = 'requirements.txt'
  if isinstance(f, str):
    f = open(f, 'rt')
  # read the contents
  return readlines(f)

def find_packages(directories=['bob']):
  """This function replaces the ``find_packages`` command from ``setuptools`` to search for packages only in the given directories.
  Using this function will increase the building speed, especially when you have (links to) deep non-code-related directory structures inside your package directory.
  The given ``directories`` should be a list of top-level sub-directories of your package, where package code can be found.
  By default, it uses ``'bob'`` as the only directory to search.
  """
  from setuptools import find_packages as _original
  if isinstance(directories, str):
    directories = [directories]
  packages = []
  for d in directories:
    packages += [d]
    packages += ["%s.%s" % (d, p) for p in _original(d)]
  return packages

def link_documentation(additional_packages = ['python', 'numpy'], requirements_file = "../requirements.txt", server = None):
  """Generates a list of documented packages on pythonhosted.org for the packages read from the "requirements.txt" file and the given list of additional packages.

  Parameters:

  additional_packages : [str]
    A list of additional bob packages for which the documentation urls are added.
    By default, 'numpy' is added

  requirements_file : str or file-like
    The file (relative to the documentation directory), where to read the requirements from.
    If ``None``, it will be skipped.

  server : str or None
    The url to the server which provides the documentation.
    If ``None`` (the default), the ``BOB_DOCUMENTATION_SERVER`` environment variable is taken if existent.
    If neither ``server`` is specified, nor a ``BOB_DOCUMENTATION_SERVER`` environment variable is set, the default ``"https://pythonhosted.org/%s"`` is used.

  """

  def smaller_than(v1, v2):
    """Compares scipy/numpy version numbers"""

    c1 = v1.split('.')
    c2 = v2.split('.')[:len(c1)] #clip to the compared version
    for i in range(len(c2)):
      n1 = c1[i]
      n2 = c2[i]
      try:
        n1 = int(n1)
        n2 = int(n2)
      except ValueError:
        n1 = str(n1)
        n2 = str(n2)
      if n1 < n2: return True
      if n1 > n2: return False
    return False


  if sys.version_info[0] <= 2:
    import urllib2 as urllib
    from urllib2 import HTTPError, URLError
  else:
    import urllib.request as urllib
    import urllib.error as error
    HTTPError = error.HTTPError
    URLError = error.URLError

  # collect packages
  packages = []
  if requirements_file is not None:
    if not isinstance(requirements_file, str) or os.path.exists(requirements_file):
      packages += load_requirements(requirements_file)
  packages += additional_packages

  # standard documentation: Python
  mapping = {}
  if 'python' in packages:
    python_manual = 'http://docs.python.org/%d.%d' % sys.version_info[:2]
    print ("Adding intersphinx source %s" % python_manual)
    mapping[python_manual] = None
    packages.remove('python')

  if 'numpy' in packages:
    try:
      import numpy
      numpy_version = numpy.version.version
      if smaller_than(numpy_version, '1.5.z'):
        numpy_version = '.'.join(numpy_version.split('.')[:-1]) + '.x'
      else:
        numpy_version = '.'.join(numpy_version.split('.')[:-1]) + '.0'
    except ImportError:
      numpy_version = '1.9.1'
    numpy_manual = 'http://docs.scipy.org/doc/numpy-%s' % numpy_version

    # numpy mapping
    print ("Adding intersphinx source %s" % numpy_manual)
    mapping[numpy_manual]  = None
    packages.remove('numpy')

  if 'scipy' in packages:
    try:
      import scipy
      scipy_version = scipy.version.version
      if smaller_than(scipy_version, '0.9.0'):
        scipy_version = '.'.join(scipy_version.split('.')[:-1]) + '.x'
      else:
        scipy_version = '.'.join(scipy_version.split('.')[:-1]) + '.0'
    except ImportError:
      scipy_version = '0.16.1'
    scipy_manual = 'http://docs.scipy.org/doc/scipy-%s/reference' % scipy_version

    # numpy mapping
    print ("Adding intersphinx source %s" % scipy_manual)
    mapping[scipy_manual]  = None
    packages.remove('scipy')

  if 'matplotlib' in packages:
    matplotlib_manual = "http://matplotlib.sourceforge.net"
    print ("Adding intersphinx source %s" % matplotlib_manual)
    mapping[matplotlib_manual] = None
    packages.remove('matplotlib')

  if 'setuptools' in packages: #get the right url
    setuptools_manual = "https://setuptools.readthedocs.io/en/latest/"
    print ("Adding intersphinx source %s" % setuptools_manual)
    mapping[setuptools_manual] = None
    packages.remove('setuptools')


  # get the server for the other packages
  if server is None:
    if "BOB_DOCUMENTATION_SERVER" in os.environ:
      server = os.environ["BOB_DOCUMENTATION_SERVER"]
    else:
      server = "https://pythonhosted.org/%s"

  # check if the packages have documentation on the server
  for p in packages:
    # generate URL
    url = server % p.split()[0]

    try:
      # request url
      f = urllib.urlopen(urllib.Request(url))
      print ("Found documentation on %s; adding intersphinx source" % url)
      mapping[url] = None
    except HTTPError as exc:
      if exc.code != 404:
        # url request failed with a something else than 404 Error
        print ("Requesting URL %s returned error %s" % (url, exc))
        # notice mapping is not updated here, as the URL does not exist
    except URLError as exc:
      print ("Requesting URL %s did not succeed; are you offline? The error was %s" % (url, exc))

  return mapping
