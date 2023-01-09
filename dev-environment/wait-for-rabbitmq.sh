#!/usr/bin/env bash

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

set -e

# Generally, we just want our applications to crash when they can't run and let
# the orchestrator (docker, k8s, ...) be responsible for restarting or
# whatever. This script solves an issue in the dev environment where MO crashes
# when it can't connect to RabbitMQ, but the MO-docker-compose-service never
# shuts down because uvicorn catches the exception to support hot-reloading.
# So yeah, this script just saves developers from having to restart the service
# manually or save a file to trigger uvicorns hot reload.

python -m mora.cli wait-for-rabbitmq --seconds 30 || exit

exec "$@"
