#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""A package that contains a helper for Bob Python/C++ extension development
"""

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

setup(
    name="bob.extension",
    version=version,
    description="Building of Python/C++ extensions for Bob",
    url='http://gitlab.idiap.ch/bob/bob.extension',
    license="BSD",
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=['setuptools', 'click', 'click-plugins'],

    entry_points={
        'console_scripts': [
            'bob = bob.extension.scripts:main_cli',
            'bob_new_version.py = bob.extension.scripts:new_version',
            'bob_dependecy_graph.py = bob.extension.scripts:dependency_graph',
        ],
        'bob.cli': [
            'config = bob.extension.scripts.config:config',
        ],
        # some test entry_points
        'bob.extension.test_config_load': [
            'basic_config = bob.extension.data.basic_config',
            'resource_config = bob.extension.data.resource_config',
            'subpackage_config = bob.extension.data.subpackage.config',
        ],
    },
    classifiers=[
        'Framework :: Bob',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
