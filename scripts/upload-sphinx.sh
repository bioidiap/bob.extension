#!/usr/bin/env bash

if [ -z "${DOCUSER}" ] || [ -z "${DOCPASS}" ] || [ -z "${BOB_DOCUMENTATION_SERVER}" ]; then
  echo "Server username and/or password undefined - not uploading documentation";
  exit 0
fi

# check branch (see: http://stackoverflow.com/a/229606)
branch=$(git branch)
if [[ "$branch" != *"master"* ]]; then
  echo "Not on master branch, but on branch '$branch' -- not uploading documentation";
  exit 0;
fi

echo "Detected branch '$branch' to be master branch -- uploading wheel to Idiap servers"

info=sphinx/.gitlab-ci.info
codename=$(basename ${CI_PROJECT_NAME})-${CI_BUILD_REF}
server=https://${DOCUSER}:${DOCPASS}@www.idiap.ch/software/bob/docs-upload/

# annotate
echo "repo=${CI_PROJECT_PATH}" >> ${info}
echo "branch=${CI_BUILD_REF_NAME}" >> ${info}
echo "tag=${CI_BUILD_TAG}" >> ${info}
echo "build=${CI_BUILD_ID}" >> ${info}
echo "commit=${CI_BUILD_REF}" >> ${info}
echo "runner=${CI_RUNNER_DESCRIPTION}" >> ${info}

# compress
tar cfj ${codename}.tar.bz2 sphinx

# send
curl --silent --insecure --upload-file ${codename}.tar.bz2 ${server}
