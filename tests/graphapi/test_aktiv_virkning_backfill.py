# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The background job backfills aktiv_virkning on pre-existing rows.

See ``mora.db.backfill``: migration ``e2a9c47f1b6d`` adds the column NULLable
without a backfill, and this job touches each NULL row with a no-op ``UPDATE`` so
the trigger fills it, in batches, claiming rows with ``FOR UPDATE SKIP LOCKED``
so many MO containers can run it concurrently.
"""

from collections.abc import Callable
from collections.abc import Sequence
from uuid import UUID

import pytest
from sqlalchemy import Row
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mora.db import BrugerAttrEgenskaber
from mora.db import BrugerRegistrering
from mora.db.backfill import backfill_aktiv_virkning

from ..conftest import AnotherTransaction
from ..conftest import SessionmakerMaker


async def _status(db: AsyncSession, person: UUID) -> Sequence[Row]:
    """Per egenskaber row: (is_null, equals_own_virkning)."""
    result = await db.execute(
        select(
            BrugerAttrEgenskaber.aktiv_virkning.is_(None),
            BrugerAttrEgenskaber.aktiv_virkning
            == func.tstzmultirange(BrugerAttrEgenskaber.virkning_period),
        )
        .join(
            BrugerRegistrering,
            BrugerRegistrering.id == BrugerAttrEgenskaber.bruger_registrering_id,
        )
        .where(BrugerRegistrering.bruger_id == str(person))
    )
    return result.all()


async def _null_out_egenskaber(
    another_transaction: AnotherTransaction, person: UUID
) -> None:
    """Set the person's egenskaber active_tils to NULL, simulating rows that
    predate the column being backfilled. On this isolated copy we drop the
    NOT NULL constraint (the pre-backfill state the job is meant to run in) and
    disable the trigger around the UPDATE so it does not immediately recompute
    the value back."""
    async with another_transaction() as (_sessionmaker, session):
        await session.execute(
            text(
                "ALTER TABLE bruger_attr_egenskaber "
                "ALTER COLUMN active_tils DROP NOT NULL"
            )
        )
        await session.execute(
            text("ALTER TABLE bruger_attr_egenskaber DISABLE TRIGGER set_active_tils")
        )
        await session.execute(
            text(
                "UPDATE bruger_attr_egenskaber ae SET active_tils = NULL "
                "FROM bruger_registrering r "
                "WHERE r.id = ae.bruger_registrering_id AND r.bruger_id = :uuid"
            ),
            {"uuid": str(person)},
        )
        await session.execute(
            text("ALTER TABLE bruger_attr_egenskaber ENABLE TRIGGER set_active_tils")
        )


@pytest.mark.integration_test
async def test_backfill_fills_null_rows(
    empty_db: AsyncSession,
    sessionmakermaker: SessionmakerMaker,
    another_transaction: AnotherTransaction,
    create_person: Callable[[], UUID],
) -> None:
    person = create_person()
    await _null_out_egenskaber(another_transaction, person)

    before = await _status(empty_db, person)
    assert before  # sanity
    assert all(is_null for is_null, _ in before)

    await backfill_aktiv_virkning(sessionmakermaker.sessionmaker)

    after = await _status(empty_db, person)
    for is_null, equals_own_virkning in after:
        assert not is_null
        assert equals_own_virkning  # active person -> own virkning


@pytest.mark.integration_test
async def test_backfill_skips_locked_rows(
    empty_db: AsyncSession,
    sessionmakermaker: SessionmakerMaker,
    another_transaction: AnotherTransaction,
    create_person: Callable[[], UUID],
) -> None:
    """Rows locked by another transaction are skipped, not blocked on.

    This is what lets multiple MO containers back-fill concurrently: whichever
    container holds a row, the others move on. The skipped rows are filled on a
    later pass once the lock is released."""
    person = create_person()
    await _null_out_egenskaber(another_transaction, person)

    # Hold a lock on the person's (only) NULL rows, then run the backfill: with
    # nothing else to do it must finish without touching the locked rows.
    async with another_transaction() as (_sessionmaker, session):
        await session.execute(
            text(
                "SELECT ae.id FROM bruger_attr_egenskaber ae "
                "JOIN bruger_registrering r ON r.id = ae.bruger_registrering_id "
                "WHERE r.bruger_id = :uuid FOR UPDATE"
            ),
            {"uuid": str(person)},
        )
        await backfill_aktiv_virkning(sessionmakermaker.sessionmaker)
        assert all(is_null for is_null, _ in await _status(empty_db, person))

    # Lock released -> a subsequent pass fills them.
    await backfill_aktiv_virkning(sessionmakermaker.sessionmaker)
    assert all(not is_null for is_null, _ in await _status(empty_db, person))
