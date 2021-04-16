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
echo ""

# Migrate sessiondb
echo "Migrating sessiondb"
python3 -m mora.cli initdb --wait 30 || exit
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
echo ""

# Wait for rabbitmq to start
echo "Waiting for rabbitmq"
python3 -m mora.cli wait-for-rabbitmq --seconds 30 || exit
echo ""

# Wait for object store to start
echo "Waiting for minio"
python3 -m mora.cli wait-for-minio --seconds 30 || exit
echo ""

# Ensure object store bucket exists
echo "Ensuring minio bucket exists"
python3 -m mora.cli ensure-minio-bucket --seconds 30 || exit
echo ""
