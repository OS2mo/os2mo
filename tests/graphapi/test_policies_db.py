# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The seeded policies match the hardcoded built-in policies."""

import pytest
from more_itertools import one
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mora.db import Policy as PolicyRow
from mora.graphapi.policies_builtin import POLICIES
from mora.graphapi.policy import Mutator
from mora.graphapi.policy import Policy
from mora.graphapi.policy import ReadRule
from mora.graphapi.policy import Selector
from mora.graphapi.policy import SelectorKind
from mora.graphapi.policy import TypeRule


def _to_policy(row: PolicyRow) -> Policy:
    s = one(row.selectors)
    return Policy(
        name=row.name,
        selector=Selector(kind=SelectorKind(s.kind.value), value=s.value),
        readers=tuple(
            ReadRule(
                collection=r.collection,
                fields=frozenset(r.fields),
                k=r.k,
                condition=r.condition,
            )
            for r in row.readers
        ),
        mutators=tuple(Mutator(name=m.name, mk=m.mk, k=m.k) for m in row.mutators),
        types=TypeRule(grants=frozenset((g.type, g.field) for g in row.type_grants)),
        active=row.active,
    )


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
    loaded = [_to_policy(r) for r in rows]
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
