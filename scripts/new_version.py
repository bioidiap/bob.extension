#!/usr/bin/env python

from __future__ import print_function
import sys, os
import subprocess

import argparse
from distutils.version import StrictVersion as Version

doc = """
This script will push a new version of the given package on GitHub and PyPI.
It assumes that you are in the main directory of the package and have successfully ran buildout, and that you have submitted all changes that should go into the new version.

By default, four steps are executed, in this order:

- tag: The --stable-version will be set, added to GitHub, tagged in GitHub and pushed.
- pypi: The --stable-version will be registered and uploaded to PyPI
- docs: The documentation will be generated and uploaded to PythonHosted
- latest: The --latest-version will be set and committed to GitHub

If any of these commands fail, the remaining steps will be skipped, unless you specify the --keep-going option
"""

parser = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("--stable-version", '-s', required = True, help = "The stable version for the package")
parser.add_argument("--latest-version", '-l', required = True, help = "The latest version for the package")
parser.add_argument("--steps", nargs = "+", choices = ['tag', 'pypi', 'docs', 'latest'], default = ['tag', 'pypi', 'docs', 'latest'], help = "Select the steps that you want to execute")
parser.add_argument("--dry-run", '-q', action = 'store_true', help = "Only print the actions, but do not execute them")
parser.add_argument("--keep-going", '-f', action = 'store_true', help = "Run all steps, even if some of them fail. HANDLE THIS FLAG WITH CARE!")
parser.add_argument("--verbose", '-v', action = 'store_true', help = "Print more information")

args = parser.parse_args()


# assert the the version file is there
version_file = 'version.txt'
assert os.path.exists(version_file)

def run_commands(version, *calls):
  """Updates the version.txt to the given version and runs the given commands."""
  if args.verbose or args.dry_run:
    print (" - cat '%s' > %s" % (version, version_file))
  if not args.dry_run:
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
          exit(-1)

# get current version
current_version = open(version_file).read().rstrip()

# check the versions
if Version(args.latest_version) <= Version(args.stable_version):
  print ("The latest version '%s' must be greater than the stable version '%s'" % (args.latest_version, args.stable_version))
  sys.exit(-1)
if Version(current_version) >= Version(args.latest_version):
  print ("The latest version '%s' must be greater than the current version '%s'" % (args.latest_version, current_version))
  sys.exit(-1)

if 'tag' in args.steps:
  if Version(current_version) != Version(args.stable_version):
    print ("\nTagging version '%s'" % args.stable_version)
    # update stable version on github and add a tag
    run_commands(args.stable_version, ['git', 'add', 'version.txt'], ['git', 'commit', '-m', '"Increased version to %s [skip ci]"' % args.stable_version], ['git', 'tag', 'v%s' % args.stable_version], ['git', 'push', '--tags'])
  else:
    print ("\nSkipping the 'tag' step since the the current version '%s' is already the stable version '%s'" % (current_version, args.stable_version))


if 'pypi' in args.steps:
  if Version(current_version) != Version(args.stable_version):
    print ("\nUploading version '%s' to PyPI" % args.stable_version)
    # update version on github and add a tag
    run_commands(args.stable_version, ['./bin/python', 'setup.py', 'register'], ['./bin/python', 'setup.py', 'sdist', '--formats', 'zip', 'upload'])
  else:
    print ("\nSkipping the 'pypi' step since the the current version '%s' is already the stable version '%s'" % (current_version, args.stable_version))


if 'docs' in args.steps:
  # Documentation can be uploaded, independent of the versions
  print ("\nUploading documentation to PythonHosted.org")
  run_commands(args.stable_version, ["./bin/python", "setup.py", "build_sphinx", "--source-dir", "doc", "--build-dir", "build/doc", "--all-files"], ["./bin/python", "setup.py", "upload_docs", "--upload-dir", "build/doc/html"])

if 'latest' in args.steps:
  # update GitHub version to latest version
  print ("\nSetting latest version '%s'" % args.latest_version)
  run_commands(args.latest_version, ['git', 'add', 'version.txt'], ['git', 'commit', '-m', '"Increased version to %s"' % args.latest_version], ['git', 'push'])


