#!/bin/bash
# Used by Jenkins

. $(dirname $0)/common.sh

BUILD_DIR="$TOPDIR"/backend/build

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
exec py.test \
    --verbose \
    --cov=mora \
    --cov-report=xml:"$BUILD_DIR"/coverage/python.xml \
    --cov-config=.coveragerc \
    --junitxml="$BUILD_DIR"/reports/python.xml \
    "$@"
