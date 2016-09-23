#!/usr/bin/env python

"""
This script will push a new 'stable' version of the current package on
GitHub and PyPI, and update the new version of the package to the given
'latest' version on GitHub.

It assumes that you are in the main directory of the package and have
successfully ran bootstrap, and that you have submitted all changes that should
go into the new version. Preferably, the build on Travis passed. For database
packages, it also assumes that the '.sql3' file has been generated (if any).
Further, it assumes that the 'stable' version has not yet been uploaded to
PyPI, and that no GitHub tag with this version exists.

The 'stable' version (i.e., what will be downloadable from PyPI) can be
current version of the package, but not lower than that.

The 'latest' version (i.e., what will be the new master branch on GitHub)
must be higher than the current and than the stable version.

By default, both versions can be automatically computed from the 'current'
version, which is read from the 'version.txt' file. In this case, the
'stable' version will be the 'current' version without the trailing beta
indicator, and the 'latest' version will be 1 patch level above the 'current'
version, with the beta indicator 0, for example:

* current version (in version.txt): 2.1.6b3
-> automatic stable version: 2.1.6
-> automatic latest version: 2.1.7b0


By default, this script executes two steps, in this order:

  * tag: If given, the 'stable' version will be set and added to GitHub;
    and the version is tagged in GitHub and pushed.

  * latest: The 'latest' version will be set and committed to GitHub

If any of these commands fail, the remaining steps will be skipped, unless you
specify the '--keep-going' option.

If you only want a subset of the steps to be executed, you can limit them using
the '--steps' option. A valid use case, e.g., is only to re-upload the
documentation.

Examples:

  Tags my package with the stable version '2.0.0'. Update my next package
  version to '2.0.1a0'. Do it verbosely ('-vv'):

    %(prog)s --latest-version=2.0.1a0 --stable-version=2.0.0 -vv


  Print out, what would be done using the '--dry-run' option:

    %(prog)s -q


  Do everything automatically (assumes a proper version.txt file):

    %(prog)s -vv
"""

from __future__ import print_function
import sys, os
import subprocess
import shutil
import tempfile
import logging
import re

import argparse
from distutils.version import StrictVersion as Version

logger = logging.getLogger("bob.extension")

def _update_readme(version = None):
  # replace the travis badge in the README.rst with the given version
  BRANCH_RE = re.compile(r'/(master|(v\d+\.\d+\.\d+([abc]\d+)?))')
  with open("README.rst") as read:
    with open(".README.rst", 'w') as write:
      for line in read:
        if BRANCH_RE.search(line) is not None and "gitlab" in line:
          replacement = "/v%s" % version if version is not None else "/master"
          line = BRANCH_RE.sub(replacement, line)
        write.write(line)
  os.rename(".README.rst", "README.rst")


def get_remote_md5_sum(url, max_file_size=100 * 1024 * 1024):
    try:
      from urllib.request import urlopen
    except ImportError:
      from urllib2 import urlopen
    import hashlib
    remote = urlopen(url)
    hash = hashlib.md5()

    total_read = 0
    while True:
        data = remote.read(4096)
        total_read += 4096

        if not data or total_read > max_file_size:
            break

        hash.update(data)

    return hash.hexdigest()


