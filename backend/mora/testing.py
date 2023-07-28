# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import APIRouter
from starlette.status import HTTP_204_NO_CONTENT
from structlog import get_logger

from oio_rest.db import get_connection

logger = get_logger()


router = APIRouter()


@router.post("/autocommit", status_code=HTTP_204_NO_CONTENT)
async def autocommit(enable: bool) -> None:
    """
    Toggle database autocommit.
    """
    logger.warning("Database autocommit", enabled=enable)
    connection = get_connection()
    connection.autocommit = enable


@router.post("/commit", status_code=HTTP_204_NO_CONTENT)
async def commit() -> None:
    """
    Commit pending changes to the database.
    """
    logger.warning("Database commit")
    connection = get_connection()
    connection.commit()


@router.post("/rollback", status_code=HTTP_204_NO_CONTENT)
async def rollback() -> None:
    """
    Roll back pending changes to the database.
    """
    logger.warning("Database rollback")
    connection = get_connection()
    connection.rollback()
