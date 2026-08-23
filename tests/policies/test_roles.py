# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the built-in Reader and Admin policies."""

import pytest
from sqlalchemy import select

from alembic_helpers.rbac_map import RBAC_MAP
from mora import db
from tests.policies.helpers import assert_bootstrapped


@pytest.mark.integration_test
@pytest.mark.parametrize("role", ["reader", "admin"])
async def test_role_policy_bootstrapped(empty_db: db.AsyncSession, role: str) -> None:
    """The role's policy is seeded active, bound to every actor."""
    policy_id = await assert_bootstrapped(empty_db, role.capitalize(), ("all", ""))

    # One explicit rule per (type, field) the role governs, gated on the role
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
        for (type, field), required in RBAC_MAP.items()
        if required == role
    }
