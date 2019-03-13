#!/bin/sh -e

CURDIR=$(cd $(dirname $0); pwd)
TOPDIR="$CURDIR/../.."

for fixture in minimal simple normal
do
    echo
    echo $fixture
    echo

    "$TOPDIR"/flask.sh full-run \
             --fixture $fixture --dump-to "$CURDIR/$fixture.sql"
done

mv "$CURDIR/normal.sql" "$CURDIR/dummy.sql"
