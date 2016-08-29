#!/usr/bin/env bash
# Wed 17 Aug 2016 13:50:09 CEST
set -ex

if [ "${#}" != 2 ]; then
  echo "usage: `basename $0` <prefix> <python-version>"
  echo "example: `basename $0` /opt/conda 2.7"
  exit 1
fi

BASEDIR=$1
PYTHON_VERSION=$2
CONDA=${BASEDIR}/bin/conda
MINICONDA=miniconda.sh

if [ "$(uname)" == "Darwin" ]; then
  ARCH="MacOSX-x86_64"
else
  ARCH="Linux-x86_64"
fi

if [[ "$PYTHON_VERSION" == "2.7" ]]; then
  PYK="2"
else
  PYK="3"
fi

# Create root environment and add basic channels for conda
if [ ! -x ${CONDA} ]; then
  if [ ! -x ${MINICONDA} ]; then
    mkdir -pv `dirname ${MINICONDA}`
    echo "[>>] Downloading `basename ${MINICONDA}` -> ${MINICONDA}..."
    curl --progress-bar https://repo.continuum.io/miniconda/Miniconda${PYK}-latest-${ARCH}.sh --output ${MINICONDA}
    chmod 755 ${MINICONDA}
  fi

  echo "[>>] Creating root environment and setting basic options..."
  bash ${MINICONDA} -b -p ${BASEDIR}
fi

echo "[>>] Updating conda in the root environment..."
touch ${BASEDIR}/.condarc
${CONDA} config --set show_channel_urls True
${CONDA} install --override-channels -c defaults --yes -n root conda-build sphinx sphinx_rtd_theme
${CONDA} update --override-channels -c defaults --yes -n root conda
${CONDA} config --add channels conda-forge
${CONDA} config --add channels ${TEST_CHANNEL}
${CONDA} info

# Function for running command and echoing results
run_cmd() {
  echo "[(`date +%c`)>>] Running \"${@}\"..."
  ${@}
  if [ "$?" != "0" ]; then
    echo "[(`date +%c`)!!] Command Failed \"${@}\""
    exit 1
  else
    echo "[(`date +%c`)<<] Finished comand \"${@}\""
  fi
}
