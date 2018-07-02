#!/bin/sh

BASEDIR="$(cd $(dirname $0)/..; pwd)"

mkdir -p build/coverage build/reports

./manage.py python -- -m pytest \
    --verbose \
    --cov=mora \
    --cov-report=xml:build/coverage/python.xml \
    --cov-config=.coveragerc \
    --junitxml=build/reports/python.xml \
    "$@"
