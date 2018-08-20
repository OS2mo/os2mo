#!/bin/sh

set -e

yarn
python3 -m venv "$VENV"

. "$VENV"/bin/activate

pip install -U packaging pip setuptools wheel
pip install -r requirements-test.txt
pip install -e mox/oio_rest
