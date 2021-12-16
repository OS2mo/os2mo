#!/bin/sh
# SPDX-FileCopyrightText: 2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

hypercorn \
  --bind 0.0.0.0:5000 \
  --worker-class uvloop \
  --access-logfile - \
  --error-logfile - \
  --workers 1 \
  "$@" \
  'mora.app:create_app()'
