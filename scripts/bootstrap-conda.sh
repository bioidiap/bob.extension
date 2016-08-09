#!/usr/bin/env bash
# Mon  8 Aug 17:40:24 2016 CEST
# Andre Anjos <andre.anjos@idiap.ch>

# Creates a build environment for the current package
# $1 == conda folder (e.g. "/opt/conda")
# $2 == python version (e.g. "2.7")

if [ "${#}" -ne 2 ]; then
  echo "usage: ${0} <conda-root> <python-version>"
  echo "example: ${0} /opt/conda 2.7"
  exit 1
fi

CONDA_FOLDER=${1}
PYTHON_VERSION=${2}
PREFIX=`pwd`/build-env
WHEELS_SERVER="www.idiap.ch"
WHEELS_REPOSITORY="https://${WHEELS_SERVER}/software/bob/wheels/gitlab/"

# Function for running command and echoing results
run_cmd() {
  echo "[(`date +%c`)>>] Running \"${@}\"..."
  ${@}
  echo "[(`date +%c`)<<] Finished comand \"${@}\""
}

# Clones the conda dev environment to use
if [ ! -d ${PREFIX} ]; then
  echo "[++] Bootstrapping (offline) conda installation at ${PREFIX}..."
  run_cmd ${CONDA_FOLDER}/bin/conda create --prefix ${PREFIX} --clone `cat ${CONDA_FOLDER}/envs/latest-devel-${PYTHON_VERSION}.txt` --yes
else
  echo "[!!] Prefix directory ${PREFIX} exists, not re-installing..."
fi

# Source the newly created conda environment
echo "[>>] Running \"source ${CONDA_FOLDER}/bin/activate `pwd`/build-env\"..."
source ${CONDA_FOLDER}/bin/activate `pwd`/build-env
echo "[<<] Environment ${PREFIX} activated"

# Install this package's dependencies
if [ -e requirements.txt ]; then
  use_pip=`which pip`
  echo "[++] Using pip: ${use_pip}"
  run_cmd ${use_pip} install --find-links ${WHEELS_REPOSITORY} --use-wheel --no-index --trusted-host ${WHEELS_SERVER} --pre --requirement requirements.txt
else
  echo "[!!] No requirements.txt file found, skipping 'pip install'..."
fi

# Finally, bootstrap the installation from the new environment
if [ -e bootstrap-buildout.py ]; then
  use_python=`which python`
  echo "[++] Using python: ${use_python}"
  run_cmd ${use_python} bootstrap-buildout.py
else
  echo "[!!] No bootstrap-buildout.py file found, skipping 'buildout bootstrap'..."
fi
