#!/usr/bin/env bash

BIN=$(dirname $0)
ROOT=${BIN}/..
DOCS=${ROOT}/docs

${BIN}/clean.sh

cd ${ROOT}
tox
make -C ${DOCS} html
python setup.py sdist bdist_wheel
