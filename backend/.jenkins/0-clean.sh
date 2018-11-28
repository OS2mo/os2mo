#!/bin/bash
# Used by Jenkins

WANT_VENV=0

. $(dirname $0)/common.sh

#
# remove virtual environment, and build products
#
rm -rf \
   "$VENV" \
   "$TOPDIR"/frontend/dist \
   "$TOPDIR"/frontend/node_modules \
   "$TOPDIR"/backend/build \
   "$TOPDIR"/docs/out
