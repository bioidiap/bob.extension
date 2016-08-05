#!/usr/bin/env bash

if [ -z "${DOCUSER}" ] || [ -z "${DOCPASS}" ]; then
  echo "Server username and/or password undefined - not uploading wheel";
  exit 0
fi

# create wheel
if [ -n "${BOB_WHEEL_TAG}" ]; then
  WHEEL_OPTION="--python-tag ${BOB_WHEEL_TAG}";
fi
./bin/python setup.py bdist_wheel -d wheel $WHEEL_OPTION

# upload wheel
wheel=`find wheel -name "*.whl"`
server=https://${DOCUSER}:${DOCPASS}@www.idiap.ch/software/bob/wheels-upload/gitlab/

echo -e "\n\nUploading wheel $wheel to server https://www.idiap.ch/software/bob/wheels-upload/gitlab/"

# send
curl --silent --insecure --upload-file $wheel ${server}
