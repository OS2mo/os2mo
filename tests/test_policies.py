# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the policy-based access control (PBAC) engine.

The policies are database-managed; until the policy CRUD API is introduced,
the tests declare them directly through the ORM.
"""

from uuid import UUID

import pytest
from more_itertools import one
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
    rules: list[tuple],
    activated: bool = True,
) -> UUID:
    """Insert a policy directly in the database.

    Rules are (type, field) or (type, field, condition) tuples.
    """
    async with another_transaction() as (_, session):
        policy = db.Policy(name=name, activated=activated)
        policy.actors = [
            db.PolicyActor(kind=kind, value=value) for kind, value in actors
        ]
        policy.rules = [
            db.PolicyRule(type=type, field=field, condition=one(rest) if rest else None)
            for type, field, *rest in rules
        ]
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


# Rule conditions (CEL)
# ---------------------


@pytest.mark.integration_test
async def test_condition_grants_when_true(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
) -> None:
    # The policy applies to the "conditional-role" role but only grants
    # employees when the condition holds.
    await make_policy(
        another_transaction,
        "conditional",
        actors=[("role", "conditional-role")],
        rules=[("Query", "employees", 'token.preferred_username == "bruce"')],
    )
    set_auth(role="conditional-role", preferred_username="bruce")
    assert graphapi_post(READ_EMPLOYEES).errors is None


@pytest.mark.integration_test
async def test_condition_denies_when_false(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
) -> None:
    # The actor matches the policy (by role), but the condition does not hold.
    await make_policy(
        another_transaction,
        "conditional",
        actors=[("role", "conditional-role")],
        rules=[("Query", "employees", 'token.preferred_username == "alice"')],
    )
    set_auth(role="conditional-role", preferred_username="bruce")
    assert denied(graphapi_post(READ_EMPLOYEES))


@pytest.mark.integration_test
async def test_unconditional_rule_grants_despite_false_condition(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
) -> None:
    # Two rules for the same field: one with a false condition, one
    # unconditional. The unconditional one grants access regardless.
    await make_policy(
        another_transaction,
        "conditional",
        actors=[("role", "conditional-role")],
        rules=[("Query", "employees", "false"), ("Query", "employees")],
    )
    set_auth(role="conditional-role")
    assert graphapi_post(READ_EMPLOYEES).errors is None


# Legacy policy (RBAC-via-PBAC)
# -----------------------------


@pytest.mark.integration_test
async def test_legacy_policy_bootstrapped(
    another_transaction: AnotherTransaction, empty_db
) -> None:
    async with another_transaction() as (_, session):
        policy = (
            await session.scalars(select(db.Policy).where(db.Policy.name == "Legacy"))
        ).one()
        assert policy.activated is True

        # Applies to everyone via an "all" actor.
        actors = (
            await session.scalars(
                select(db.PolicyActor).where(db.PolicyActor.policy_fk == policy.id)
            )
        ).all()
        assert [(actor.kind, actor.value) for actor in actors] == [("all", "")]

        # One explicit rule per permission-gated (type, field), each gated on
        # the field's required RBAC role. No wildcards; covers top-level
        # queries and mutators as well as nested relation fields.
        rules = set(
            (
                await session.execute(
                    select(
                        db.PolicyRule.type,
                        db.PolicyRule.field,
                        db.PolicyRule.condition,
                    ).where(db.PolicyRule.policy_fk == policy.id)
                )
            ).all()
        )
    assert not any(rule[0] == "*" or rule[1] == "*" for rule in rules)
    assert ("Query", "employees", '"read_employee" in token.roles') in rules
    assert ("Mutation", "address_create", '"create_address" in token.roles') in rules
    assert ("Mutation", "ituser_update", '"update_ituser" in token.roles') in rules
    assert ("Employee", "addresses", '"read_address" in token.roles') in rules


@pytest.mark.integration_test
async def test_legacy_grants_when_role_matches_permission(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    # Reading employees requires the "read_employee" role under legacy RBAC.
    # The Legacy policy grants it to anyone carrying that role.
    set_auth(role="read_employee")
    assert graphapi_post(READ_EMPLOYEES).errors is None


@pytest.mark.integration_test
async def test_legacy_denies_when_role_missing(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    # A token without the field's required role gets nothing from Legacy.
    set_auth(role="some_unrelated_role")
    assert denied(graphapi_post(READ_EMPLOYEES))


@pytest.mark.integration_test
async def test_legacy_permission_is_field_specific(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    # The Legacy rule conditions are gated on the *accessed field's* required
    # role: "read_employee" grants the employees query but not the org_units
    # query (which requires "read_org_unit").
    set_auth(role="read_employee")
    assert graphapi_post(READ_EMPLOYEES).errors is None
    assert denied(graphapi_post(READ_ORG_UNITS))


# Administrator/Reader convenience policies
# -----------------------------------------


@pytest.mark.integration_test
async def test_administrator_and_reader_bootstrapped(
    another_transaction: AnotherTransaction, empty_db
) -> None:
    async with another_transaction() as (_, session):
        rules = set(
            (
                await session.execute(
                    select(
                        db.Policy.name,
                        db.PolicyActor.kind,
                        db.PolicyActor.value,
                        db.PolicyRule.type,
                        db.PolicyRule.field,
                    )
                    .where(db.PolicyActor.policy_fk == db.Policy.id)
                    .where(db.PolicyRule.policy_fk == db.Policy.id)
                    .where(db.Policy.name.in_(["Administrator", "Reader"]))
                )
            ).all()
        )
    assert rules == {
        ("Administrator", "role", "admin", "Query", "*"),
        ("Administrator", "role", "admin", "Mutation", "*"),
        ("Reader", "role", "reader", "Query", "*"),
    }


@pytest.mark.integration_test
async def test_reader_role_reads_all_queries(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    set_auth(role="reader")
    assert graphapi_post(READ_EMPLOYEES).errors is None
    assert graphapi_post(READ_ORG_UNITS).errors is None
    # Reader grants queries only, not mutations.
    delete = """
    mutation {
      facet_delete(uuid: "00000000-0000-0000-0000-000000000000") { uuid }
    }
    """
    assert denied(graphapi_post(delete))
