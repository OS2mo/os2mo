#!/bin/sh

set -xe

cd $(dirname $0)

if test -z "$PYTHON"
then
    PYTHON=python3.5
fi

rm -rf .coverage htmlcov

if test -z "$NOBUILD"
then
    $PYTHON ./manage.py build
    $PYTHON ./manage.py python -- -m pip install -q -r requirements-test.txt
fi

$PYTHON ./manage.py python -- -m coverage run ./manage.py test "$@"

$PYTHON ./manage.py python -- -m coverage html
$PYTHON ./manage.py python -- -m coverage report

