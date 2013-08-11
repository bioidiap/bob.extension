#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 28 Jan 2013 16:40:27 CET

"""A custom build class for Bob/Python extensions
"""

import os
import string
import subprocess
from distutils.extension import Extension as ExtensionBase
from setuptools.command.build_ext import build_ext as build_ext_base

def pkgconfig(package):

  def uniq(seq, idfun=None):
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

  cmd = [
      'pkg-config',
      '--modversion',
      package,
      ]

  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT)

  output = proc.communicate()[0]

  if proc.returncode != 0:
    raise RuntimeError("PkgConfig did not find package %s. Output:\n%s" % \
        (package, output.strip()))

  version = output.strip()

  flag_map = {
      '-I': 'include_dirs',
      '-L': 'library_dirs',
      '-l': 'libraries',
      }

  cmd = [
      'pkg-config',
      '--libs',
      '--cflags',
      package,
      ]

  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT)

  output = proc.communicate()[0]

  if proc.returncode != 0:
    raise RuntimeError("PkgConfig did not find package %s. Output:\n%s" % \
        (package, output.strip()))

  kw = {}

  for token in output.split():
    if token[:2] in flag_map:
      kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])

    elif token[0] == '-': # throw others to extra_link_args
      kw.setdefault('extra_compile_args', []).append(token)

    else: # these are maybe libraries
      import os
      if os.path.exists(token):
        dirname = os.path.dirname(token)
        if dirname not in kw.get('library_dirs', []):
          kw.setdefault('library_dirs', []).append(dirname)

        bname = os.path.splitext(os.path.basename(token))[0][3:]
        if bname not in kw.get('libraries', []):
          kw.setdefault('libraries', []).append(bname)

  for k, v in kw.items(): # remove duplicated
    kw[k] = uniq(v)

  try:
    # Python 3 style
    maketrans = ''.maketrans
  except AttributeError:
    # fallback for Python 2
    from string import maketrans

  # adds version and HAVE flags
  PACKAGE = package.upper().translate(maketrans(" -", "__"))
  kw['define_macros'] = [
      ('HAVE_%s' % PACKAGE, '1'),
      ('%s_VERSION' % PACKAGE, '"%s"' % version),
      ]

  return kw

def uniq(seq):
  """Uniqu-fy preserving order"""

  seen = set()
  seen_add = seen.add
  return [ x for x in seq if x not in seen and not seen_add(x)]

class Extension(ExtensionBase):
  """Extension building with Bob/Python bindings.

  See the documentation for :py:class:`distutils.extension.Extension` for more
  details on input parameters.
  """

  def __init__(self, *args, **kwargs):
    """Initialize the extension with parameters.

    Bob/Python adds a single parameter to the standard arguments of the
    constructor:

    pkgconfig : [list]

      This should be a list of strings indicating the name of the bob
      (pkg-config) modules you would like to have linked to your extension
      **additionally** to ``bob-python``. Candidates are module names like
      "bob-machine" or "bob-math".

      For convenience, you can also specify "opencv" or other 'pkg-config'
      registered packages as a dependencies.
    """

    modules = ['bob-python']

    if 'pkgconfig' in kwargs and kwargs['pkgconfig']:
      if isinstance(kwargs['pkgconfig'], str):
        modules.append(kwargs['pkgconfig'])
      else:
        modules.extend(kwargs['pkgconfig'])

    if 'pkgconfig' in kwargs: del kwargs['pkgconfig']

    # Only one instance of each
    modules = uniq(modules)

    # Mixing
    parameters = {
        'include_dirs': [],
        'library_dirs': [],
        'libraries': [],
        'define_macros': [],
        }

    for m in modules:
      config = pkgconfig(m)
      for key in parameters.keys():
        if key in config and config[key]:
          parameters[key].extend(config[key])

    # Reset the include_dirs to use '-isystem'
    include_dirs = ['-isystem%s' % k for k in parameters['include_dirs']]
    if 'extra_compile_args' in kwargs:
      kwargs['extra_compile_args'].extend(include_dirs)
    else:
      kwargs['extra_compile_args'] = include_dirs
    del parameters['include_dirs']

    # Filter and make unique
    for key in parameters.keys():
      parameters[key] = uniq(parameters[key])

      # Tune input parameters if they were set
      if key in kwargs: kwargs[key].extend(parameters[key])
      else: kwargs[key] = parameters[key]

    # Set the runtime_library_dirs specially
    if 'runtime_library_dirs' in kwargs:
      kwargs['runtime_library_dirs'].extend(parameters('runtime_library_dirs'))
    else:
      kwargs['runtime_library_dirs'] = parameters['library_dirs']

    # Make sure the language is correctly set to C++
    kwargs['language'] = 'c++'

    # Run the constructor for the base class
    ExtensionBase.__init__(self, *args, **kwargs)

class build_ext(build_ext_base):
  '''Customized extension to build bob.python bindings in the expected way'''

  linker_is_smart = None

  def __init__(self, *args, **kwargs):
    build_ext_base.__init__(self, *args, **kwargs)

  def build_extension(self, ext):
    '''Concretely builds the extension given as input'''

    def linker_can_remove_symbols(linker):
      '''Tests if the `ld` linker can remove unused symbols from linked
      libraries. In this case, use the --no-as-needed flag during link'''

      import tempfile
      f, name = tempfile.mkstemp()
      del f

      cmd = linker + ['-Wl,--no-as-needed', '-lm', '-o', name]
      proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT)
      output = proc.communicate()[0]
      if os.path.exists(name): os.unlink(name)
      return True if proc.returncode == 0 else False

    def ld_ok(opt):
      '''Tells if a certain option is a go for the linker'''

      if opt.find('-L') == 0: return False
      return True

    # Some clean-up on the linker which is screwed up...
    self.compiler.linker_so = [k for k in self.compiler.linker_so if ld_ok(k)]

    if self.linker_is_smart is None:
      self.linker_is_smart = linker_can_remove_symbols(self.compiler.linker_so)
      if self.linker_is_smart: self.compiler.linker_so += ['-Wl,--no-as-needed']

    if hasattr(self.compiler, 'dll_libraries') and \
        self.compiler.dll_libraries is None:
      self.compiler.dll_libraries = []

    build_ext_base.build_extension(self, ext)
