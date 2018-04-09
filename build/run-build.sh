#!/bin/sh

set -e

./flask.sh build
./flask.sh sphinx
