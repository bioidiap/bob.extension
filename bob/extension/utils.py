#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri 21 Mar 2014 10:37:40 CET

"""General utilities for building extensions"""

import os
import re
import sys

import pkg_resources


def load_requirements(f=None):
    """Loads the contents of requirements.txt on the given path.

    Defaults to "./requirements.txt"
    """

    def readlines(f):
        retval = [str(k.strip()) for k in f]
        return [k for k in retval if k and k[0] not in ("#", "-")]

    # if f is None, use the default ('requirements.txt')
    if f is None:
        f = "requirements.txt"
    if isinstance(f, str):
        f = open(f, "rt")
    # read the contents
    return readlines(f)


def find_packages(directories=["bob"]):
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


def link_documentation(
    additional_packages=["python", "numpy"],
    requirements_file="../requirements.txt",
    server=None,
):
    """Generates a list of documented packages on our documentation server for the packages read from the "requirements.txt" file and the given list of additional packages.

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
      If neither ``server`` is specified, nor a ``BOB_DOCUMENTATION_SERVER`` environment variable is set, the default ``"http://www.idiap.ch/software/bob/docs/bob/%(name)s/%(version)s/"`` is used.

    """

    def smaller_than(v1, v2):
        """Compares scipy/numpy version numbers"""

        c1 = v1.split(".")
        c2 = v2.split(".")[: len(c1)]  # clip to the compared version
        for i in range(len(c2)):
            n1 = c1[i]
            n2 = c2[i]
            try:
                n1 = int(n1)
                n2 = int(n2)
            except ValueError:
                n1 = str(n1)
                n2 = str(n2)
            if n1 < n2:
                return True
            if n1 > n2:
                return False
        return False

    import urllib.error as error
    import urllib.request as urllib

    HTTPError = error.HTTPError
    URLError = error.URLError

    # collect packages are automatically included in the list of indexes
    packages = []
    version_re = re.compile(r"\s*[\<\>=]+\s*")
    if requirements_file is not None:
        if not isinstance(requirements_file, str) or os.path.exists(
            requirements_file
        ):
            requirements = load_requirements(requirements_file)
            packages += [version_re.split(k)[0] for k in requirements]
    packages += additional_packages

    def _add_index(name, addr, packages=packages):
        """Helper to add a new doc index to the intersphinx catalog

        Parameters:

          name (str): Name of the package that will be added to the catalog
          addr (str): The URL (except the ``objects.inv`` file), that will be added

        """

        if name in packages:
            print("Adding intersphinx source for `%s': %s" % (name, addr))
            mapping[name] = (addr, None)
            packages = [k for k in packages if k != name]

    def _add_numpy_index():
        """Helper to add the numpy manual"""

        try:
            import numpy

            ver = numpy.version.version
            ver = ".".join(ver.split(".")[:-1])
            _add_index("numpy", "https://numpy.org/doc/%s/" % ver)

        except ImportError:
            _add_index("numpy", "https://numpy.org/devdocs/")

    def _add_scipy_index():
        """Helper to add the scipy manual"""

        try:
            import scipy

            ver = scipy.version.version
            if smaller_than(ver, "0.9.0"):
                ver = ".".join(ver.split(".")[:-1]) + ".x"
            else:
                ver = ".".join(ver.split(".")[:-1]) + ".0"
            _add_index(
                "scipy", "https://docs.scipy.org/doc/scipy-%s/reference/" % ver
            )

        except ImportError:
            _add_index("scipy", "https://docs.scipy.org/doc/scipy/reference/")

    def _add_click_index():
        """Helper to add the click manual"""

        import click

        major, minor = [int(x) for x in click.__version__.split(".")[0:2]]
        if major < 8:
            ver = f"{major}.x"
        else:
            ver = f"{major}.{minor}.x"
        _add_index("click", "https://click.palletsprojects.com/en/%s/" % ver)

    mapping = {}

    # add indexes for common packages used in Bob
    _add_index(
        "python", "https://docs.python.org/%d.%d/" % sys.version_info[:2]
    )
    _add_numpy_index()
    _add_index("scipy", "https://docs.scipy.org/doc/scipy/")
    _add_index("matplotlib", "https://matplotlib.org/stable/")
    _add_index("setuptools", "https://setuptools.readthedocs.io/en/latest/")
    _add_index("six", "https://six.readthedocs.io")
    _add_index("sqlalchemy", "https://docs.sqlalchemy.org/en/latest/")
    _add_index("docopt", "https://docopt.readthedocs.io/en/latest/")
    _add_index("scikit-learn", "https://scikit-learn.org/stable/")
    _add_index("scikit-image", "https://scikit-image.org/docs/dev/")
    _add_index("pillow", "https://pillow.readthedocs.io/en/latest/")
    _add_index("PIL", "https://pillow.readthedocs.io/en/latest/")
    _add_index("pandas", "https://pandas.pydata.org/pandas-docs/stable/")
    _add_index("dask", "https://docs.dask.org/en/latest/")
    _add_index("dask-jobqueue", "https://jobqueue.dask.org/en/latest/")
    _add_index("distributed", "https://distributed.dask.org/en/latest/")
    _add_click_index()
    _add_index("torch", "https://pytorch.org/docs/stable/")
    _add_index("xarray", "https://xarray.pydata.org/en/stable/")
    _add_index("h5py", "https://docs.h5py.org/en/stable/")

    # get the server for the other packages
    if server is None:
        if "BOB_DOCUMENTATION_SERVER" in os.environ:
            server = os.environ["BOB_DOCUMENTATION_SERVER"]
        else:
            server = "http://www.idiap.ch/software/bob/docs/bob/%(name)s/%(version)s/|http://www.idiap.ch/software/bob/docs/bob/%(name)s/%(version)s/sphinx|http://www.idiap.ch/software/bob/docs/bob/%(name)s/master/|http://www.idiap.ch/software/bob/docs/bob/%(name)s/master/sphinx"

    # array support for BOB_DOCUMENTATION_SERVER
    # transforms "(file:///path/to/dir  https://example.com/dir| http://bla )"
    # into ["file:///path/to/dir", "https://example.com/dir", "http://bla"]
    # so, trim eventual parenthesis/white-spaces and splits by white space or |
    if server.strip():
        server = re.split(r"[|\s]+", server.strip("() "))
    else:
        server = []

    # check if the packages have documentation on the server
    for p in packages:
        if p in mapping:
            continue  # do not add twice...

        for s in server:
            # generate URL
            package_name = p.split()[0]
            if s.count("%s") == 1:  # old style
                url = s % package_name
            else:  # use new style, with mapping, try to link against specific version
                try:
                    version = (
                        "v" + pkg_resources.require(package_name)[0].version
                    )
                except pkg_resources.DistributionNotFound:
                    version = "stable"  # package is not a runtime dep, only referenced
                url = s % {"name": package_name, "version": version}

            try:
                # otherwise, urlopen will fail
                if url.startswith("file://"):
                    urllib.urlopen(urllib.Request(url + "objects.inv"))
                    url = url[7:]  # intersphinx does not like file://
                else:
                    urllib.urlopen(urllib.Request(url))

                # request url
                print(
                    "Found documentation for %s on %s; adding intersphinx source"
                    % (p, url)
                )
                mapping[p] = (url, None)
                break  # inner loop, for server, as we found a candidate!

            except HTTPError as exc:
                if exc.code != 404:
                    # url request failed with a something else than 404 Error
                    print("Requesting URL %s returned error: %s" % (url, exc))
                    # notice mapping is not updated here, as the URL does not exist

            except URLError as exc:
                print(
                    "Requesting URL %s did not succeed (maybe offline?). "
                    "The error was: %s" % (url, exc)
                )

            except IOError as exc:
                print("Path %s does not exist. The error was: %s" % (url, exc))

    return mapping
