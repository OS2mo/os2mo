#!/bin/bash
# Used by Jenkins

WANT_VENV=0

. $(dirname $0)/common.sh

#
# remove virtual environment, and build products
#
rm -rf \
   "$VENV" \
   "$TOPDIR"/backend/build \
   "$TOPDIR"/docs/out
