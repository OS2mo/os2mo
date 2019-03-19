#!/bin/sh -e

CURDIR=$(cd $(dirname $0); pwd)
TOPDIR="$CURDIR/../.."

for fixture in minimal simple small normal large
do
    echo
    echo $fixture
    echo

    "$TOPDIR"/flask.sh update-fixture $fixture
done
