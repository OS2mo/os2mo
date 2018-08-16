#!/bin/sh

set -e

BASEDIR="$(cd $(dirname $0)/..; pwd)"

. "$VENV"/bin/activate

mkdir -p build/coverage build/reports

exec py.test \
    --verbose \
    --cov=mora \
    --cov-report=xml:build/coverage/python.xml \
    --cov-config=.coveragerc \
    --junitxml=build/reports/python.xml \
    "$@"
