#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Tests for the python-based config functionality"""


import os

import numpy
import pkg_resources

from .config import load, mod_to_context

path = pkg_resources.resource_filename("bob.extension", "data")


def test_basic():

    c = load([os.path.join(path, "basic_config.py")])
    assert hasattr(c, "a") and c.a == 1
    assert hasattr(c, "b") and c.b == 3

    ctx = mod_to_context(c)
    assert ctx == {"a": 1, "b": 3}


def test_basic_with_context():

    c = load([os.path.join(path, "basic_config.py")], {"d": 35, "a": 0})
    assert hasattr(c, "a") and c.a == 1
    assert hasattr(c, "b") and c.b == 3
    assert hasattr(c, "d") and c.d == 35


def test_chain_loading():

    file1 = os.path.join(path, "basic_config.py")
    file2 = os.path.join(path, "load_config.py")
    c = load([file1, file2])
    assert hasattr(c, "a") and c.a == 1
    assert hasattr(c, "b") and c.b == 6


def test_config_with_module():

    c = load([os.path.join(path, "config_with_module.py")])
    assert hasattr(c, "return_zeros") and numpy.allclose(
        c.return_zeros(), numpy.zeros(shape=(2,))
    )


def test_entry_point_configs():

    # test when all kinds of paths
    c = load(
        [
            os.path.join(path, "basic_config.py"),
            "resource_config",
            "bob.extension.data.resource_config",
            "bob.extension.data.basic_config",
            "subpackage_config",
        ],
        entry_point_group="bob.extension.test_config_load",
    )
    assert hasattr(c, "a") and c.a == 1
    assert hasattr(c, "b") and c.b == 3
    assert hasattr(c, "rc")


def test_load_resource():
    for p, ref in [
        (os.path.join(path, "resource_config2.py"), 1),
        (os.path.join(path, "resource_config2.py:a"), 1),
        (os.path.join(path, "resource_config2.py:b"), 2),
        ("resource1", 1),
        ("resource2", 2),
        ("bob.extension.data.resource_config2", 1),
        ("bob.extension.data.resource_config2:a", 1),
        ("bob.extension.data.resource_config2:b", 2),
    ]:
        c = load(
            [p],
            entry_point_group="bob.extension.test_config_load",
            attribute_name="a",
        )
        assert c == ref, c

    try:
        load(
            ["bob.extension.data.resource_config2:c"],
            entry_point_group="bob.extension.test_config_load",
            attribute_name="a",
        )
        assert False, "The code above should have raised an ImportError"
    except ImportError:
        pass
