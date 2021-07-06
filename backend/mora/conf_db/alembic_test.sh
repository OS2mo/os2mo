#!/bin/bash
# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
set -e

GENERATE_OUTPUT=$(alembic revision --autogenerate 2>&1)
echo "${GENERATE_OUTPUT}"

echo "# Check that database is up-to-date"
echo "${GENERATE_OUTPUT}" | grep -v "Target database is not up to date."

echo "# Check that we did not generate anything"
echo "${GENERATE_OUTPUT}" | grep -v "Generating"
