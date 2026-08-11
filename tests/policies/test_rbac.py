# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the built-in RBAC policy."""

import pytest
from sqlalchemy import select

from alembic_helpers.rbac_map import RBAC_MAP
from mora import db
from tests.policies.helpers import assert_bootstrapped


@pytest.mark.integration_test
async def test_rbac_policy_bootstrapped(empty_db: db.AsyncSession) -> None:
    """The RBAC policy is seeded active, bound to every actor."""
    policy_id = await assert_bootstrapped(empty_db, "RBAC", ("all", ""))

    # One explicit rule per permission-gated (type, field), gated on the
    # field's required RBAC role
    rules = set(
        (
            await empty_db.execute(
                select(
                    db.PolicyRule.type,
                    db.PolicyRule.field,
                    db.PolicyRule.condition,
                ).where(db.PolicyRule.policy_fk == policy_id)
            )
        ).all()
    )
    assert rules == {
        (type, field, f'"{role}" in token.roles')
        for (type, field), (role, _, _) in RBAC_MAP.items()
    }
