#!/bin/bash
# Used by Jenkins

. $(dirname $0)/common.sh

#
# first, upgrade setuptools & pip - pysaml2 depends on it
#
pip install -U packaging pip setuptools wheel

#
# then install our requirements and then additionally, install the
# sources themselves so that we can invoke the command easily
#
# (unfortunately, we use a few dependencies from git, and that doesn't
# work well with setuptools, hence the two steps)
#
pip install \
    -r "$TOPDIR"/backend/requirements-test.txt \
    -e "$TOPDIR"/backend

#
# build the frontend
#
"$TOPDIR"/backend/flask.sh build

#
# build the documentation
#
"$TOPDIR"/backend/flask.sh docs
