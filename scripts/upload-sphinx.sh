#!/usr/bin/env bash

# some checks
if [ "${TRAVIS_PULL_REQUEST}" != "false" ]; then
  echo "This is a pull request - not uploading documentation";
  exit 0
fi

if [ -z "${DOCUSER}" ] || [ -z "${DOCPASS}" ] || [ -z "${BOB_DOCUMENTATION_SERVER}" ]; then
  echo "Server username and/or password undefined - not uploading documentation";
  exit 0
fi

# check branch (see: http://stackoverflow.com/a/2111099)
branch=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
if [ "$branch" != "master" ]; then
  echo "Not on master branch -- not uploading documentation";
  exit 0;
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
curl --silent --insecure --upload-file ${codename}.tar.bz2 ${server}
