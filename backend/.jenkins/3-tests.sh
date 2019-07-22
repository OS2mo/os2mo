#!/bin/bash
# Used by Jenkins

. $(dirname $0)/common.sh

BUILD_DIR="$TOPDIR"/backend/build

# We'll want warnings during our test run!
export PYTHONWARNINGS=default
export FLASK_ENV=testing
export FLASK_APP="mora.app:create_app()"

#
# create the output directories
#
mkdir -p "$BUILD_DIR"/coverage "$BUILD_DIR"/reports

#
# we use pytest, kinda sorta, for its nice and integrated support for
# junit & coverage xml. unfortunately, however, it doesn't work all
# the well with the actual unittest suite, ignoring expected failures
# and subtests :(
#
# in reality, the entire point of pytest is that it's a replacement
# for unittest, so we should probably move to another testrunner,
# eventually
#
coverage run \
         --rcfile="$TOPDIR"/backend/setup.cfg \
         -m mora.cli -- \
         test --verbose --buffer \
         --xml-report "$BUILD_DIR"/reports \
         "$@"

coverage report \
         --rcfile="$TOPDIR"/backend/setup.cfg

coverage xml \
         --rcfile="$TOPDIR"/backend/setup.cfg \
         -o "$BUILD_DIR"/coverage/python.xml
