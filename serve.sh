#!/bin/sh

set -e

export $(cat $(dirname $0)/.env)

pipenv sync -d --bare

exec pipenv run serve "$@"
