#!/bin/sh
set -e

python3 -m mora.cli initdb --wait 30
python3 -m mora.cli check-configuration-db-status
python3 -m mora.cli wait-for-rabbitmq --seconds 30

exec "$@"
