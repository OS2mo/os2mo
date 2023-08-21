# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import APIRouter
from ramqp import AMQPSystem
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT
from structlog import get_logger

from mora import amqp
from mora import config
from oio_rest.db import get_connection

logger = get_logger()


router = APIRouter()


@router.post("/amqp/flush", status_code=HTTP_204_NO_CONTENT)
async def flush(request: Request) -> None:
    """
    Flush queued AMQP events immediately.

    Note that this is only needed for the "new" AMQP subsystem. Events in the old one
    are always sent immediately.
    """
    logger.warning("Flushing AMQP events")

    settings = config.get_settings()
    amqp_system = AMQPSystem(settings.amqp)
    await amqp._emit_events(request.app.state.sessionmaker, amqp_system)


@router.post("/database/autocommit", status_code=HTTP_204_NO_CONTENT)
async def autocommit(enable: bool) -> None:
    """
    Toggle database autocommit.
    """
    logger.warning("Database autocommit", enabled=enable)
    connection = get_connection()
    connection.autocommit = enable


@router.post("/database/commit", status_code=HTTP_204_NO_CONTENT)
async def commit() -> None:
    """
    Commit pending changes to the database.
    """
    logger.warning("Database commit")
    connection = get_connection()
    connection.commit()


@router.post("/database/rollback", status_code=HTTP_204_NO_CONTENT)
async def rollback() -> None:
    """
    Roll back pending changes to the database.
    """
    logger.warning("Database rollback")
    connection = get_connection()
    connection.rollback()
