#!/bin/bash
# Used by Jenkins

. $(dirname $0)/common.sh

rm -rf \
   "$TOPDIR"/frontend/dist \
   "$TOPDIR"/frontend/node_modules
