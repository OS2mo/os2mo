#!/bin/bash

set -e

. "$VENV"/bin/activate

flake8 --exit-zero
