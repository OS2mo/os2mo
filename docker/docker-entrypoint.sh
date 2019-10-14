#!/bin/sh
set -e

python3 -m mora.cli initdb --wait 30
python3 -m mora.cli check-configuration-db-status

exec "$@"
