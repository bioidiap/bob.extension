#!/usr/bin/env bash

# some checks
if [ "${TRAVIS_PULL_REQUEST}" != "false" ]; then
  echo "This is a pull request - not uploading documentation";
  exit 0
fi

if [ -z "${DOCUSER}" ] || [ -z "${DOCPASS}" ] || [ -z "${BOB_UPLOAD_WHEEL}" ]; then
  echo "Server username and/or password undefined - not uploading wheel";
  exit 0
fi

# create wheel
if [ "${BOB_UPLOAD_WHEEL}" != "1" ]; then
  WHEEL_OPTION=${BOB_UPLOAD_WHEEL}
fi
bin/python setup.py bdist_wheel -d wheel $WHEEL_OPTION

# uplaod wheel
wheel=`find wheel -name "*.whl"`
server=https://${DOCUSER}:${DOCPASS}@www.idiap.ch/software/bob/wheels-upload/travis/

# send
curl --silent --insecure --upload-file $wheel ${server}
