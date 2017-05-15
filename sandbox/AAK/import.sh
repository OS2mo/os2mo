#!/bin/sh

DIR=$(cd $(dirname $0); pwd)

VENV=$DIR/venv
PYTHON=${PYTHON:-python3.5}

$PYTHON -m venv $VENV

$VENV/bin/pip install grequests openpyxl tzlocal
$VENV/bin/python $DIR/import.py "$@"
