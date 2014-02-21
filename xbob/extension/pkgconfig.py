#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 16 Oct 10:08:42 2013 CEST

import os
import subprocess
import logging

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

def call_pkgconfig(cmd, paths=None):
  """Runs a command as a subprocess and raises if that does not work

  Returns the exit status, stdout and stderr.
  """

  # if the user has passed their own paths, add it to the environment
  env = os.environ
  if paths is not None:
    env = os.environ.copy()
    var = os.pathsep.join(paths)
    old = env.get('PKG_CONFIG_PATH', False)
    env['PKG_CONFIG_PATH'] = os.pathsep.join([var, old]) if old else var

  # calls the lua creation script using the parameters
  cmd = ['pkg-config'] + [str(k) for k in cmd]
  subproc = subprocess.Popen(
      cmd,
      env=env,
      stderr=subprocess.PIPE,
      stdout=subprocess.PIPE
      )

  logging.debug("Running `%s'" % (" ".join(cmd),))
  stdout, stderr = subproc.communicate()

  # handles py3k string conversion, if necessary
  if isinstance(stdout, bytes) and not isinstance(stdout, str):
    stdout = stdout.decode('utf8')

  if isinstance(stderr, bytes) and not isinstance(stderr, str):
    stderr = stderr.decode('utf8')

  # always print the stdout
  logger = logging.getLogger('pkgconfig')
  for k in stdout.split('\n'):
    if k: logger.debug(k)

  return subproc.returncode, stdout, stderr

def version():
  """Determines the version of pkg-config which is installed"""

  status, stdout, stderr = call_pkgconfig(['--version'])

  if status != 0:
    raise RuntimeError("pkg-config is not installed - please do it")

  return stdout.strip()

