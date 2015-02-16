#!/usr/bin/env python

"""
This script will push a new ``'stable'`` version of the current package on GitHub and PyPI, and update the new version of the package to the given ``'latest'`` version on GitHub.
It assumes that you are in the main directory of the package and have successfully ran bootstrap, and that you have submitted all changes that should go into the new version.
Preferably, the build on Travis passed.
For database packages, it also assumes that the ``.sql3`` files have been generated.
Also, it assumes that the ``'stable'`` version has not yet been uploaded to PyPI, and that no GitHub tag with this version exists.

The ``'stable'`` version (i.e., what will be downloadable from PyPI) can be current version of the package, but not lower than that.
The ``'latest'`` version (i.e., what will be the new master branch on GitHub) must be higher than the current and than the stable version.
Both versions can be automatically computed from the current version, which is stored in the 'version.txt' file.
By default, five steps are executed, in this order:

- ``tag``: If given, the --stable-version will be set and added to GitHub; and the version is tagged in GitHub and pushed.
- ``build``: The package will be (re-)built with bin/buildout using the provided build options.
- ``pypi``: The --stable-version (or the current version) will be registered and uploaded to PyPI
- ``docs``: The documentation will be generated and uploaded to PythonHosted
- ``latest``: The --latest-version will be set and committed to GitHub

If any of these commands fail, the remaining steps will be skipped, unless you specify the ``--keep-going`` option.

If you only want a subset of the steps to be executed, you can limit them using the ``--steps`` option.
A valid use case, e.g., is only to re-upload the documentation.
"""

from __future__ import print_function
import sys, os
import subprocess

import argparse
from distutils.version import StrictVersion as Version



def _update_readme(version = None):
  # replace the travis badge in the README.rst with the given version
  with open("README.rst") as read:
    with open(".README.rst", 'w') as write:
      for line in read:
        if "?branch=" in line:
          pos = line.find("?branch=")
          line = line[:pos] + "?branch=%s\n" % ("v%s"%version if version is not None else "master")
        write.write(line)
  os.rename(".README.rst", "README.rst")

def main(command_line_options = None):
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument("--latest-version", '-l', help = "The latest version for the package; if not specified, it is guessed from the current version")
  parser.add_argument("--stable-version", '-s', help = "The stable version for the package; if not specified, it is guessed from the current version")
  parser.add_argument("--build-options", '-b', nargs='+', default = [], help = "Add options to build your package")
  parser.add_argument("--steps", nargs = "+", choices = ['tag', 'build', 'pypi', 'docs', 'latest'], default = ['tag', 'build', 'pypi', 'docs', 'latest'], help = "Select the steps that you want to execute")
  parser.add_argument("--dry-run", '-q', action = 'store_true', help = "Only print the actions, but do not execute them")
  parser.add_argument("--keep-going", '-f', action = 'store_true', help = "Run all steps, even if some of them fail. HANDLE THIS FLAG WITH CARE!")
  parser.add_argument("--verbose", '-v', action = 'store_true', help = "Print more information")

  args = parser.parse_args(command_line_options)


  # assert the the version file is there
  version_file = 'version.txt'
  if not os.path.exists(version_file):
    raise ValueError("Could not find the file '%s' containing the version number. Are you inside the root directory of your package?" % version_file)

  # get current version
  current_version = open(version_file).read().rstrip()

  if args.stable_version is None:
    args.stable_version = ".".join("%s"%v for v in Version(current_version).version)
    print ("Assuming stable version to be %s (since current version %s)" % (args.stable_version, current_version))

  if args.latest_version is None:
    # increase current patch version once
    version = Version(current_version)
    ver = list(version.version)
    ver[-1] += 1
    args.latest_version = ".".join([str(v) for v in ver])
    if version.prerelease is not None:
      args.latest_version += "".join(str(p) for p in version.prerelease)
    print ("Assuming latest version to be %s (since current version %s)" % (args.latest_version, current_version))


  def run_commands(version, *calls):
    """Updates the version.txt to the given version and runs the given commands."""
    if version is not None and (args.verbose or args.dry_run):
      print (" - cat '%s' > %s" % (version, version_file))
    if not args.dry_run and version is not None:
      # update version to stable version, if not done yet
      with open(version_file, 'w') as f:
        f.write(version)

    # get all calls
    for call in calls:
      if args.verbose or args.dry_run:
        print (' - ' + ' '.join(call))
      if not args.dry_run:
        # execute call
        if subprocess.call(call):
          # call failed (has non-zero exit status)
          print ("Command '%s' failed; stopping" % ' '.join(call))
          if not args.keep_going:
            raise ValueError("Command '%s' failed; stopping" % ' '.join(call))


  # check the versions
  if args.stable_version is not None and Version(args.latest_version) <= Version(args.stable_version):
    raise ValueError("The latest version '%s' must be greater than the stable version '%s'" % (args.latest_version, args.stable_version))
  if Version(current_version) >= Version(args.latest_version):
    raise ValueError("The latest version '%s' must be greater than the current version '%s'" % (args.latest_version, current_version))
  if args.stable_version is not None and Version(current_version) > Version(args.stable_version):
    raise ValueError("The stable version '%s' cannot be smaller than the current version '%s'" % (args.stable_version, current_version))

  if not os.path.exists('./bin/buildout'):
    raise IOError("The bin/buildout script does not exist. Have you bootstrapped your system?")


  if 'tag' in args.steps:
    if args.stable_version is not None and Version(args.stable_version) > Version(current_version):
      print ("\nReplacing branch tag in README.rst to '%s'"%('v'+args.stable_version))
      _update_readme(args.stable_version)
      # update stable version on github
      run_commands(args.stable_version, ['git', 'add', 'version.txt', 'README.rst'], ['git', 'commit', '-m', 'Increased stable version to %s' % args.stable_version])
    else:
      # assure that we have the current version
      args.stable_version = current_version
    # add a github tag
    print ("\nTagging version '%s'" % args.stable_version)
    run_commands(None, ['git', 'tag', 'v%s' % args.stable_version], ['git', 'push', '--tags'])


  if 'build' in args.steps:
    print ("\nBuilding the package")
    run_commands(None, ['./bin/buildout'] + args.build_options)


  if 'pypi' in args.steps:
    print ("\nUploading version '%s' to PyPI" % args.stable_version)
    # update version on github and add a tag
    run_commands(None, ['./bin/python', 'setup.py', 'register'], ['./bin/python', 'setup.py', 'sdist', '--formats', 'zip', 'upload'])


  if 'docs' in args.steps:
    # Documentation can be uploaded, independent of the versions
    print ("\nUploading documentation to PythonHosted.org")
    run_commands(None, ["./bin/python", "setup.py", "build_sphinx", "--source-dir", "doc", "--build-dir", "build/doc", "--all-files"], ["./bin/python", "setup.py", "upload_docs", "--upload-dir", "build/doc/html"])


  if 'latest' in args.steps:
    # update GitHub version to latest version
    print ("\nReplacing branch tag in README.rst to 'master'")
    _update_readme()
    print ("\nSetting latest version '%s'" % args.latest_version)
    run_commands(args.latest_version, ['git', 'add', 'version.txt', 'README.rst'], ['git', 'commit', '-m', 'Increased latest version to %s  [skip ci]' % args.latest_version], ['git', 'push'])


if __name__ == '__main__':
  main()
