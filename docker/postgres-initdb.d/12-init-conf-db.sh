#!/bin/bash
set -e

true "${CONF_DB_USER:?CONF_DB_USER is unset. Error!}"
true "${CONF_DB_PASSWORD:?CONF_DB_PASSWORD is unset. Error!}"
true "${CONF_DB_NAME:?CONF_DB_NAME is unset. Error!}"

psql -v ON_ERROR_STOP=1 <<-EOSQL
    create user $CONF_DB_USER with encrypted password '$CONF_DB_PASSWORD';
    create database $CONF_DB_NAME owner $CONF_DB_USER;
    grant all privileges on database $CONF_DB_NAME to $CONF_DB_USER;
EOSQL

# we can connect without password because ``trust`` authentication for Unix
# sockets is enabled inside the container.
