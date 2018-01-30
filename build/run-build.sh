#!/bin/sh

set -e

./manage.py build
./manage.py sphinx
./manage.py python -- -m pip install -r requirements-test.txt
