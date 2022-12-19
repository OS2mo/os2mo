# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Starlette plugins to create our database connection."""
import os
from typing import Any

import psycopg2
from starlette.requests import HTTPConnection
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message
from starlette_context import context
from starlette_context.plugins import Plugin

from oio_rest.config import get_settings
from oio_rest.db import _get_dbname


def create_connection():
    dbname = _get_dbname()
    settings = get_settings()

    _connection = psycopg2.connect(
        dbname=dbname,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        application_name="mox init connection",
        sslmode=settings.db_sslmode,
    )
    commit = True
    if os.environ.get("TESTING", "") == "True":
        commit = False
    _connection.autocommit = commit

    return _connection


class DBConnectionPlugin(Plugin):
    """Starlette Plugin to create the `db_connection` context variable."""

    key = "db_connection"

    async def process_request(self, request: Request | HTTPConnection) -> Any | None:
        return create_connection()

    async def enrich_response(self, response: Response | Message) -> None:
        connection = context.get("db_connection")
        connection.close()


def get_database_connection() -> Any | None:
    """Get the database connection."""
    return context.get("db_connection", None)
