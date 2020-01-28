#!/bin/bash

# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

################################################################################
# Changes to this file requires approval from Labs. Please add a person from   #
# Labs as required approval to your MR if you have any changes.                #
################################################################################

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
