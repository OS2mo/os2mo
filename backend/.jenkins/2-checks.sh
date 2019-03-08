#!/bin/bash
# Used by Jenkins

. $(dirname $0)/common.sh

#
# we could type check with mypy, but we won't, for now, as it causes too many
# false errors
#
#mypy --no-incremental mora

#
# check the source code with flake8, but suppress any errors
#
exec flake8 --exit-zero --config "$TOPDIR/backend/setup.cfg" mora tests
