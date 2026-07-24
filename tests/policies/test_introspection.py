# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the built-in Introspection policy."""

import pytest
from sqlalchemy import select

from alembic_helpers.introspection import INTROSPECTION_RULES
from mora import db
from tests.policies.helpers import assert_bootstrapped


@pytest.mark.integration_test
async def test_introspection_policy_bootstrapped(empty_db: db.AsyncSession) -> None:
    """The Introspection policy is seeded active, bound to every actor."""
    policy_id = await assert_bootstrapped(empty_db, "Introspection", ("all", ""))
    rules = (
        await empty_db.execute(
            select(db.PolicyRule.type, db.PolicyRule.field).where(
                db.PolicyRule.policy_fk == policy_id
            )
        )
    ).all()
    assert set(rules) == INTROSPECTION_RULES
