#!/bin/sh

set -e

./manage.py build
./manage.py sphinx
