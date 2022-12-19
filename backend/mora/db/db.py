# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Starlette plugins to create our database connection."""
from contextvars import ContextVar
from typing import Any

import psycopg2
from starlette.requests import HTTPConnection
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message
from starlette_context import context
from starlette_context.plugins import Plugin

from oio_rest.config import get_settings

dbname_context = ContextVar("dbname")


def _get_dbname():
    settings = get_settings()
    dbname = settings.db_name
    dbname = dbname_context.get(dbname)
    return dbname


def get_new_connection(dbname: str | None = None, autocommit: bool = True):
    settings = get_settings()

    connection = psycopg2.connect(
        dbname=dbname or _get_dbname(),
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        application_name="mox init connection",
        sslmode=settings.db_sslmode,
    )
    connection.autocommit = autocommit
    return connection


class DBConnectionPlugin(Plugin):
    """Starlette Plugin to create the `db_connection` context variable."""

    key = "db_connection"

    async def process_request(self, request: Request | HTTPConnection) -> Any | None:
        return get_new_connection()

    async def enrich_response(self, response: Response | Message) -> None:
        connection = context.get("db_connection")
        connection.close()


def get_database_connection() -> Any | None:
    """Get the database connection."""
    connection = context.get("db_connection", None)
    if connection:
        return connection

    return get_new_connection()
