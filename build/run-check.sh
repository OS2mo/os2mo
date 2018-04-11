#!/bin/sh

exec ./flask.sh python -- -m flake8 --exit-zero
