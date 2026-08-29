# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The seeded policies match the hardcoded built-in policies."""

from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mora.db import Policy as PolicyRow
from mora.graphapi import policy_eval
from mora.graphapi.policies_builtin import POLICIES


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_seeded_policies_match_builtin(empty_db: AsyncSession) -> None:
    rows = (
        (
            await empty_db.scalars(
                select(PolicyRow)
                .options(
                    selectinload(PolicyRow.selectors),
                    selectinload(PolicyRow.readers),
                    selectinload(PolicyRow.mutators),
                    selectinload(PolicyRow.type_grants),
                )
                .order_by(PolicyRow.name)
            )
        )
        .unique()
        .all()
    )
    loaded = [policy_eval._to_policy(r) for r in rows]
    # Compare order-insensitively on name; the hardcoded order differs
    builtin = sorted(POLICIES, key=lambda p: p.name)
    assert {p.name for p in loaded} == {p.name for p in builtin}
    for got, want in zip(loaded, builtin):
        assert got.name == want.name
        assert got.selector == want.selector
        assert got.active == want.active
        assert set(got.readers) == set(want.readers)
        assert set(got.mutators) == set(want.mutators)
        assert got.types == want.types


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_load_policies_reads_the_database(empty_db: AsyncSession) -> None:
    await policy_eval.load_policies(empty_db)
    assert {p.name for p in policy_eval._policies} == {p.name for p in POLICIES}


async def test_load_policies_falls_back_on_database_failure() -> None:
    before = policy_eval._policies
    session = AsyncMock()
    session.scalars.side_effect = ConnectionError("no database")
    await policy_eval.load_policies(session)
    assert policy_eval._policies is before
