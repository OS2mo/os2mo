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

if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running MO in development mode (live reload)"
    exec uvicorn --reload --reload-dir=backend/mora/ --reload-dir=backend/oio_rest/ --reload-dir=backend/ramodels/ --host 0.0.0.0 --port 5000 --factory mora.app:create_app --timeout-keep-alive 100 --workers 1
else
    echo "Running MO in production mode"
    # If you change this, beware that metrics are currently counted per worker
    # so we would not scrape them correctly.
    exec uvicorn --host 0.0.0.0 --port 5000 --factory mora.app:create_app --timeout-keep-alive 100 --workers 1
fi
