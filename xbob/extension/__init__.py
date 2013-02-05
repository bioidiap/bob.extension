#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 28 Jan 2013 16:40:27 CET 

"""A custom build class for Bob/Python extensions
"""

import subprocess
from distutils.extension import Extension as ExtensionBase

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
    raise RuntimeError, "PkgConfig did not find package %s. Output:\n%s" % \
        (package, output.strip())

  kw = {}

  for token in output.split():
    if flag_map.has_key(token[:2]):
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

  for k, v in kw.iteritems(): # remove duplicated
    kw[k] = uniq(v)

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

    if kwargs.has_key('pkgconfig') and kwargs['pkgconfig']:
      if isinstance(kwargs['pkgconfig'], (str, unicode)):
        modules.append(kwargs['pkgconfig'])
      else:
        modules.extend(kwargs['pkgconfig'])

    if kwargs.has_key('pkgconfig'): del kwargs['pkgconfig']

    # Only one instance of each
    modules = uniq(modules)

    # Mixing
    parameters = {
        'include_dirs': [],
        'library_dirs': [],
        'libraries': [],
        }

    for m in modules:
      config = pkgconfig(m)
      for key in parameters.iterkeys():
        if config.has_key(key) and config[key]:
          parameters[key].extend(config[key])

    # Filter and make unique
    for key in parameters.iterkeys():
      parameters[key] = uniq(parameters[key])
    
      # Tune input parameters if they were set
      if kwargs.has_key(key): kwargs.extend(parameters[key])
      else: kwargs[key] = parameters[key]

    # Set the runtime_library_dirs specially
    if kwargs.has_key('runtime_library_dirs'):
      kwargs.extend(parameters('runtime_library_dirs'))
    else:
      kwargs['runtime_library_dirs'] = parameters['library_dirs']

    # Make sure the language is correctly set to C++
    kwargs['language'] = 'c++'

    # Run the constructor for the base class
    ExtensionBase.__init__(self, *args, **kwargs)
