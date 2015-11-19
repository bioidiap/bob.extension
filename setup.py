#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Sep 2012 14:43:19 CEST

"""A package that contains a helper for Bob/Python C++ extension development
"""

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

requiries = ['setuptools']
import sys
if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
  requiries.append('importlib')

setup(

    name="bob.extension",
    version=version,
    description="Building of Python/C++ extensions for Bob",
    url='http://github.com/bioidiap/bob.extension',
    license="BSD",
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,



    install_requires=requiries,

    entry_points = {
      'console_scripts': [
        'bob_new_version.py = bob.extension.scripts:new_version',
        'bob_dependecy_graph.py = bob.extension.scripts:dependency_graph',
      ],
    },

    classifiers = [
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
