#!/bin/bash
# Used by Jenkins

. $(dirname $0)/common.sh

#
# check the source code with flake8, but suppress any errors
#
exec flake8 --exit-zero --config "$TOPDIR/backend/setup.cfg" mora tests
