#!/usr/bin/env bash
# Mon  8 Aug 17:40:24 2016 CEST
# Andre Anjos <andre.anjos@idiap.ch>

# Creates a build environment for the current package
# $1 == conda folder (e.g. "/opt/conda")
# $2 == python version (e.g. "2.7")

CONDA_FOLDER=$1
PYTHON_VER=$2
PREFIX=`pwd`/build-env

# Clones the conda dev environment to use
echo ${CONDA_FOLDER}/bin/conda create --prefix ${PREFIX} --clone `cat
${CONDA_FOLDER}/envs/latest-devel-${PYTHON_VER}.txt` --offline --yes --quiet
${CONDA_FOLDER}/bin/conda create --prefix ${PREFIX} --clone `cat
${CONDA_FOLDER}/envs/latest-devel-${PYTHON_VER}.txt` --offline --yes --quiet

# Install this package's dependencies
echo source ${CONDA_FOLDER}/bin/activate `pwd`/build-env
source ${CONDA_FOLDER}/bin/activate `pwd`/build-env

if [ -e requirements.txt ]; then
  echo "Using pip:" `which pip`
  echo pip install --find-links 'https://www.idiap.ch/software/bob/wheels/gitlab/' --use-wheel --no-index --trusted-host 'www.idiap.ch' --pre --requirement requirements.txt
  pip install --find-links 'https://www.idiap.ch/software/bob/wheels/gitlab/' --use-wheel --no-index --trusted-host 'www.idiap.ch' --pre --requirement requirements.txt
fi

if [ -e bootstrap-buildout.py ]; then
  echo "Using python:" `which python`
  echo "python" bootstrap-buildout.py
  python bootstrap-buildout.py
fi
