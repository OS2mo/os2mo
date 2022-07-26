# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from sqlalchemy.engine import create_engine

from oio_rest.db import get_connection


def get_engine():
    """Return SQLAlchemy `Engine` instance bound to the LoRa database"""
    # We use the `creator` option to tell SQLAlchemy to use our custom
    # `get_connection` function to create database connections. This requires
    # us to pass a *valid* (but unused) database URL to `create_engine`.
    # Doing this means we only consume one database connection per LoRa worker,
    # as the `get_connection` function reuses a global database connection for
    # each worker process.
    return create_engine("postgresql://unused-database-url", creator=get_connection)
