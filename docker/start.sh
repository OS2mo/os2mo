#!/bin/sh

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

set -ex

# If DISABLE_ALEMBIC is unset or false, run alembic
if [ -z "$DISABLE_ALEMBIC" ] || [ "$DISABLE_ALEMBIC" = "false" ]; then
    echo "Upgrading database schema"
    alembic upgrade head
elif [ "$DISABLE_ALEMBIC" = "true" ]; then
    echo "Alembic disabled by switch"
else
    echo "UNKNOWN DISABLE_ALEMBIC value: $DISABLE_ALEMBIC"
    exit 1
fi

# In production, we use gunicorn with the worker class
# "uvicorn.workers.UvicornWorker", but that does not work with --reload, so we
# use uvicorn in development at the cost of some dev/prod parity. This has one
# issue in dev where the service won't restart (because of the --reload flag)
# when an error occurs. The service restarts as soon as a file is edited
# though.
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running MO in development mode (live reload)"
    exec opentelemetry-instrument uvicorn --host 0.0.0.0 --port 5000 --factory mora.app:create_app --timeout-keep-alive 100
else
    echo "Running MO in production mode"
    exec opentelemetry-instrument gunicorn --config /app/docker/gunicorn-settings.py 'mora.app:create_app()'
fi
