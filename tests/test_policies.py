# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the policy-based access control (PBAC) engine.

The policies are database-managed; until the policy CRUD API is introduced,
the tests declare them directly through the ORM.
"""

from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy import update

from mora import db
from tests.conftest import AnotherTransaction
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

# A public field (in the bootstrapped Public policy) and two role-gated ones.
READ_VERSION = "query { version { mo_version } }"
READ_ORG_UNITS = "query { org_units { objects { uuid } } }"
READ_EMPLOYEES = "query { employees { objects { uuid } } }"

ACCESS_DENIED = "No policy approved the access"


def denied(response) -> bool:
    return response.errors is not None and any(
        error["message"] == ACCESS_DENIED for error in response.errors
    )


async def make_policy(
    another_transaction: AnotherTransaction,
    name: str,
    *,
    actors: list[tuple[str, str]],
    rules: list[tuple[str, str]],
    activated: bool = True,
) -> UUID:
    """Insert a policy directly in the database."""
    async with another_transaction() as (_, session):
        policy = db.Policy(name=name, activated=activated)
        policy.actors = [
            db.PolicyActor(kind=kind, value=value) for kind, value in actors
        ]
        policy.rules = [db.PolicyRule(type=type, field=field) for type, field in rules]
        session.add(policy)
        await session.flush()
        return policy.id


@pytest.mark.integration_test
async def test_public_policy_bootstrapped(
    another_transaction: AnotherTransaction, empty_db
) -> None:
    """The Public policy is seeded active, bound to every actor."""
    async with another_transaction() as (_, session):
        policy = (
            await session.scalars(select(db.Policy).where(db.Policy.name == "Public"))
        ).one()
        assert policy.activated is True
        actors = (
            await session.scalars(
                select(db.PolicyActor).where(db.PolicyActor.policy_fk == policy.id)
            )
        ).all()
        assert [(actor.kind, actor.value) for actor in actors] == [("all", "")]
        rules = (
            await session.execute(
                select(db.PolicyRule.type, db.PolicyRule.field).where(
                    db.PolicyRule.policy_fk == policy.id
                )
            )
        ).all()
        assert ("Query", "version") in set(rules)


@pytest.mark.integration_test
async def test_introspection_policy_bootstrapped(
    another_transaction: AnotherTransaction, empty_db
) -> None:
    """The Introspection policy is seeded active, bound to every actor."""
    async with another_transaction() as (_, session):
        policy = (
            await session.scalars(
                select(db.Policy).where(db.Policy.name == "Introspection")
            )
        ).one()
        assert policy.activated is True
        actors = (
            await session.scalars(
                select(db.PolicyActor).where(db.PolicyActor.policy_fk == policy.id)
            )
        ).all()
        assert [(actor.kind, actor.value) for actor in actors] == [("all", "")]
        rules = set(
            (
                await session.execute(
                    select(db.PolicyRule.type, db.PolicyRule.field).where(
                        db.PolicyRule.policy_fk == policy.id
                    )
                )
            ).all()
        )
        assert ("*", "__typename") in rules
        assert ("__Type", "*") in rules


@pytest.mark.integration_test
async def test_public_field_readable_without_roles(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    """The all-actor Public policy grants public fields to a roleless token."""
    set_auth(role="nobody")
    response = graphapi_post(READ_VERSION)
    assert response.errors is None
    assert response.data is not None


@pytest.mark.integration_test
async def test_pbac_denies_gated_field_without_grant(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    """A field granted by no policy (nor legacy role) is rejected."""
    set_auth(role="nobody")
    response = graphapi_post(READ_ORG_UNITS)
    assert denied(response)


@pytest.mark.integration_test
async def test_public_policy_deactivation_denies(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
) -> None:
    """A deactivated policy does not grant access."""
    async with another_transaction() as (_, session):
        await session.execute(
            update(db.Policy).where(db.Policy.name == "Public").values(activated=False)
        )
    set_auth(role="nobody")
    response = graphapi_post(READ_VERSION)
    assert denied(response)


@pytest.mark.integration_test
async def test_policy_grants_gated_field_by_role(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
) -> None:
    """A policy grants its (type, field) rules to actors matching by role."""
    await make_policy(
        another_transaction,
        "unit-reader",
        actors=[("role", "unit-reader")],
        rules=[("Query", "org_units")],
    )
    set_auth(role="unit-reader")

    granted = graphapi_post(READ_ORG_UNITS)
    assert granted.errors is None

    # The role was not granted the employees collection.
    assert denied(graphapi_post(READ_EMPLOYEES))


@pytest.mark.integration_test
async def test_inactive_policy_grants_nothing(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
) -> None:
    await make_policy(
        another_transaction,
        "inactive",
        actors=[("role", "unit-reader")],
        rules=[("Query", "org_units")],
        activated=False,
    )
    set_auth(role="unit-reader")
    assert denied(graphapi_post(READ_ORG_UNITS))


@pytest.mark.integration_test
async def test_wildcard_field_rule(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
) -> None:
    """A rule may use the wildcard "*" for its field component."""
    await make_policy(
        another_transaction,
        "query-reader",
        actors=[("role", "query-reader")],
        rules=[("Query", "*")],
    )
    set_auth(role="query-reader")
    assert graphapi_post(READ_ORG_UNITS).errors is None
    assert graphapi_post(READ_EMPLOYEES).errors is None


@pytest.mark.integration_test
async def test_all_actor_policy_grants_everyone(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
) -> None:
    """An "all" actor matches every token, whatever its roles."""
    await make_policy(
        another_transaction,
        "everyone-reader",
        actors=[("all", "")],
        rules=[("Query", "employees")],
    )
    set_auth(role="nobody")
    assert graphapi_post(READ_EMPLOYEES).errors is None
