# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The aktiv_virkning triggers keep the column correct on writes to either table.

See migration ``e2a9c47f1b6d``: ``aktiv_virkning`` is a period row's own
``virkning`` intersected with the union of its registration's active periods,
which live in the ``tils`` table. A trigger on the period table maintains it when
the row's own ``virkning`` changes; a trigger on the ``tils`` table recomputes
every period row of the registration when its active periods change.

The normal write path (a GraphQL mutation) is driven end-to-end and checked via
SQL. The ``tils`` change is out-of-band -- LoRa is append-only and never updates
a ``tils`` row -- so it is necessarily driven with SQL directly.
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

from ..conftest import AnotherTransaction


async def _status(db: AsyncSession, person: UUID) -> Sequence[Row]:
    """Per egenskaber row: (is_null, is_empty, equals_own_virkning).

    Computed in SQL to avoid depending on how the multirange round-trips into
    Python. "equals_own_virkning" holds when the whole row is active."""
    result = await db.execute(
        select(
            BrugerAttrEgenskaber.aktiv_virkning.is_(None),
            func.isempty(BrugerAttrEgenskaber.aktiv_virkning),
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


@pytest.mark.integration_test
async def test_insert_populates_aktiv_virkning(
    empty_db: AsyncSession,
    create_person: Callable[[], UUID],
) -> None:
    """Creating a person fills aktiv_virkning via the period-table trigger.

    A freshly created person is Aktiv for all of its virkning, so aktiv_virkning
    must be non-NULL and equal to the row's own virkning as a multirange."""
    person = create_person()

    rows = await _status(empty_db, person)
    assert rows  # sanity: the person has egenskaber rows
    for is_null, _is_empty, equals_own_virkning in rows:
        assert not is_null
        assert equals_own_virkning


@pytest.mark.integration_test
async def test_tils_change_recomputes_aktiv_virkning(
    empty_db: AsyncSession,
    another_transaction: AnotherTransaction,
    create_person: Callable[[], UUID],
) -> None:
    """A change to the tils table recomputes the period rows' aktiv_virkning.

    The egenskaber rows are never touched; only the registration's gyldighed is
    flipped to Inaktiv directly in the tils table. The tils-table trigger must
    still recompute the egenskaber rows to the empty multirange (no active
    period), proving the value tracks changes to *either* table."""
    person = create_person()
    active = await _status(empty_db, person)
    assert active
    for is_null, is_empty, equals_own_virkning in active:
        assert not is_null
        assert not is_empty
        assert equals_own_virkning

    async with another_transaction() as (_sessionmaker, session):
        await session.execute(
            text(
                "UPDATE bruger_tils_gyldighed t SET gyldighed = 'Inaktiv' "
                "FROM bruger_registrering r "
                "WHERE r.id = t.bruger_registrering_id AND r.bruger_id = :uuid"
            ),
            {"uuid": str(person)},
        )

    recomputed = await _status(empty_db, person)
    assert recomputed
    for is_null, is_empty, _equals_own_virkning in recomputed:
        assert not is_null  # never-active is {} (empty), not NULL
        assert is_empty
