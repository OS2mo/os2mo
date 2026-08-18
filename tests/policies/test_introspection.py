# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the built-in Introspection policy."""

from collections.abc import Awaitable
from collections.abc import Callable
from uuid import UUID

import pytest
from sqlalchemy import select

from alembic_helpers.introspection import INTROSPECTION_RULES
from mora import db
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied
from tests.policies.conftest import CreatePolicy
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


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "query",
    ["query { __typename }", "query { __schema { queryType { name } } }"],
)
async def test_filtered_rule_cannot_grant_an_introspection_field(
    empty_db: db.AsyncSession,
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    deactivate_policy: Callable[[str], Awaitable[None]],
    alice: UUID,
    query: str,
) -> None:
    """A filter selects entities, and an introspection field touches none."""
    # The built-in Introspection policy would otherwise grant, unfiltered,
    # before any filter was reached
    await deactivate_policy("Introspection")
    await create_policy(
        "filtered-wildcard",
        actors=[("all", "")],
        rules=[
            (
                "*",
                "*",
                "",
                # The filter matches, and still grants no introspection
                '[{"collection": "employee", "filter": {"uuids": [token.uuid]}}]',
            )
        ],
    )
    set_auth(user_uuid=alice)

    assert_denied(graphapi_post(query))


@pytest.mark.integration_test
async def test_filtered_rule_cannot_grant_an_introspection_type_field(
    empty_db: db.AsyncSession,
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    create_policy: CreatePolicy,
    deactivate_policy: Callable[[str], Awaitable[None]],
    alice: UUID,
) -> None:
    """The fields of `__Schema` are graphql-core's own, so a filter cannot grant them."""
    # The built-in Introspection policy would otherwise grant, unfiltered,
    # before any filter was reached
    await deactivate_policy("Introspection")
    await create_policy(
        "schema-then-filtered-wildcard",
        actors=[("all", "")],
        rules=[
            # Unfiltered, so `__schema` itself is granted and its fields reached
            ("Query", "__schema"),
            (
                "*",
                "*",
                "",
                '[{"collection": "employee", "filter": {"uuids": [token.uuid]}}]',
            ),
        ],
    )
    set_auth(user_uuid=alice)

    assert_denied(graphapi_post("query { __schema { queryType { name } } }"))
