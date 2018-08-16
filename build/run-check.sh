#!/bin/sh

set -e

. "$VENV"/bin/activate

flake8 --exit-zero
