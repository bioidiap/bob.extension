# import all packages with direct dependencies
# (This will load their pure C++ libraries, if needed)
import bob.blitz
# ... in fact, bob.blitz does not have a C++ library and it would not be needed to import it here
# ... nevertheless, it stays here not to forget it!


# import the C++ function ``reverse`` from the library
from ._library import reverse

# import the ``version`` library as well
from . import version as _version
version = _version.module

def get_config():
  """Returns a string containing the configuration information.
  """

  import pkg_resources

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s (%s)\n" % (this.key, this.version, this.location)
  retval += "  - c/c++ dependencies:\n"
  for k in sorted(_version.externals): retval += "    - %s: %s\n" % (k, _version.externals[k])
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
