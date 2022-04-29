#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Mar 2014 12:43:48 CET

"""Tests for file search utilities
"""

import os
import sys

import pkg_resources

from .utils import find_packages, link_documentation, load_requirements


def test_requirement_readout():

    from io import StringIO as stringio

    f = """ # this is my requirements file
package-a >= 0.42
package-b
package-c
#package-e #not to be included

package-z
--no-index
-e http://example.com/mypackage-1.0.4.zip
"""

    result = load_requirements(stringio(f))
    expected = ["package-a >= 0.42", "package-b", "package-c", "package-z"]
    assert result == expected


def test_find_packages():
    # tests the find-packages command inside the bob.extension package

    basedir = pkg_resources.resource_filename("bob.extension", ".")
    packages = find_packages(os.path.abspath(os.path.join(basedir, "..")))

    site_packages = os.path.dirname(os.path.commonprefix(packages))
    packages = [os.path.relpath(k, site_packages) for k in packages]

    assert "bob" in packages
    assert "bob.extension" in packages
    assert "bob.extension.scripts" in packages


def test_documentation_generation():
    from io import StringIO as stringio

    f = """ # this is my requirements file
package-a >= 0.42
package-b
package-c
#package-e #not to be included
setuptools

package-z
--no-index
-e http://example.com/mypackage-1.0.4.zip
"""

    # keep the tests quiet
    _stdout = sys.stdout

    try:
        devnull = open(os.devnull, "w")
        sys.stdout = devnull

        # test NumPy and SciPy docs
        try:
            import numpy  # noqa: F401

            result = link_documentation(["numpy"], None)
            assert len(result) == 1
            key = list(result.keys())[0]
            assert "numpy" in key
        except ImportError:
            pass

        try:
            import scipy  # noqa: F401

            result = link_documentation(["scipy"], None)
            assert len(result) == 1
            key = list(result.keys())[0]
            assert "scipy" in key
        except ImportError:
            pass

        try:
            import matplotlib  # noqa: F401

            result = link_documentation(["matplotlib"], None)
            assert len(result) == 1
            key = list(result.keys())[0]
            assert "matplotlib" in key
        except ImportError:
            pass

        # test pypi packages
        additional_packages = [
            "python",
            "matplotlib",
            "bob.extension",
            "gridtk",
            "other.bob.package",
        ]

        # test linkage to official documentation
        server = "http://www.idiap.ch/software/bob/docs/bob/%s/master/"
        os.environ["BOB_DOCUMENTATION_SERVER"] = server
        result = link_documentation(additional_packages, stringio(f))
        expected = [
            "https://docs.python.org/%d.%d/" % sys.version_info[:2],
            "https://matplotlib.org/stable/",
            "https://setuptools.readthedocs.io/en/latest/",
            server % "bob.extension",
            server % "gridtk",
        ]
        result = [k[0] for k in result.values()]
        assert sorted(result) == sorted(expected)

    finally:
        sys.stdout = _stdout


def test_get_config():
    # Test the generic get_config() function
    import bob.extension

    cfg = bob.extension.get_config()
    splits = cfg.split("\n")
    assert splits[0].startswith("bob.extension")
    assert splits[1].startswith("* Python dependencies")
    assert any([s.startswith("  - setuptools") for s in splits[2:]])

    cfg = bob.extension.get_config(
        "setuptools", {"MyPackage": {"my_dict": 42}}, 0x0204
    )
    splits = cfg.split("\n")
    assert splits[0].startswith("setuptools")
    assert "api=0x0204" in splits[0]
    assert splits[1].startswith("* C/C++ dependencies")
    assert any([s.startswith("  - MyPackage") for s in splits[2:]])
