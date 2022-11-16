#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""A package that contains a helper for Bob Python/C++ extension development
"""

from setuptools import find_packages, setup

# Define package version
version = open("version.txt").read().rstrip()

setup(
    name="bob.extension",
    version=version,
    description="Building of Python/C++ extensions for Bob",
    url="http://gitlab.idiap.ch/bob/bob.extension",
    license="BSD",
    author="Andre Anjos",
    author_email="andre.anjos@idiap.ch",
    long_description=open("README.rst").read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools", "click >= 8", "click-plugins"],
    project_urls={
        "Documentation": "https://www.idiap.ch/software/bob/docs/bob/bob.extension/master/",
    },
    entry_points={
        "console_scripts": [
            "bob = bob.extension.scripts:main_cli",
        ],
        "bob.cli": [
            "config = bob.extension.scripts.config:config",
        ],
        # some test entry_points
        "bob.extension.test_config_load": [
            "basic_config = bob.extension.data.basic_config",
            "verbose_config = bob.extension.data.verbose_config",
            "resource_config = bob.extension.data.resource_config",
            "subpackage_config = bob.extension.data.subpackage.config",
            "resource1 = bob.extension.data.resource_config2",
            "resource2 = bob.extension.data.resource_config2:b",
        ],
        "bob.extension.test_dump_config": [
            "basic_config = bob.extension.data.basic_config",
            "resource_config = bob.extension.data.resource_config",
            "subpackage_config = bob.extension.data.subpackage.config",
        ],
    },
    classifiers=[
        "Framework :: Bob",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
