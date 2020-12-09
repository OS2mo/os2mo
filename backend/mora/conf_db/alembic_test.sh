#!/bin/bash
# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

if initial=$(alembic heads); then
  if alembic revision --autogenerate; then
    if final=$(alembic heads); then
      if [ "$initial" == "$final" ]; then
        exit 0
      fi
    fi
  fi
fi
exit 1
