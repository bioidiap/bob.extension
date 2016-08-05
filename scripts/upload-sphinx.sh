#!/usr/bin/env bash

if [ -z "${DOCUSER}" ] || [ -z "${DOCPASS}" ]; then
  echo "Server username and/or password undefined - not uploading documentation";
  exit 0
fi

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
