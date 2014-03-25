#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 20 Sep 2012 14:43:19 CEST

"""A package that contains a helper for Bob/Python C++ extension development
"""

from setuptools import setup, find_packages

setup(

    name="xbob.extension",
    version="0.3.0a0",
    description="Helps projects building Python/C++ extensions for Bob",
    url='http://github.com/bioidiap/xbob.extension',
    license="BSD",
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    packages=find_packages(),
    zip_safe=True,

    namespace_packages=[
      "xbob",
      ],

    install_requires=[
      'setuptools',
      'numpydoc'
      ],

    classifiers = [
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],

    )
