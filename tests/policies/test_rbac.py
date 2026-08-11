# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the built-in RBAC policy."""

import pytest
from sqlalchemy import select

from alembic_helpers.rbac_map import RBAC_MAP
from mora import db
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.policies.helpers import assert_access
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role,query,granted",
    [
        # Reading employees requires "read_employee" and reading org-units
        # "read_org_unit". The rule conditions are gated on the role the
        # *accessed field* requires, so neither role carries to the other field
        ("read_employee", "query { employees { objects { uuid } } }", True),
        ("read_employee", "query { org_units { objects { uuid } } }", False),
        ("read_org_unit", "query { org_units { objects { uuid } } }", True),
        ("read_org_unit", "query { employees { objects { uuid } } }", False),
        # A role no field requires gets nothing from RBAC at all
        ("some_unrelated_role", "query { employees { objects { uuid } } }", False),
    ],
)
async def test_rbac_gates_each_field_on_its_own_role(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    role: str,
    query: str,
    granted: bool,
) -> None:
    set_auth(role=role)
    assert_access(graphapi_post(query), granted)
