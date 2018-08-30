#!/bin/bash

set -e

. "$VENV"/bin/activate

FLASK_APP=mora/app.py flask build
FLASK_APP=mora/app.py flask sphinx
