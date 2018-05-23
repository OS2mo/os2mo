#!/bin/sh

set -e

yarn
./manage.py python -- -m pip install -r requirements-test.txt
./manage.py python -- -m pip install -e ../mox/oio_rest
