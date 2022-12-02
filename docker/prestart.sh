#!/bin/sh

# SPDX-FileCopyrightText: 2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

set -e

# If DISABLE_ALEMBIC is unset or false, run alembic
if [ -z "$DISABLE_ALEMBIC" ] || [ "$DISABLE_ALEMBIC" = "false" ]; then
    python3 -m oio_rest initdb --wait 30
elif [ "$DISABLE_ALEMBIC" = "true" ]; then
    echo "Alembic disabled by switch"
else
    echo "UNKNOWN DISABLE_ALEMBIC value: $DISABLE_ALEMBIC"
    exit 1
fi
