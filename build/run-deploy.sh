#!/bin/sh

set -ex

if test "$BRANCH_NAME" = development
then
    ssh -l mora 192.168.122.116 /srv/update-mora.py "$GIT_COMMIT"
elif test "$BRANCH_NAME" = master
then
    echo 'TODO!'
else
    echo "Nothing to deploy for $BRANCH_NAME!"
fi
