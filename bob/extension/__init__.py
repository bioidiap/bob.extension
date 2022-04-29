#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Amir Mohammadi <amir.mohammadi@idiap.ch>

"""A custom build class for Pkg-config based extensions
"""

import contextlib
import logging

import pkg_resources

from .rc_config import _loadrc

logger = logging.getLogger(__name__)


__version__ = pkg_resources.require(__name__)[0].version

# Loads the rc user preferences
rc = _loadrc()
"""The content of the global configuration file loaded as a dictionary.
The value for any non-existing key is ``None``."""


@contextlib.contextmanager
def rc_context(dict):
    """A context manager for bob.extension.rc.
    You can use this context manager to temporarily change a value in
    ``bob.extension.rc``.

    Example
    -------
    >>> from bob.extension import rc, rc_context
    >>> assert rc.get("non-existing-key") is None
    >>> with rc_context({"non-existing-key": 1}):
    ...     a = rc.get("non-existing-key")
    >>> a
    1
    """
    old_rc = rc.copy()
    try:
        rc.update(dict)
        yield
    finally:
        rc.clear()
        rc.update(old_rc)


def get_config(package=__name__, externals=None, api_version=None):
    """Returns a string containing the configuration information for the given ``package`` name.
    By default, it returns the configuration of this package.

    This function can be reused by other packages.
    If these packages have external C or C++ dependencies, the ``externals`` dictionary can be specified.
    Also, if the package provides an API version, it can be specified.

    **Keyword parameters:**

    package : *str*
      The name of the package to get the configuration information from.
      Usually, the ``__name__`` of the package.

    externals : *{dep: description}*
      A dictionary of external C or C++ dependencies, with the ``dep``endent package name as key, and a free ``description`` as value.

    api_version : *int* (usually in hexadecimal)
      The API version of the ``package``, if any.
    """

    import pkg_resources

    packages = pkg_resources.require(package)
    this = packages[0]
    deps = packages[1:]

    if api_version is not None:
        retval = "%s: %s [api=0x%04x] (%s)\n" % (
            this.key,
            this.version,
            api_version,
            this.location,
        )
    else:
        retval = "%s: %s (%s)\n" % (this.key, this.version, this.location)

    if externals is not None:
        retval += "* C/C++ dependencies:\n"
        for k in sorted(externals):
            retval += "  - %s: %s\n" % (k, externals[k])

    if len(deps):
        retval += "* Python dependencies:\n"
        # sort python dependencies and make them unique
        deps_dict = {}
        for d in deps:
            deps_dict[d.key] = d
        for k in sorted(deps_dict):
            retval += "  - %s: %s (%s)\n" % (
                deps_dict[k].key,
                deps_dict[k].version,
                deps_dict[k].location,
            )

    return retval.strip()


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith("_")]