def main(command_line_options = None):
  doc = __doc__ % dict(prog=os.path.basename(sys.argv[0]))
  parser = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument("--latest-version", '-l', help = "The latest version for the package; if not specified, it is guessed from the current version")
  parser.add_argument("--stable-version", '-s', help = "The stable version for the package; if not specified, it is guessed from the current version")
  parser.add_argument("--build-options", '-b', nargs='+', default = [], help = "Add options to build your package")
  parser.add_argument("--steps", nargs = "+", choices = ['tag', 'build', 'pypi', 'docs', 'latest', 'conda-forge'], default = ['tag', 'latest'], help = "Select the steps that you want to execute")
  parser.add_argument("--dry-run", '-q', action = 'store_true', help = "Only print the actions, but do not execute them")
  parser.add_argument("--keep-going", '-f', action = 'store_true', help = "Run all steps, even if some of them fail. HANDLE THIS FLAG WITH CARE!")
  parser.add_argument("--verbose", '-v', action = 'store_true', help = "Print more information")
  parser.add_argument("--force", action='store_true', help="Ignore some checks. Use this with caution.")
  parser.add_argument("--no-buildout", action='store_true', help="Do not use the binaries in the ./bin folder")

  args = parser.parse_args(command_line_options)


  # assert the the version file is there
  version_file = 'version.txt'
  if not os.path.exists(version_file):
    if args.force:
      logger.warn("Could not find the file '%s' containing the version number. Are you inside the root directory of your package?" % version_file)
    else:
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
      args.latest_version += "".join(str(p) for p in version.prerelease[:-1]) + '0'
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
          if not args.keep_going:
            raise ValueError("Command '%s' failed; stopping" % ' '.join(call))


  # check the versions
  if args.stable_version is not None and Version(args.latest_version) <= Version(args.stable_version):
    if args.force:
      logger.warn("The latest version '%s' must be greater than the stable version '%s'" % (args.latest_version, args.stable_version))
    else:
      raise ValueError("The latest version '%s' must be greater than the stable version '%s'" % (args.latest_version, args.stable_version))
  if Version(current_version) >= Version(args.latest_version):
    if args.force:
      logger.warn("The latest version '%s' must be greater than the current version '%s'" % (args.latest_version, current_version))
    else:
      raise ValueError("The latest version '%s' must be greater than the current version '%s'" % (args.latest_version, current_version))
  if args.stable_version is not None and Version(current_version) > Version(args.stable_version):
    if args.force:
      logger.warn("The stable version '%s' cannot be smaller than the current version '%s'" % (args.stable_version, current_version))
    else:
      raise ValueError("The stable version '%s' cannot be smaller than the current version '%s'" % (args.stable_version, current_version))

  if not os.path.exists('./bin/buildout'):
    if args.force or args.no_buildout:
      logger.warn("The bin/buildout script does not exist. Have you bootstrapped your system?")
    else:
      raise IOError("The bin/buildout script does not exist. Have you bootstrapped your system?")


  if 'tag' in args.steps:
    if args.stable_version is not None and Version(args.stable_version) > Version(current_version):
      print ("\nReplacing branch tag in README.rst to '%s'"%('v'+args.stable_version))
      _update_readme(args.stable_version)
      # update stable version on git
      run_commands(args.stable_version, ['git', 'add', 'version.txt', 'README.rst'], ['git', 'commit', '-m', 'Increased stable version to %s' % args.stable_version])
    else:
      # assure that we have the current version
      args.stable_version = current_version
    # add a git tag
    print ("\nTagging version '%s'" % args.stable_version)
    run_commands(None, ['git', 'tag', 'v%s' % args.stable_version], ['git', 'push', '--tags'])


  if 'build' in args.steps:
    if not args.no_buildout:
      print ("\nBuilding the package")
      run_commands(None, ['./bin/buildout'] + args.build_options)

  if args.no_buildout:
    if sys.executable:
      python_cmd = sys.executable
    else:
      python_cmd = 'python'
  else:
    python_cmd = './bin/python'

  if 'pypi' in args.steps:
    print ("\nUploading version '%s' to PyPI" % args.stable_version)
    # update version on git and add a tag
    run_commands(None, [python_cmd, 'setup.py', 'sdist', '--formats', 'zip', 'upload'])


  if 'docs' in args.steps:
    # Documentation can be uploaded, independent of the versions
    print ("\nUploading documentation to PythonHosted.org")
    run_commands(None, [python_cmd, "setup.py", "build_sphinx", "--source-dir", "doc", "--build-dir", "build/doc", "--all-files"], [python_cmd, "setup.py", "upload_docs", "--upload-dir", "build/doc/html"])


  if 'latest' in args.steps:
    # update GitHub version to latest version
    print ("\nReplacing branch tag in README.rst to 'master'")
    _update_readme()
    print ("\nSetting latest version '%s'" % args.latest_version)
    run_commands(args.latest_version, ['git', 'add', 'version.txt', 'README.rst'], ['git', 'commit', '-m', 'Increased latest version to %s  [skip ci]' % args.latest_version], ['git', 'push'])

  if 'conda-forge' in args.steps:
    # open a pull request on conda-forge
    package = os.path.basename(os.getcwd())
    url = 'https://pypi.io/packages/source/{0}/{1}/{1}-{2}.zip'.format(package[0], package, args.stable_version)
    try:
      md5 = get_remote_md5_sum(url)
    except Exception:
      if not args.dry_run:
        raise
      else:
        md5 = 'dryrunmd5'
    temp_dir = tempfile.mkdtemp()
    try:
      print("\nClonning the feedstock")
      feedstock = os.path.join(temp_dir, 'feedstock')
      try:
        run_commands(None,
                     ['git', 'clone', 'git@github.com:conda-forge/{}-feedstock.git'.format(package), feedstock])
      except ValueError:
        print("\nThe feedstock does not exist on conda-forge. Exiting ...")
        raise
      if not args.dry_run:
        os.chdir(feedstock)
      run_commands(None, ['git', 'remote', 'add', 'bioidiap', 'git@github.com:bioidiap/{}-feedstock.git'.format(package)],
                   ['git', 'fetch', '--all'],
                   ['git', 'checkout', '-b', args.stable_version])
      # update meta.yaml
      if not args.dry_run:
        with open('recipe/meta.yaml') as f:
          doc = f.read()
        doc = re.sub(r'\{\s?%\s?set\s?version\s?=\s?".*"\s?%\s?\}', '{% set version = "' + str(args.stable_version) + '" %}', doc, count=1)
        doc = re.sub(r'\s+number\:\s?[0-9]+', '\n  number: 0', doc, count=1)
        doc = re.sub(r'\{\s?%\s?set\s?build_number\s?=\s?"[0-9]+"\s?%\s?\}', '{% set build_number = "0" %}', doc, count=1)
        doc = re.sub(r'\s+md5\:.*', '\n  md5: {}'.format(md5), doc, count=1)
        doc = re.sub(r'\s+url\:.*', '\n  url: {}'.format(url.replace(args.stable_version, '{{ version }}')), doc, count=1)
        doc = re.sub(r'\s+home\:.*', '\n  home: https://www.idiap.ch/software/bob/', doc, count=1)
        with open('recipe/meta.yaml', 'w') as f:
          f.write(doc)
      run_commands(None,
                   ['git', '--no-pager', 'diff'],
                   ['git', 'commit', '-am', 'Updating to version {}'.format(args.stable_version)],
                   ['git', 'push', '--set-upstream', 'bioidiap', args.stable_version],
                   ['firefox', 'https://github.com/conda-forge/{}-feedstock/compare/master...bioidiap:{}?expand=1'.format(package, args.stable_version)])
      print('\nPlease create the pull request in the webpage that was openned.')
    finally:
      shutil.rmtree(temp_dir)

if __name__ == '__main__':
  main()
