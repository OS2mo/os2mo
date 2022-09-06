#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

set -e
apt update \
  && apt install -y --no-install-recommends postgresql-11-pgtap \
  && rm -rf /var/lib/apt/lists/*
