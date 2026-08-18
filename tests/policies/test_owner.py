# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the built-in Owner policy."""

import pytest
from sqlalchemy import select

from mora import db
from tests.policies.helpers import assert_bootstrapped


@pytest.mark.integration_test
async def test_owner_policy_bootstrapped(empty_db: db.AsyncSession) -> None:
    """The Owner policy is seeded active, bound to the "owner" role."""
    policy_id = await assert_bootstrapped(empty_db, "Owner", ("role", "owner"))
    rules = (
        await empty_db.execute(
            select(
                db.PolicyRule.type,
                db.PolicyRule.field,
                db.PolicyRule.condition,
                db.PolicyRule.filter,
            ).where(db.PolicyRule.policy_fk == policy_id)
        )
    ).all()

    # One rule per way of owning what a mutator touches, so a mutator may have
    # several: `org_unit_update` has one for a rename and two for a move
    assert len(rules) == 70
    assert sum(rule.field == "org_unit_update" for rule in rules) == 3
    # Every rule gates a mutator on ownership, so all carry a filter, and those
    # applying only to some inputs carry a condition saying which
    assert all(rule.type == "Mutation" and rule.filter for rule in rules)
    assert sum(bool(rule.condition) for rule in rules) == 13
