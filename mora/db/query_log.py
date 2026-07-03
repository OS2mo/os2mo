# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Request-scoped postgres query logging.

Enabling logging by sending a header on the GraphQL API is helpful when
debugging a specific query that misbehaves or performs poorly. The flag is
stored in starlette_context, so only queries issued while handling that
request are logged.
"""

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError
from structlog import get_logger

logger = get_logger()

QUERY_LOG_HEADER = "X-Log-Postgres-Queries"
_QUERY_LOG_CONTEXT_KEY = "log_postgres_queries"


def enable_query_logging() -> None:
    """Turn on postgres query logging for the current request cycle."""
    context[_QUERY_LOG_CONTEXT_KEY] = True


def is_query_logging_enabled() -> bool:
    try:
        return bool(context.get(_QUERY_LOG_CONTEXT_KEY, False))
    except ContextDoesNotExistError:
        return False


def _log_query(conn, cursor, statement, parameters, context_, executemany) -> None:
    if is_query_logging_enabled():
        logger.info(
            "postgres_query",
            statement=statement,
            parameters=parameters,
            executemany=executemany,
        )


def register_query_logger(engine: AsyncEngine) -> None:
    """Attach the query-logging listener to the given async engine."""
    # Events fire on the underlying sync engine; async wrappers delegate to it.
    event.listen(engine.sync_engine, "before_cursor_execute", _log_query)
