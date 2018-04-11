#!/bin/sh

set -e

if test -z $PIPENV
then
    PIPENV=pipenv
fi

if ! which $PIPENV > /dev/null 2>&1
then
    echo 'Please install pipenv!' >&2
    exit 1
fi

if ! $PIPENV --venv > /dev/null 2>&1
then
    $PIPENV --bare sync --dev
fi

exec $PIPENV --bare run flask "$@"
