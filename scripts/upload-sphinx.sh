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
echo "repo=${TRAVIS_REPO_SLUG}"   >> ${info}
echo "branch=${TRAVIS_BRANCH}"    >> ${info}
echo "tag=${TRAVIS_TAG}"          >> ${info}
echo "build=${TRAVIS_JOB_NUMBER}" >> ${info}
echo "commit=${TRAVIS_COMMIT}"    >> ${info}
echo "os=${TRAVIS_OS_NAME}"       >> ${info}

# compress
tar cfj ${codename}.tar.bz2 sphinx

# send
echo "Uploading ${codename} into webdav server..."
curl -k -T ${codename}.tar.bz2 ${server}
