#!/bin/bash
# Used by Jenkins

. $(dirname $0)/common.sh

GIT_COMMIT=$(GIT_DIR="$TOPDIR/.git" git rev-parse --short HEAD)

#
# this script exists to deploy a successful build on our two servers,
# eventually, we'll do something much better using a proper
# provisioning tool
#
if [[ "$BRANCH_NAME" = development ]]
then
    ssh -l mora 192.168.122.116 /srv/update-mora.py "$GIT_COMMIT"
elif [[ "$BRANCH_NAME" = master ]]
then
    ssh -l mora 192.168.122.113 /srv/update-mora.py "$GIT_COMMIT"
elif [[ "$BRANCH_NAME" = release/* ]]
then
    echo "TODO: Cannot handle release branches, yet!"
else
    echo "Nothing to deploy for $BRANCH_NAME!"
fi
