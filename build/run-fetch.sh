#!/bin/sh

set -e

yarn
pipenv clean
pipenv sync --dev
