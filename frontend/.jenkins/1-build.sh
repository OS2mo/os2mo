#!/bin/bash
# Used by Jenkins

. $(dirname $0)/common.sh

yarn
yarn build
