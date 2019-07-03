#!/bin/sh
set -e

export FLASK_APP=mora.app:create_app
python3 -m mora.cli initdb --wait 30

exec "$@"