class pkgconfig:
  """A class for capturing configuration information from pkg-config

  Example usage:

    .. doctest::
       :options: +NORMALIZE_WHITESPACE +ELLIPSIS

       >>> glibc = pkgconfig('glibc')
       >>> glibc.include_directories() # doctest: SKIP
       ['/usr/include']
       >>> glibc.library_directories() # doctest: SKIP
       ['/usr/lib']

  If the package does not exist, a RuntimeError is raised. All calls to any
  methods of a ``pkgconfig`` object are translated into a subprocess call that
  queries for that specific information. If ``pkg-config`` fails, a
  RuntimeError is raised.
  """

  def __init__(self, name, paths=None):
    """Constructor

    Parameters:

    name
      The name of the package of interest, as you would pass on the command
      line

    extra_paths
      Search paths to be added to the environment's PKG_CONFIG_PATH to search
      for packages.

    Equivalent command line version:

    .. code-block:: sh

       $ PKG_CONFIG_PATH=<paths> pkg-config <name>

    """

    status, stdout, stderr = call_pkgconfig(['--modversion', name], paths)

    if status != 0:
      raise RuntimeError("pkg-config package `%s' was not found" % name)

    self.name = name
    self.version = stdout.strip()
    self.paths = paths

  def __xcall__(self, cmd):
    """Calls call_pkgconfig() with self.name and self.paths"""

    return call_pkgconfig(cmd + [self.name], self.paths)

  def __cmp__(self, other):
    """Compares this package with a version number

    We create a new ``distutils.version.LooseVersion`` object out of your input
    argument and then, compare it to our own version, returning the result.

    Returns an integer smaller than zero if this package's version number is
    smaller than the provided value. Returns zero in case of a match and
    greater than zero in the other case.
    """

    from distutils.version import LooseVersion
    return cmp(self.version, LooseVersion(other))

  def __ge__(self, other):
    from distutils.version import LooseVersion
    return LooseVersion(self.version) >= LooseVersion(other)

  def __gt__(self, other):
    from distutils.version import LooseVersion
    return LooseVersion(self.version) > LooseVersion(other)

  def __le__(self, other):
    from distutils.version import LooseVersion
    return LooseVersion(self.version) <= LooseVersion(other)

  def __lt__(self, other):
    from distutils.version import LooseVersion
    return LooseVersion(self.version) < LooseVersion(other)

  def __eq__(self, other):
    from distutils.version import LooseVersion
    return LooseVersion(self.version) == LooseVersion(other)

  def __ne__(self, other):
    from distutils.version import LooseVersion
    return LooseVersion(self.version) != LooseVersion(other)

  def include_directories(self):
    """Returns a pre-processed list containing include directories.

    Equivalent command line version:

    .. code-block:: sh

       $ PKG_CONFIG_PATH=<paths> pkg-config --cflags-only-I <name>

    """

    status, stdout, stderr = self.__xcall__(['--cflags-only-I'])

    if status != 0:
      raise RuntimeError("error querying --cflags-only-I for package `%s': %s" % (self.name, stderr))

    retval = []
    for token in stdout.split():
      retval.append(token[2:])

    return uniq(retval)

  def cflags_other(self):
    """Returns a pre-processed dictionary containing compilation options.

    Equivalent command line version:

    .. code-block:: sh

       $ PKG_CONFIG_PATH=<paths> pkg-config --cflags-only-other <name>

    The returned dictionary contains two entries ``extra_compile_args`` and
    ``define_macros``. The ``define_macros`` entries are ready for deployment
    in the ``setup()`` function of your package.
    """

    status, stdout, stderr = self.__xcall__(['--cflags-only-other'])

    if status != 0:
      raise RuntimeError("error querying --cflags-only-other for package `%s': %s" % (self.name, stderr))

    flag_map = {
        '-D': 'define_macros',
        }

    kw = {}

    for token in stdout.split():
      if token[:2] in flag_map:
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])

      else: # throw others to extra_link_args
        kw.setdefault('extra_compile_args', []).append(token)

    # make it uniq
    for k, v in kw.items(): kw[k] = uniq(v)

    # for macros, separate them so they can be plugged on C/C++ extensions
    if 'define_macros' in kw:
      for k, string in enumerate(kw['define_macros']):
        if string.find('=') != -1:
          kw['define_macros'][k] = string.split('=', 2)
        else:
          kw['define_macros'][k] = (string, None)

    return kw

  def libraries(self):
    """Returns a pre-processed list containing libraries to link against

    Equivalent command line version:

    .. code-block:: sh

       $ PKG_CONFIG_PATH=<paths> pkg-config --libs-only-l <name>

    """

    status, stdout, stderr = self.__xcall__(['--libs-only-l'])

    if status != 0:
      raise RuntimeError("error querying --libs-only-l for package `%s': %s" % (self.name, stderr))

    retval = []
    for token in stdout.split():
      retval.append(token[2:])

    return uniq(retval)

  def library_directories(self):
    """Returns a pre-processed list containing library directories.

    Equivalent command line version:

    .. code-block:: sh

       $ PKG_CONFIG_PATH=<paths> pkg-config --libs-only-L <name>

    """

    status, stdout, stderr = self.__xcall__(['--libs-only-L'])

    if status != 0:
      raise RuntimeError("error querying --libs-only-L for package `%s': %s" % (self.name, stderr))

    retval = []
    for token in stdout.split():
      retval.append(token[2:])

    return uniq(retval)

  def extra_link_args(self):
    """Returns a pre-processed list containing extra link arguments.

    Equivalent command line version:

    .. code-block:: sh

       $ PKG_CONFIG_PATH=<paths> pkg-config --libs-only-other <name>

    """

    status, stdout, stderr = self.__xcall__(['--libs-only-other'])

    if status != 0:
      raise RuntimeError("error querying --libs-only-other for package `%s': %s" % (self.name, stderr))

    return stdout.strip().split()

  def variable_names(self):
    """Returns a list with all variable names know to this package

    Equivalent command line version:

    .. code-block:: sh

       $ PKG_CONFIG_PATH=<paths> pkg-config --print-variables <name>

    """

    status, stdout, stderr = self.__xcall__(['--print-variables'])

    if status != 0:
      raise RuntimeError("error querying --print-variables for package `%s': %s" % (self.name, stderr))

    return stdout.strip().split()

  def variable(self, name):
    """Returns a variable with a specific name (if it exists)

    Equivalent command line version:

    .. code-block:: sh

       $ PKG_CONFIG_PATH=<paths> pkg-config --variable=<variable-name> <name>

    .. warning::

       If a variable does not exist in a package, pkg-config does not signal an
       error. Instead, it returns an empty string. So, do we.
    """

    status, stdout, stderr = self.__xcall__(['--variable=%s' % name])

    if status != 0:
      raise RuntimeError("error querying --variable=%s for package `%s': %s" % (name, self.name, stderr))

    return stdout.strip()

  def package_macros(self):
    """Returns package availability and version number macros

    This method returns a python list with 2 macros indicating package
    availability and a version number, using standard GNU compatible names. For
    example, if the package is named ``foo`` and its version is ``1.4``, this
    command would return:

    .. code-block:: sh

       >>> foo = pkgconfig('foo')
       >>> foo.package_macros()
       [('HAVE_FOO', '1'), ('FOO_VERSION', '"1.4"')]

    """
    from re import sub
    NAME = sub(r'[\.\-\s]', '_', self.name.upper())
    return [('HAVE_' + NAME, '1'), (NAME + '_VERSION', '"%s"' % self.version)]

__all__ = ['pkgconfig']
