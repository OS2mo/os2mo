# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Background backfill of aktiv_virkning on pre-existing rows.

Migration ``e2a9c47f1b6d`` adds ``aktiv_virkning`` NULLable without a backfill,
because rewriting every relation/attribute row in a single migration takes too
long to run online. Instead, this job touches each not-yet-filled row with a
no-op ``UPDATE`` so the INSERT/UPDATE trigger computes the value, in batches,
until none remain. It deliberately does not duplicate the trigger's logic.

It runs as a lifespan background task on every MO container. Rows are claimed
with ``FOR UPDATE SKIP LOCKED``, so any number of containers can run it
concurrently without contending on or double-processing the same rows: once a
row's trigger has run it is no longer NULL, so every container converges and the
loop terminates. ``NULL`` means only "not yet backfilled" (a never-active row is
the empty multirange, not NULL), which makes it a safe, terminating work
predicate.
"""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog import get_logger

from ._common import Base
from ._common import _AktivVirkningMixin

logger = get_logger()

# Rows per batch. Small enough that each COMMIT (which fires the deferred
# triggers) stays cheap and row locks are released promptly for other containers.
BATCH_SIZE = 1000

# Pause between batches to yield to request handling and avoid saturating the
# database while backfilling in the background.
SLEEP_BETWEEN_BATCHES = 0.1


def _tables() -> list[str]:
    """Every relation/attribute table carrying active_tils, from the ORM."""
    return sorted(
        mapper.local_table.name
        for mapper in Base.registry.mappers
        if issubclass(mapper.class_, _AktivVirkningMixin)
    )


async def _backfill_table(sessionmaker: async_sessionmaker, table: str) -> None:
    # No-op UPDATE that fires the BEFORE INSERT/UPDATE trigger, which fills
    # active_tils. FOR UPDATE SKIP LOCKED lets multiple containers cooperate
    # without contending on, or double-processing, the same rows.
    statement = text(
        f"UPDATE {table} SET id = id WHERE id IN ("
        f"SELECT id FROM {table} WHERE active_tils IS NULL "
        f"LIMIT {BATCH_SIZE} FOR UPDATE SKIP LOCKED)"
    )
    total = 0
    while True:
        async with sessionmaker() as session, session.begin():
            result = await session.execute(statement)
            rowcount = result.rowcount
        if not rowcount:
            break
        total += rowcount
        await asyncio.sleep(SLEEP_BETWEEN_BATCHES)
    logger.info("aktiv_virkning backfill: table done", table=table, rows=total)


async def backfill_aktiv_virkning(sessionmaker: async_sessionmaker) -> None:
    """Fill aktiv_virkning on pre-existing rows, one table at a time.

    Safe to run repeatedly and concurrently; a no-op once every row is filled.
    Never raises on error: it must not take down the application it runs inside.
    """
    try:
        for table in _tables():
            await _backfill_table(sessionmaker, table)
        logger.info("aktiv_virkning backfill: done")
    except asyncio.CancelledError:
        logger.info("aktiv_virkning backfill: cancelled")
        raise
    except Exception:
        logger.exception("aktiv_virkning backfill: failed")
