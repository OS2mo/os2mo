# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Background backfill of aktiv_virkning on pre-existing rows."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog import get_logger

logger = get_logger()

TABLES = (
    "bruger_attr_egenskaber",
    "bruger_attr_udvidelser",
    "bruger_relation",
    "facet_attr_egenskaber",
    "facet_relation",
    "itsystem_attr_egenskaber",
    "itsystem_relation",
    "klasse_attr_egenskaber",
    "klasse_relation",
    "organisationenhed_attr_egenskaber",
    "organisationenhed_relation",
    "organisationfunktion_attr_egenskaber",
    "organisationfunktion_attr_udvidelser",
    "organisationfunktion_relation",
)


async def _backfill_table(
    sessionmaker: async_sessionmaker, table: str
) -> None:  # pragma: no cover
    # No-op UPDATE, so the BEFORE trigger fills active_tils rather than this
    # duplicating its logic.
    statement = text(
        f"UPDATE {table} SET id = id WHERE id IN ("
        f"SELECT id FROM {table} WHERE active_tils IS NULL "
        f"LIMIT 1000 FOR UPDATE SKIP LOCKED)"
    )
    while True:
        async with sessionmaker() as session, session.begin():
            result = await session.execute(statement)
        if not result.rowcount:
            break
        logger.info(
            "aktiv_virkning backfill: batch done", table=table, rows=result.rowcount
        )
        await asyncio.sleep(0.1)
    logger.info("aktiv_virkning backfill: table done", table=table)


async def backfill_aktiv_virkning(
    sessionmaker: async_sessionmaker,
) -> None:  # pragma: no cover
    for table in TABLES:
        await _backfill_table(sessionmaker, table)
    logger.info("aktiv_virkning backfill: done")
