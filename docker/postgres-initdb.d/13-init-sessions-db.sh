#!/bin/bash
set -e

true "${SESSIONS_DB_USER:?SESSIONS_DB_USER is unset. Error!}"
true "${SESSIONS_DB_PASSWORD:?SESSIONS_DB_PASSWORD is unset. Error!}"
true "${SESSIONS_DB_NAME:?SESSIONS_DB_NAME is unset. Error!}"

psql -v ON_ERROR_STOP=1 <<-EOSQL
    create user $SESSIONS_DB_USER with encrypted password '$SESSIONS_DB_PASSWORD';
    create database $SESSIONS_DB_NAME owner $SESSIONS_DB_USER;
    grant all privileges on database $SESSIONS_DB_NAME to $SESSIONS_DB_USER;
EOSQL

# we can connect without password because ``trust`` authentication for Unix
# sockets is enabled inside the container.

# Do not replace this script with a raw .sql script. If an .sql script fails
# (entrypoint script will exit) and the container is restarted with an already
# initialized data directory, the rest of the scripts will not be run.
