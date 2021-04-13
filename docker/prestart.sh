#!/bin/sh

# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

################################################################################
# Changes to this file requires approval from Labs. Please add a person from   #
# Labs as required approval to your MR if you have any changes.                #
################################################################################

set -e

# Ensure db is up
echo "Waiting for db to be ready"
python3 -m mora.cli checkdb --wait 30 || exit
echo "OK"
echo ""

# Migrate sessiondb
echo "Migrating sessiondb"
python3 -m mora.cli initdb --wait 30 || exit
echo "OK"
echo ""

# Migrate conf_db
echo "Migrating conf_db"
cd backend/mora/conf_db
alembic upgrade head || exit
cd ../../..
echo "OK"
echo ""

# Check that DBs are up and ready
echo "Checking db-status"
python3 -m mora.cli check-configuration-db-status || exit
echo "OK"
echo ""

# Wait for rabbitmq to start
echo "Waiting for rabbitmq"
python3 -m mora.cli wait-for-rabbitmq --seconds 30 || exit
echo "OK"
echo ""
