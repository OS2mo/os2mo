#!/bin/sh

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

set -ex

# Run prerequisites that are the same across dev, CI and prod.
# (Currently this means applying Alembic migrations to the `mox` database.)
. ./docker/prestart.sh

# In production, we use gunicorn with the worker class
# "uvicorn.workers.UvicornWorker", but that does not work with --reload, so we
# use uvicorn in development at the cost of some dev/prod parity. This has one
# issue in dev where the service won't restart (because of the --reload flag)
# when an error occurs. The service restarts as soon as a file is edited
# though.
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running MO in development mode (live reload)"
    exec uvicorn --reload --reload-dir=backend/mora/ --reload-dir=backend/oio_rest/ --reload-dir=backend/ramodels/ --host 0.0.0.0 --port 5000 --factory mora.app:create_app --timeout-keep-alive 100
else
    echo "Running MO in production mode"
    exec gunicorn --config /app/docker/gunicorn-settings.py 'mora.app:create_app()'
fi
