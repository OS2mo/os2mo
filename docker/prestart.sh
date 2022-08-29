#!/bin/sh

# SPDX-FileCopyrightText: 2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

################################################################################
# Changes to this file requires approval from Labs. Please add a person from   #
# Labs as required approval to your MR if you have any changes.                #
################################################################################

set -e

# If DISABLE_ALEMBIC is unset or false, run alembic
if [ -z "$DISABLE_ALEMBIC" ] || [ "$DISABLE_ALEMBIC" = "false" ]; then
    if [ "$ENABLE_INTERNAL_LORA" = "True" ]; then
        python3 -m oio_rest initdb --wait 30
    else
        echo "ENABLE_INTERNAL_LORA is $ENABLE_INTERNAL_LORA, not running 'initdb'"
    fi
elif [ "$DISABLE_ALEMBIC" = "true" ]; then
    echo "Alembic disabled by switch"
else
    echo "UNKNOWN DISABLE_ALEMBIC value: $DISABLE_ALEMBIC"
    exit 1
fi
