#!/bin/sh

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

set -ex

# Run prerequisites that are the same across dev, CI and prod.
# (Currently this means applying Alembic migrations to the `mox` database.)
. ./docker/prestart.sh

if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running MO in development mode (live reload)"
    exec uvicorn --reload --host 0.0.0.0 --port 80 main:app
else
    echo "Running MO in production mode"
    exec gunicorn --config /app/docker/gunicorn-settings.py main:app
fi
