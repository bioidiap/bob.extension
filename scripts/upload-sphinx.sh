#!/usr/bin/env bash

# some checks
if [ "${TRAVIS_PULL_REQUEST}" != "false" ]; then
  echo "This is a pull request - not updating documentation";
  exit 0
fi

pyver=$(python -c 'import sys; print "%d.%d" % sys.version_info[:2]')
pyver_req="2.7"

if [ "${pyver}" != "${pyver_req}" ]; then
  echo "Not building against Python ${pyver_req} - not uploading documentation";
  exit 0
fi

info=sphinx/.travis.info
codename=$(basename ${TRAVIS_REPO_SLUG})-${TRAVIS_COMMIT}
server=https://${DOCUSER}:${DOCPASS}@www.idiap.ch/software/bob/docs-upload/

# annotate
echo -e "repo=${TRAVIS_REPO_SLUG}\n"   >> ${info}
echo -e "branch=${TRAVIS_BRANCH}\n"    >> ${info}
echo -e "tag=${TRAVIS_TAG}\n"          >> ${info}
echo -e "build=${TRAVIS_JOB_NUMBER}\n" >> ${info}
echo -e "commit=${TRAVIS_COMMIT}\n"    >> ${info}
echo -e "os=${TRAVIS_OS_NAME}\n"       >> ${info}

# compress
tar cfj ${codename}.tar.bz2 sphinx

# send
curl -k -T ${codename}.tar.bz2 ${server}
