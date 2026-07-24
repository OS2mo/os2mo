# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the built-in Introspection policy."""

import pytest
from sqlalchemy import select

from mora import db
from tests.policies.helpers import assert_bootstrapped

# The rules the migration seeds, spelled out rather than imported: the list is
# short, static, and the reason to pin it is that a change to it must be
# deliberate. `__typename` is a meta-field that can appear under any type; the
# __-prefixed introspection types carry the remaining introspection fields
INTROSPECTION_RULES = {
    ("*", "__typename"),
    ("Query", "__schema"),
    ("Query", "__type"),
    ("__Type", "*"),
    ("__Schema", "*"),
    ("__Field", "*"),
    ("__Directive", "*"),
    ("__EnumValue", "*"),
    ("__InputValue", "*"),
    ("__DirectiveLocation", "*"),
    ("__TypeKind", "*"),
}


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
