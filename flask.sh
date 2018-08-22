#!/bin/sh

set -e

export $(cat $(dirname $0)/.env)

exec pipenv run flask "$@"
