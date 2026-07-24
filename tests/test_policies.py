# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the policy-based access control (PBAC) engine.

The policies are database-managed; until the policy CRUD API is introduced,
the tests declare them directly through the ORM.
"""

import json
from uuid import UUID

import pytest
from more_itertools import first
from sqlalchemy import select
from sqlalchemy import update

from mora import db
from mora.db.policies import POLICYADMIN_UUID
from tests.conftest import AnotherTransaction
from tests.conftest import GQLResponse
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

    Rules are (type, field[, condition[, filter]]) tuples.
    """
    async with another_transaction() as (_, session):
        policy = db.Policy(name=name, activated=activated)
        policy.actors = [
            db.PolicyActor(kind=kind, value=value) for kind, value in actors
        ]
        policy.rules = [
            db.PolicyRule(
                type=type,
                field=field,
                condition=first(rest, None),
                filter=first(rest[1:], None),
            )
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


# Entity rule filters
# -------------------

CREATE_EMPLOYEE = """
  mutation CreateEmployee($input: EmployeeCreateInput!) {
    employee_create(input: $input) {
      uuid
    }
  }
"""

CREATE_ITSYSTEM = """
  mutation CreateITSystem($input: ITSystemCreateInput!) {
    itsystem_create(input: $input) {
      uuid
    }
  }
"""

CREATE_ITUSER = """
  mutation CreateITUser($input: ITUserCreateInput!) {
    ituser_create(input: $input) {
      uuid
    }
  }
"""

UPDATE_ITUSER = """
  mutation UpdateITUser($input: ITUserUpdateInput!) {
    ituser_update(input: $input) {
      uuid
    }
  }
"""

DELETE_ITUSER = """
  mutation DeleteITUser($uuid: UUID!) {
    ituser_delete(uuid: $uuid) {
      uuid
    }
  }
"""


def create_named_person(
    graphapi_post: GraphAPIPost, uuid: str, given_name: str, surname: str
) -> None:
    response = graphapi_post(
        CREATE_EMPLOYEE,
        variables={
            "input": {"uuid": uuid, "given_name": given_name, "surname": surname}
        },
    )
    assert response.errors is None


def create_itsystem(graphapi_post: GraphAPIPost) -> str:
    response = graphapi_post(
        CREATE_ITSYSTEM,
        variables={
            "input": {
                "user_key": "test-itsystem",
                "name": "Test IT system",
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None
    return response.data["itsystem_create"]["uuid"]


def create_ituser_for(
    graphapi_post: GraphAPIPost, person: str, itsystem: str, user_key: str
) -> str:
    response = graphapi_post(
        CREATE_ITUSER,
        variables={
            "input": {
                "user_key": user_key,
                "itsystem": itsystem,
                "person": person,
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None
    return response.data["ituser_create"]["uuid"]


# A check-spec CEL expression pinning the object being mutated (input.uuid) and
# constraining it via the given (inline CEL) sub-filter map on the ituser
# collection.
def ituser_check_spec(inner_filter_cel: str) -> str:
    return (
        '{"collection": "ituser", "check": "IN", "field": input.uuid, '
        f'"filter": {inner_filter_cel}}}'
    )


@pytest.mark.integration_test
async def test_rule_filter_limits_ituser_update_by_person(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
    root_org,
) -> None:
    # Alice may update IT-users, but only those attached to a person named Bob.
    bob = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    carol = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    create_named_person(graphapi_post, bob, "Bob", "Bertelsen")
    create_named_person(graphapi_post, carol, "Carol", "Carlsen")
    itsystem = create_itsystem(graphapi_post)
    bob_ituser = create_ituser_for(graphapi_post, bob, itsystem, "bob-account")
    carol_ituser = create_ituser_for(graphapi_post, carol, itsystem, "carol-account")

    await make_policy(
        another_transaction,
        "alice-updates-bobs-itusers",
        actors=[("role", "editor")],
        rules=[
            (
                "Mutation",
                "ituser_update",
                None,
                ituser_check_spec('{"employee": {"query": "Bob"}}'),
            )
        ],
    )
    set_auth(role="editor")

    def update(ituser: str) -> object:
        return graphapi_post(
            UPDATE_ITUSER,
            variables={
                "input": {
                    "uuid": ituser,
                    "user_key": "changed",
                    "validity": {"from": "2020-01-01"},
                }
            },
        )

    # Bob's IT-user matches the rule filter -> Alice may update it.
    assert update(bob_ituser).errors is None
    # Carol's does not match -> denied.
    assert denied(update(carol_ituser))


@pytest.mark.integration_test
async def test_rule_filter_cel_reads_input(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
    root_org,
) -> None:
    # The check-spec pins the object by `input.uuid` with an empty (match-all)
    # sub-filter, so the object being updated always matches -- proving `input`
    # is in scope.
    bob = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    create_named_person(graphapi_post, bob, "Bob", "Bertelsen")
    itsystem = create_itsystem(graphapi_post)
    bob_ituser = create_ituser_for(graphapi_post, bob, itsystem, "bob-account")

    await make_policy(
        another_transaction,
        "input-scoped",
        actors=[("all", "")],
        rules=[("Mutation", "ituser_update", None, ituser_check_spec("{}"))],
    )
    set_auth(user_uuid=bob)

    response = graphapi_post(
        UPDATE_ITUSER,
        variables={
            "input": {
                "uuid": bob_ituser,
                "user_key": "changed",
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None


@pytest.mark.integration_test
async def test_rule_filter_fails_hard_when_unevaluatable(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
    root_org,
) -> None:
    # A filtered rule that cannot be evaluated must fail hard (surface an error),
    # never silently deny -- a silent deny would mask the misconfiguration.
    bob = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    create_named_person(graphapi_post, bob, "Bob", "Bertelsen")
    itsystem = create_itsystem(graphapi_post)
    bob_ituser = create_ituser_for(graphapi_post, bob, itsystem, "bob-account")

    await make_policy(
        another_transaction,
        "alice-corrupt-filter",
        actors=[("role", "editor")],
        rules=[("Mutation", "ituser_update", None, "not json")],
    )
    set_auth(role="editor")

    response = graphapi_post(
        UPDATE_ITUSER,
        variables={
            "input": {
                "uuid": bob_ituser,
                "user_key": "changed",
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    # Fails hard with the CEL evaluation error, not a silent permission deny.
    assert response.errors is not None
    assert any("CEL" in (e.get("message") or "") for e in response.errors)


# A grab-bag of filters that must all fail hard (surface an error), never
# silently deny -- each exercises a distinct malformed/unevaluatable branch of
# the check-spec engine.
MALFORMED_FILTERS = [
    # Unknown key in a (person) sub-filter.
    '{"collection": "ituser", "check": "IN", "field": input.uuid,'
    ' "filter": {"employee": {"bogus": 1}}}',
    # A sub-filter that is not an object.
    '{"collection": "ituser", "check": "IN", "field": input.uuid,'
    ' "filter": {"employee": 5}}',
    # An invalid uuid inside a sub-filter.
    '{"collection": "ituser", "check": "IN", "field": input.uuid,'
    ' "filter": {"employee": {"uuids": ["not-a-uuid"]}}}',
    # An invalid uuid inside a registration sub-filter.
    '{"collection": "ituser", "check": "EXISTS",'
    ' "filter": {"employee": {"registration": {"actors": ["not-a-uuid"]}}}}',
    # The check-spec filter is not a map.
    '{"collection": "ituser", "check": "IN", "field": input.uuid, "filter": 5}',
    # No collection.
    '{"check": "IN", "field": input.uuid, "filter": {}}',
    # The pinned field is not a uuid.
    '{"collection": "ituser", "check": "IN", "field": "not-a-uuid", "filter": {}}',
    # An unknown check kind.
    '{"collection": "ituser", "check": "NOPE", "field": input.uuid, "filter": {}}',
    # An unsupported collection.
    '{"collection": "bogus", "check": "EXISTS", "filter": {}}',
    # The expression returns neither a map nor a list.
    '"not-a-check-spec"',
    # A list containing a non-map.
    '[{"collection": "ituser", "check": "EXISTS", "filter": {}}, 5]',
    # A genuine CEL evaluation error (index out of range), not a missing var.
    "[1, 2][9]",
    # A non-object org_unit sub-filter (ancestor).
    '{"collection": "org_unit", "check": "EXISTS", "filter": {"ancestor": 5}}',
    # An invalid uuid in an org_unit sub-filter.
    '{"collection": "org_unit", "check": "EXISTS", "filter": {"uuids": ["x"]}}',
    # A non-object owner sub-filter.
    '{"collection": "org_unit", "check": "EXISTS", "filter": {"owner": 5}}',
    # An invalid uuid in an owner sub-filter.
    '{"collection": "owner", "check": "EXISTS", "filter": {"uuids": ["x"]}}',
]


@pytest.mark.integration_test
@pytest.mark.parametrize("filter_cel", MALFORMED_FILTERS)
async def test_rule_filter_malformed_fails_hard(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
    root_org,
    filter_cel: str,
) -> None:
    bob = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    create_named_person(graphapi_post, bob, "Bob", "Bertelsen")
    itsystem = create_itsystem(graphapi_post)
    bob_ituser = create_ituser_for(graphapi_post, bob, itsystem, "bob-account")

    await make_policy(
        another_transaction,
        "malformed-filter",
        actors=[("role", "editor")],
        rules=[("Mutation", "ituser_update", None, filter_cel)],
    )
    set_auth(role="editor")

    response = graphapi_post(
        UPDATE_ITUSER,
        variables={
            "input": {
                "uuid": bob_ituser,
                "user_key": "changed",
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    # An error surfaced -- and not the silent permission deny.
    assert response.errors is not None
    assert not denied(response)


# Owner policy
# ------------
# The migration seeds an "Owner" policy bound to the `owner` role whose
# per-mutator rules grant access only when the caller owns the affected entity.
# In the default config the caller's employee uuid is `token.uuid`, so we set
# the acting owner's `user_uuid` to the person that owns the entity.

# Two owners: X owns things below; Y owns nothing.
OWNER_X = "a1a1a1a1-0000-0000-0000-000000000001"
OWNER_Y = "b2b2b2b2-0000-0000-0000-000000000002"

CREATE_OWNER = """
  mutation CreateOwner($input: OwnerCreateInput!) {
    owner_create(input: $input) { uuid }
  }
"""

CREATE_ORG_UNIT = """
  mutation CreateOU($input: OrganisationUnitCreateInput!) {
    org_unit_create(input: $input) { uuid }
  }
"""

UPDATE_ORG_UNIT = """
  mutation UpdateOU($input: OrganisationUnitUpdateInput!) {
    org_unit_update(input: $input) { uuid }
  }
"""

UPDATE_EMPLOYEE = """
  mutation UpdateEmployee($input: EmployeeUpdateInput!) {
    employee_update(input: $input) { uuid }
  }
"""

CREATE_ITUSERS = """
  mutation CreateITUsers($input: [ITUserCreateInput!]!) {
    itusers_create(input: $input) { uuid }
  }
"""

UPDATE_MANAGER = """
  mutation UpdateManager($input: ManagerUpdateInput!) {
    manager_update(input: $input) { uuid }
  }
"""

TERMINATE_MANAGER = """
  mutation TerminateManager($input: ManagerTerminateInput!) {
    manager_terminate(input: $input) { uuid }
  }
"""

OU_TYPE = "c0c0c0c0-0000-0000-0000-0000000000ff"


@pytest.mark.integration_test
async def test_owner_policy_bootstrapped(
    another_transaction: AnotherTransaction, empty_db
) -> None:
    async with another_transaction() as (_, session):
        policy = (
            await session.scalars(select(db.Policy).where(db.Policy.name == "Owner"))
        ).one()
        assert policy.activated is True

        # Bound to the "owner" role.
        actors = (
            await session.scalars(
                select(db.PolicyActor).where(db.PolicyActor.policy_fk == policy.id)
            )
        ).all()
        assert [(actor.kind, actor.value) for actor in actors] == [("role", "owner")]

        rules = (
            await session.execute(
                select(
                    db.PolicyRule.type,
                    db.PolicyRule.field,
                    db.PolicyRule.condition,
                    db.PolicyRule.filter,
                ).where(db.PolicyRule.policy_fk == policy.id)
            )
        ).all()
    pairs = {(rule.type, rule.field) for rule in rules}
    # No wildcards; a representative sample across the covered mutators.
    assert not any(t == "*" or f == "*" for (t, f) in pairs)
    for field in (
        "org_unit_create",
        "org_unit_update",
        "employee_update",
        "ituser_update",
        "itusers_create",
        "related_units_update",
    ):
        assert ("Mutation", field) in pairs
    # Every rule is a filter (the ownership check) with no extra condition.
    assert all(rule.condition is None and rule.filter is not None for rule in rules)
    # The filters reference the lazy `actor` variable.
    assert all("actor" in rule.filter for rule in rules)


def make_owner(
    graphapi_post: GraphAPIPost,
    owner: str,
    *,
    org_unit: str | None = None,
    person: str | None = None,
) -> None:
    """Record that ``owner`` (a person) owns the given org-unit or person."""
    input: dict = {"owner": owner, "validity": {"from": "2020-01-01"}}
    if org_unit is not None:
        input["org_unit"] = org_unit
    if person is not None:
        input["person"] = person
    response = graphapi_post(CREATE_OWNER, variables={"input": input})
    assert response.errors is None, response.errors


def new_org_unit(graphapi_post: GraphAPIPost, name: str, parent: str | None) -> object:
    return graphapi_post(
        CREATE_ORG_UNIT,
        variables={
            "input": {
                "name": name,
                "user_key": name,
                "parent": parent,
                "org_unit_type": OU_TYPE,
                "validity": {"from": "2020-01-01"},
            }
        },
    )


def ituser_input(person: str, itsystem: str, user_key: str) -> dict:
    return {
        "user_key": user_key,
        "itsystem": itsystem,
        "person": person,
        "validity": {"from": "2020-01-01"},
    }


@pytest.mark.integration_test
async def test_owner_org_unit_object_and_hierarchy(
    graphapi_post: GraphAPIPost,
    empty_db,
    root_org,
    create_org_unit,
    set_auth: SetAuth,
) -> None:
    # X owns `owned` directly and `root` (an ancestor of `child`); Y owns nothing.
    create_named_person(graphapi_post, OWNER_X, "Xenia", "Xu")
    create_named_person(graphapi_post, OWNER_Y, "Yannick", "Yde")
    owned = str(create_org_unit("owned"))
    root = str(create_org_unit("root"))
    child = str(create_org_unit("child", UUID(root)))
    make_owner(graphapi_post, OWNER_X, org_unit=owned)
    make_owner(graphapi_post, OWNER_X, org_unit=root)

    # A rename (no `parent`) exercises the UNIT(input.uuid) rule without a move;
    # since `input.parent` is null the `current`-referencing branch is not taken,
    # so `current` is never loaded.
    def rename(uuid: str) -> object:
        return graphapi_post(
            UPDATE_ORG_UNIT,
            variables={
                "input": {
                    "uuid": uuid,
                    "name": "Renamed",
                    "validity": {"from": "2021-01-01"},
                }
            },
        )

    # Y owns nothing -> denied for both the owned unit and the descendant.
    set_auth(role="owner", user_uuid=OWNER_Y)
    assert denied(rename(owned))
    assert denied(rename(child))

    # X owns the descendant via its ancestor `root`, and `owned` directly.
    set_auth(role="owner", user_uuid=OWNER_X)
    assert rename(child).errors is None
    assert rename(owned).errors is None


@pytest.mark.integration_test
async def test_owner_person_linked_detail(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    # An IT-user links only a person; the OBJ_PERSON rule grants its owner.
    person = "eeeeeeee-0000-0000-0000-0000000000ee"
    create_named_person(graphapi_post, OWNER_X, "Xenia", "Xu")
    create_named_person(graphapi_post, OWNER_Y, "Yannick", "Yde")
    create_named_person(graphapi_post, person, "Percy", "Pil")
    make_owner(graphapi_post, OWNER_X, person=person)
    itsystem = create_itsystem(graphapi_post)
    ituser = create_ituser_for(graphapi_post, person, itsystem, "acct")

    def update() -> object:
        return graphapi_post(
            UPDATE_ITUSER,
            variables={
                "input": {
                    "uuid": ituser,
                    "user_key": "changed",
                    "validity": {"from": "2020-01-01"},
                }
            },
        )

    set_auth(role="owner", user_uuid=OWNER_Y)
    assert denied(update())
    set_auth(role="owner", user_uuid=OWNER_X)
    assert update().errors is None


@pytest.mark.integration_test
async def test_owner_employee_object_and_create(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    person = "eeeeeeee-0000-0000-0000-0000000000ee"
    create_named_person(graphapi_post, OWNER_X, "Xenia", "Xu")
    create_named_person(graphapi_post, OWNER_Y, "Yannick", "Yde")
    create_named_person(graphapi_post, person, "Percy", "Pil")
    make_owner(graphapi_post, OWNER_X, person=person)

    def update_employee(uuid: str) -> object:
        return graphapi_post(
            UPDATE_EMPLOYEE,
            variables={"input": {"uuid": uuid, "validity": {"from": "2020-01-01"}}},
        )

    # X owns `person` -> may update it; Y may not.
    set_auth(role="owner", user_uuid=OWNER_Y)
    assert denied(update_employee(person))
    set_auth(role="owner", user_uuid=OWNER_X)
    assert update_employee(person).errors is None

    # A brand-new employee has no owners, so employee_create is denied even for X.
    created = graphapi_post(
        CREATE_EMPLOYEE,
        variables={
            "input": {
                "uuid": "f0f0f0f0-0000-0000-0000-0000000000f0",
                "given_name": "New",
                "surname": "Comer",
            }
        },
    )
    assert denied(created)


@pytest.mark.integration_test
async def test_owner_create_under_owned_parent(
    graphapi_post: GraphAPIPost,
    empty_db,
    root_org,
    create_org_unit,
    set_auth: SetAuth,
) -> None:
    create_named_person(graphapi_post, OWNER_X, "Xenia", "Xu")
    owned = str(create_org_unit("owned"))
    unowned = str(create_org_unit("unowned"))
    make_owner(graphapi_post, OWNER_X, org_unit=owned)

    set_auth(role="owner", user_uuid=OWNER_X)

    # Under an owned parent -> granted.
    assert new_org_unit(graphapi_post, "sub", owned).errors is None
    # Under a parent X does not own -> denied.
    assert denied(new_org_unit(graphapi_post, "sub2", unowned))
    # A root unit (no parent) has no parent to own -> denied.
    assert denied(new_org_unit(graphapi_post, "newroot", None))


@pytest.mark.integration_test
async def test_owner_move_requires_new_parent_ownership(
    graphapi_post: GraphAPIPost,
    empty_db,
    root_org,
    create_org_unit,
    set_auth: SetAuth,
) -> None:
    # X owns `home` (and thus its descendant `movable`) and the `new_parent`,
    # but not `other`.
    create_named_person(graphapi_post, OWNER_X, "Xenia", "Xu")
    home = str(create_org_unit("home"))
    movable = str(create_org_unit("movable", UUID(home)))
    new_parent = str(create_org_unit("new-parent"))
    other = str(create_org_unit("other"))
    make_owner(graphapi_post, OWNER_X, org_unit=home)
    make_owner(graphapi_post, OWNER_X, org_unit=new_parent)

    set_auth(role="owner", user_uuid=OWNER_X)

    def move(parent: str) -> object:
        return graphapi_post(
            UPDATE_ORG_UNIT,
            variables={
                "input": {
                    "uuid": movable,
                    "parent": parent,
                    "validity": {"from": "2021-01-01"},
                }
            },
        )

    # Moving to a parent X does not own is denied (owns the unit but not `other`).
    assert denied(move(other))
    # Moving to an owned new parent is granted.
    assert move(new_parent).errors is None


@pytest.mark.integration_test
async def test_owner_bulk_requires_all_items_owned(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    # itusers_create takes a list; the owner must own every item's person.
    owned1 = "e1e1e1e1-0000-0000-0000-0000000000e1"
    owned2 = "e2e2e2e2-0000-0000-0000-0000000000e2"
    foreign = "e3e3e3e3-0000-0000-0000-0000000000e3"
    create_named_person(graphapi_post, OWNER_X, "Xenia", "Xu")
    for uuid, name in ((owned1, "One"), (owned2, "Two"), (foreign, "Three")):
        create_named_person(graphapi_post, uuid, name, "Person")
    make_owner(graphapi_post, OWNER_X, person=owned1)
    make_owner(graphapi_post, OWNER_X, person=owned2)
    itsystem = create_itsystem(graphapi_post)

    set_auth(role="owner", user_uuid=OWNER_X)

    # Every person in the batch is owned -> granted.
    granted = graphapi_post(
        CREATE_ITUSERS,
        variables={
            "input": [
                ituser_input(owned1, itsystem, "a1"),
                ituser_input(owned2, itsystem, "a2"),
            ]
        },
    )
    assert granted.errors is None

    # One person is not owned -> the whole batch is denied.
    batch = graphapi_post(
        CREATE_ITUSERS,
        variables={
            "input": [
                ituser_input(owned1, itsystem, "b1"),
                ituser_input(foreign, itsystem, "b2"),
            ]
        },
    )
    assert denied(batch)

    # An empty batch yields no check-specs, so it is denied (parity with legacy
    # check_owner's empty-entity-set deny), not vacuously granted.
    empty = graphapi_post(CREATE_ITUSERS, variables={"input": []})
    assert denied(empty)


@pytest.mark.integration_test
async def test_owner_unit_linked_detail_and_hierarchy(
    graphapi_post: GraphAPIPost,
    empty_db,
    root_org,
    create_org_unit,
    create_manager,
    set_auth: SetAuth,
) -> None:
    # A manager is an org-function linked (mandatorily) to an org-unit, so it
    # exercises the OBJ_UNIT path (an org_unit sub-filter joined into an
    # org-function predicate). The manager sits on `child`; X owns only the
    # ancestor `root`, so the grant must flow down the hierarchy.
    create_named_person(graphapi_post, OWNER_X, "Xenia", "Xu")
    create_named_person(graphapi_post, OWNER_Y, "Yannick", "Yde")
    root = create_org_unit("root")
    child = create_org_unit("child", root)
    make_owner(graphapi_post, OWNER_X, org_unit=str(root))
    manager = str(create_manager(child))

    def update() -> object:
        return graphapi_post(
            UPDATE_MANAGER,
            variables={"input": {"uuid": manager, "validity": {"from": "2021-01-01"}}},
        )

    # Y owns nothing -> denied.
    set_auth(role="owner", user_uuid=OWNER_Y)
    assert denied(update())
    # X owns the ancestor -> may update the manager on the descendant, and
    # terminate it.
    set_auth(role="owner", user_uuid=OWNER_X)
    assert update().errors is None
    assert (
        graphapi_post(
            TERMINATE_MANAGER,
            variables={"input": {"uuid": manager, "to": "2050-01-01"}},
        ).errors
        is None
    )


@pytest.mark.integration_test
async def test_owner_may_delete_owned_detail(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    # `ituser_delete` takes a bare `uuid`; the owner of the linked person may
    # delete it, others may not.
    person = "eeeeeeee-0000-0000-0000-0000000000ee"
    create_named_person(graphapi_post, OWNER_X, "Xenia", "Xu")
    create_named_person(graphapi_post, OWNER_Y, "Yannick", "Yde")
    create_named_person(graphapi_post, person, "Percy", "Pil")
    make_owner(graphapi_post, OWNER_X, person=person)
    itsystem = create_itsystem(graphapi_post)
    ituser = create_ituser_for(graphapi_post, person, itsystem, "acct")

    set_auth(role="owner", user_uuid=OWNER_Y)
    assert denied(graphapi_post(DELETE_ITUSER, variables={"uuid": ituser}))
    set_auth(role="owner", user_uuid=OWNER_X)
    assert graphapi_post(DELETE_ITUSER, variables={"uuid": ituser}).errors is None


@pytest.mark.integration_test
@pytest.mark.envvar(
    # A bogus authoritative IT-system: resolving any actor would raise.
    {
        "KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS": "00000000-0000-0000-0000-000000000000"
    }
)
async def test_owner_lazy_actor_not_resolved_when_unreferenced(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    another_transaction: AnotherTransaction,
    empty_db,
    root_org,
) -> None:
    # A filter that references only `input` (never `actor`) must not trigger
    # actor resolution. We configure an authoritative IT-system for owners so
    # that *any* actor resolution would fail (no matching IT-user); a non-actor
    # rule still succeeds, proving `actor` is left unresolved (lazy).
    person = "eeeeeeee-0000-0000-0000-0000000000ee"
    create_named_person(graphapi_post, person, "Percy", "Pil")
    itsystem = create_itsystem(graphapi_post)
    ituser = create_ituser_for(graphapi_post, person, itsystem, "acct")

    # Anyone may update any IT-user; the filter pins the object but references no
    # `actor`.
    await make_policy(
        another_transaction,
        "any-ituser",
        actors=[("all", "")],
        rules=[("Mutation", "ituser_update", None, ituser_check_spec("{}"))],
    )

    # A plain user (no `owner` role, so the bootstrap Owner policy's
    # actor-referencing rules never apply).
    set_auth(user_uuid=person)

    response = graphapi_post(
        UPDATE_ITUSER,
        variables={
            "input": {
                "uuid": ituser,
                "user_key": "changed",
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None


# Policy CRUD API
# ---------------

POLICYADMIN = str(POLICYADMIN_UUID)

DECLARE_POLICY = """
  mutation DeclarePolicy($input: PolicyDeclareInput!) {
    policy_declare(input: $input) {
      uuid
      name
      description
      activated
    }
  }
"""

READ_POLICIES = """
  query ReadPolicies {
    policies {
      objects {
        uuid
        name
        description
        activated
      }
    }
  }
"""

PAGINATE_POLICIES = """
  query PaginatePolicies($limit: int, $cursor: Cursor) {
    policies(limit: $limit, cursor: $cursor) {
      objects {
        uuid
        name
      }
      page_info {
        next_cursor
      }
    }
  }
"""

FILTER_POLICIES = """
  query FilterPolicies($uuids: [UUID!]) {
    policies(filter: { uuids: $uuids }) {
      objects {
        uuid
        name
      }
    }
  }
"""

DELETE_POLICY = """
  mutation DeletePolicy($uuid: UUID!) {
    policy_delete(input: { uuid: $uuid })
  }
"""

DECLARE_ACTOR = """
  mutation DeclareActor($input: PolicyActorDeclareInput!) {
    policy_actor_declare(input: $input) {
      uuid
      kind
      value
    }
  }
"""

DECLARE_ACTORS = """
  mutation DeclareActors($input: PolicyActorsDeclareInput!) {
    policy_actors_declare(input: $input) {
      uuid
      kind
      value
    }
  }
"""

DELETE_ACTOR = """
  mutation DeleteActor($uuid: UUID!) {
    policy_actor_delete(input: { uuid: $uuid })
  }
"""

READ_POLICY_ACTORS = """
  query ReadPolicyActors($uuids: [UUID!]) {
    policies(filter: { uuids: $uuids }) {
      objects {
        uuid
        actors {
          uuid
          kind
          value
        }
      }
    }
  }
"""

FILTER_BY_ACTOR = """
  query FilterByActor($filter: PolicyFilter) {
    policies(filter: $filter) {
      objects {
        uuid
        name
      }
    }
  }
"""

NOT_FOUND_UUID = "d0d19f81-36e0-46bd-9be5-49d31b1e15a7"


def declare_policy(graphapi_post: GraphAPIPost, **input) -> GQLResponse:
    return graphapi_post(DECLARE_POLICY, variables={"input": input})


def read_policies(graphapi_post: GraphAPIPost) -> list[dict]:
    response = graphapi_post(READ_POLICIES)
    assert response.errors is None
    return response.data["policies"]["objects"]


def create_policy(graphapi_post: GraphAPIPost, name: str) -> str:
    response = declare_policy(graphapi_post, name=name)
    assert response.errors is None
    return response.data["policy_declare"]["uuid"]


def declare_actor(
    graphapi_post: GraphAPIPost, policy: str, kind: str, value: str
) -> str:
    response = graphapi_post(
        DECLARE_ACTOR,
        variables={"input": {"policy": policy, "kind": kind, "value": value}},
    )
    assert response.errors is None
    return response.data["policy_actor_declare"]["uuid"]


def policy_names_for_filter(graphapi_post: GraphAPIPost, filter_value) -> set[str]:
    response = graphapi_post(FILTER_BY_ACTOR, variables={"filter": filter_value})
    assert response.errors is None
    return {obj["name"] for obj in response.data["policies"]["objects"]}


CREATE_EMPLOYEE = """
  mutation CreateEmployee($input: EmployeeCreateInput!) {
    employee_create(input: $input) {
      uuid
    }
  }
"""


@pytest.mark.integration_test
async def test_policyadmin_is_bootstrapped(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The migration inserts the policyadmin policy, so it is always present.
    policies = {p["uuid"]: p for p in read_policies(graphapi_post)}
    assert POLICYADMIN in policies
    assert policies[POLICYADMIN]["name"] == "Policy Administrator"


@pytest.mark.integration_test
async def test_policyadmin_cannot_be_deleted(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = graphapi_post(DELETE_POLICY, variables={"uuid": POLICYADMIN})
    assert response.errors is not None

    # It is still there.
    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert POLICYADMIN in uuids


@pytest.mark.integration_test
async def test_policy_create_and_read(graphapi_post: GraphAPIPost, empty_db) -> None:
    response = declare_policy(
        graphapi_post,
        name="GDPR",
        description="Data protection policy",
    )
    assert response.errors is None
    created = response.data["policy_declare"]
    assert created["name"] == "GDPR"
    assert created["description"] == "Data protection policy"
    # Policies default to activated on declare.
    assert created["activated"] is True

    policies = {p["uuid"]: p for p in read_policies(graphapi_post)}
    assert created["uuid"] in policies
    assert policies[created["uuid"]]["name"] == "GDPR"
    # The bootstrap policy coexists with the created one.
    assert POLICYADMIN in policies


@pytest.mark.integration_test
async def test_policy_declare_updates_existing(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    baseline = len(read_policies(graphapi_post))
    created = declare_policy(graphapi_post, name="Initial")
    uuid = created.data["policy_declare"]["uuid"]

    updated = declare_policy(
        graphapi_post,
        uuid=uuid,
        name="Renamed",
        description="now with a description",
        activated=False,
    )
    assert updated.errors is None
    obj = updated.data["policy_declare"]
    assert obj["uuid"] == uuid
    assert obj["name"] == "Renamed"
    assert obj["description"] == "now with a description"
    assert obj["activated"] is False

    # Declaring with a uuid updates rather than creates: just one new policy.
    assert len(read_policies(graphapi_post)) == baseline + 1


@pytest.mark.integration_test
async def test_policy_declare_with_uuid_creates(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # Declaring with a client-supplied UUID that does not exist creates it (this
    # is what lets the create flow generate the UUID up front).
    response = declare_policy(
        graphapi_post,
        uuid=NOT_FOUND_UUID,
        name="client-uuid",
    )
    assert response.errors is None
    assert response.data["policy_declare"]["uuid"] == NOT_FOUND_UUID

    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert NOT_FOUND_UUID in uuids


@pytest.mark.integration_test
async def test_policy_delete(graphapi_post: GraphAPIPost, empty_db) -> None:
    created = declare_policy(graphapi_post, name="ToDelete")
    uuid = created.data["policy_declare"]["uuid"]

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": uuid})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True

    uuids = {p["uuid"] for p in read_policies(graphapi_post)}
    assert uuid not in uuids
    # Deleting a normal policy leaves the bootstrap policy untouched.
    assert POLICYADMIN in uuids


@pytest.mark.integration_test
async def test_policy_filter_by_uuid(graphapi_post: GraphAPIPost, empty_db) -> None:
    created = declare_policy(graphapi_post, name="Filtered")
    uuid = created.data["policy_declare"]["uuid"]

    response = graphapi_post(FILTER_POLICIES, variables={"uuids": [uuid]})
    assert response.errors is None
    objects = response.data["policies"]["objects"]
    assert len(objects) == 1
    assert objects[0]["uuid"] == uuid
    assert objects[0]["name"] == "Filtered"


@pytest.mark.integration_test
async def test_policy_pagination(graphapi_post: GraphAPIPost, empty_db) -> None:
    # Create a handful of policies to page through (plus the bootstrap ones).
    baseline = len(read_policies(graphapi_post))
    created: set[str] = set()
    for i in range(5):
        response = declare_policy(graphapi_post, name=f"policy-{i}")
        assert response.errors is None
        created.add(response.data["policy_declare"]["uuid"])

    # Page through them two at a time using the keyset cursor.
    seen: list[str] = []
    cursor = None
    for _ in range(10):  # safety bound to avoid an infinite loop
        response = graphapi_post(
            PAGINATE_POLICIES, variables={"limit": 2, "cursor": cursor}
        )
        assert response.errors is None
        page = response.data["policies"]
        seen.extend(obj["uuid"] for obj in page["objects"])
        cursor = page["page_info"]["next_cursor"]
        if cursor is None:
            break
    else:  # pragma: no cover
        raise AssertionError("pagination did not terminate")

    # Every created policy plus the bootstrap ones was returned exactly once.
    assert len(seen) == baseline + 5
    assert created <= set(seen)
    assert POLICYADMIN in seen


@pytest.mark.integration_test
async def test_policy_actor_declare_and_read(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "with-actors")
    declare_actor(graphapi_post, policy, "role", "admin")
    declare_actor(graphapi_post, policy, "role", "reader")

    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert response.errors is None
    actors = response.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {
        ("role", "admin"),
        ("role", "reader"),
    }


@pytest.mark.integration_test
async def test_policy_actor_delete(graphapi_post: GraphAPIPost, empty_db) -> None:
    policy = create_policy(graphapi_post, "with-actor")
    actor_uuid = declare_actor(graphapi_post, policy, "role", "admin")

    deleted = graphapi_post(DELETE_ACTOR, variables={"uuid": actor_uuid})
    assert deleted.errors is None
    assert deleted.data["policy_actor_delete"] is True

    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert response.errors is None
    assert response.data["policies"]["objects"][0]["actors"] == []


@pytest.mark.integration_test
async def test_policy_actor_filter_cases(graphapi_post: GraphAPIPost, empty_db) -> None:
    # The bootstrap "Legacy", "Public" and "Introspection" policies each have an
    # "all" actor that matches every role-based actor filter (covered by
    # test_policy_actor_all_matches_any_filter). Exclude them from the observed
    # sets so these cases isolate role-based matching. They are not deleted: the
    # "Public" policy grants the (public) Policy object fields this test reads.
    catch_all = {"Legacy", "Public", "Introspection"}

    def names_for(filter: dict | None) -> set[str]:
        return policy_names_for_filter(graphapi_post, filter) - catch_all

    # role-policy is bound to role "admin"; reader-policy to role "reader";
    # unbound-policy has no actors. The bootstrap "Policy Administrator" is
    # hard-bound to role "admin".
    role_policy = create_policy(graphapi_post, "role-policy")
    declare_actor(graphapi_post, role_policy, "role", "admin")
    reader_policy = create_policy(graphapi_post, "reader-policy")
    declare_actor(graphapi_post, reader_policy, "role", "reader")
    create_policy(graphapi_post, "unbound-policy")

    # The bootstrap "Administrator" policy is bound to the "admin" role, "Reader"
    # to the "reader" role and "Owner" to the "owner" role.
    everything = {
        "role-policy",
        "reader-policy",
        "unbound-policy",
        "Policy Administrator",
        "Administrator",
        "Reader",
        "Owner",
    }
    has_actor = {
        "role-policy",
        "reader-policy",
        "Policy Administrator",
        "Administrator",
        "Reader",
        "Owner",
    }
    admins = {"role-policy", "Policy Administrator", "Administrator"}

    # No actor constraint -> all policies (including the actor-less one).
    assert {
        p["name"] for p in read_policies(graphapi_post)
    } - catch_all == everything  # omitted
    assert names_for(None) == everything  # null
    assert names_for({}) == everything  # {}
    assert names_for({"actor": None}) == everything

    # Empty actor filter -> policies that have *any* actor (excludes unbound).
    assert names_for({"actor": {}}) == has_actor

    # Matching by role. Both role-policy and the bootstrap policy are bound to
    # "admin"; "reader" matches reader-policy and the bootstrap "Reader".
    assert names_for({"actor": {"roles": ["admin"]}}) == admins
    assert names_for({"actor": {"roles": ["reader"]}}) == {
        "reader-policy",
        "Reader",
    }

    # An empty list matches nothing.
    assert names_for({"actor": {"roles": []}}) == set()

    # Multiple roles are OR'ed together.
    assert names_for({"actor": {"roles": ["admin", "reader"]}}) == admins | {
        "reader-policy",
        "Reader",
    }

    # No actor matches a non-existent role.
    assert names_for({"actor": {"roles": ["nobody"]}}) == set()


@pytest.mark.integration_test
async def test_policyadmin_hard_bound_to_admin_role(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [POLICYADMIN]})
    assert response.errors is None
    actors = response.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {("role", "admin")}


@pytest.mark.integration_test
async def test_policyadmin_cannot_be_modified(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # Updating the policy itself is rejected.
    update = declare_policy(
        graphapi_post,
        uuid=POLICYADMIN,
        name="Hacked",
    )
    assert update.errors is not None

    # Declaring an actor on it is rejected.
    add = graphapi_post(
        DECLARE_ACTOR,
        variables={
            "input": {"policy": POLICYADMIN, "kind": "role", "value": "mallory"}
        },
    )
    assert add.errors is not None

    # Its hard-bound admin role is unchanged.
    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [POLICYADMIN]})
    actors = read.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {("role", "admin")}


@pytest.mark.integration_test
async def test_policy_actor_declare_is_idempotent(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    first = declare_actor(graphapi_post, policy, "role", "admin")
    second = declare_actor(graphapi_post, policy, "role", "admin")
    # Declaring the same actor twice returns the same binding, no duplicate.
    assert first == second
    response = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert len(response.data["policies"]["objects"][0]["actors"]) == 1


@pytest.mark.integration_test
async def test_policy_actors_declare_replaces_set(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_ACTORS,
        variables={
            "input": {
                "policy": policy,
                "actors": [
                    {"kind": "role", "value": "admin"},
                    {"kind": "role", "value": "editor"},
                ],
            }
        },
    )
    assert response.errors is None
    assert len(response.data["policy_actors_declare"]) == 2

    # Declaring a new set replaces the old one: "editor" is dropped, "reader" is
    # added, and "admin" is kept (unchanged).
    again = graphapi_post(
        DECLARE_ACTORS,
        variables={
            "input": {
                "policy": policy,
                "actors": [
                    {"kind": "role", "value": "admin"},
                    {"kind": "role", "value": "reader"},
                ],
            }
        },
    )
    assert again.errors is None

    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    actors = read.data["policies"]["objects"][0]["actors"]
    assert {(a["kind"], a["value"]) for a in actors} == {
        ("role", "admin"),
        ("role", "reader"),
    }

    # Declaring an empty set clears all actors.
    cleared = graphapi_post(
        DECLARE_ACTORS, variables={"input": {"policy": policy, "actors": []}}
    )
    assert cleared.errors is None
    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [policy]})
    assert read.data["policies"]["objects"][0]["actors"] == []


# Rules
# -----

DECLARE_RULE = """
  mutation DeclareRule($input: PolicyRuleDeclareInput!) {
    policy_rule_declare(input: $input) {
      uuid
      type
      field
      condition
      filter
    }
  }
"""

DECLARE_RULES = """
  mutation DeclareRules($input: PolicyRulesDeclareInput!) {
    policy_rules_declare(input: $input) {
      uuid
      type
      field
      condition
      filter
    }
  }
"""

DELETE_RULE = """
  mutation DeleteRule($uuid: UUID!) {
    policy_rule_delete(input: { uuid: $uuid })
  }
"""

READ_POLICY_RULES = """
  query ReadPolicyRules($uuids: [UUID!]) {
    policies(filter: { uuids: $uuids }) {
      objects {
        uuid
        rules {
          uuid
          type
          field
          condition
          filter
        }
      }
    }
  }
"""


def declare_rule(
    graphapi_post: GraphAPIPost,
    policy: str,
    type: str,
    field: str,
    condition: str | None = None,
    filter: str | None = None,
) -> str:
    response = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {
                "policy": policy,
                "type": type,
                "field": field,
                "condition": condition,
                "filter": filter,
            }
        },
    )
    assert response.errors is None
    return response.data["policy_rule_declare"]["uuid"]


def read_policy_rules(graphapi_post: GraphAPIPost, uuid: str) -> list[dict]:
    response = graphapi_post(READ_POLICY_RULES, variables={"uuids": [uuid]})
    assert response.errors is None
    return response.data["policies"]["objects"][0]["rules"]


@pytest.mark.integration_test
async def test_policy_rule_declare_and_read(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "with-rules")
    declare_rule(graphapi_post, policy, "Query", "policies")
    declare_rule(graphapi_post, policy, "Policy", "*")

    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"]) for r in rules} == {
        ("Query", "policies"),
        ("Policy", "*"),
    }


@pytest.mark.integration_test
async def test_policy_rule_declare_is_idempotent(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    first = declare_rule(graphapi_post, policy, "Query", "policies")
    second = declare_rule(graphapi_post, policy, "Query", "policies")
    assert first == second
    assert len(read_policy_rules(graphapi_post, policy)) == 1


@pytest.mark.integration_test
async def test_policy_rules_declare_replaces_set(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_RULES,
        variables={
            "input": {
                "policy": policy,
                "rules": [
                    {"type": "Query", "field": "policies"},
                    {"type": "Mutation", "field": "policy_declare"},
                ],
            }
        },
    )
    assert response.errors is None
    assert len(response.data["policy_rules_declare"]) == 2

    again = graphapi_post(
        DECLARE_RULES,
        variables={
            "input": {
                "policy": policy,
                "rules": [
                    {"type": "Query", "field": "policies"},
                    {"type": "Policy", "field": "name"},
                ],
            }
        },
    )
    assert again.errors is None
    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"]) for r in rules} == {
        ("Query", "policies"),
        ("Policy", "name"),
    }

    cleared = graphapi_post(
        DECLARE_RULES, variables={"input": {"policy": policy, "rules": []}}
    )
    assert cleared.errors is None
    assert read_policy_rules(graphapi_post, policy) == []


@pytest.mark.integration_test
async def test_policy_rule_delete(graphapi_post: GraphAPIPost, empty_db) -> None:
    policy = create_policy(graphapi_post, "p")
    rule_uuid = declare_rule(graphapi_post, policy, "Query", "policies")
    deleted = graphapi_post(DELETE_RULE, variables={"uuid": rule_uuid})
    assert deleted.errors is None
    assert deleted.data["policy_rule_delete"] is True
    assert read_policy_rules(graphapi_post, policy) == []


@pytest.mark.integration_test
async def test_policyadmin_rules_bootstrapped(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    pairs = {
        (r["type"], r["field"]) for r in read_policy_rules(graphapi_post, POLICYADMIN)
    }
    assert ("Query", "policies") in pairs
    assert ("Mutation", "policy_declare") in pairs
    assert ("Mutation", "policy_rules_declare") in pairs


@pytest.mark.integration_test
async def test_policyadmin_rules_cannot_be_modified(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    add = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {"policy": POLICYADMIN, "type": "Query", "field": "employees"}
        },
    )
    assert add.errors is not None
    replace = graphapi_post(
        DECLARE_RULES, variables={"input": {"policy": POLICYADMIN, "rules": []}}
    )
    assert replace.errors is not None


@pytest.mark.integration_test
async def test_pbac_admin_can_read_policies(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The admin token has the "admin" role, which the bootstrap Policy
    # Administrator is bound to and which grants Query.policies.
    response = graphapi_post(READ_POLICIES)
    assert response.errors is None


@pytest.mark.integration_test
async def test_pbac_denies_without_grant(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    set_auth(role="nobody", user_uuid="11111111-1111-1111-1111-111111111111")
    response = graphapi_post(READ_POLICIES)
    assert response.errors is not None


@pytest.mark.integration_test
async def test_pbac_grant_via_policy(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    # As admin (RBAC), grant the "employee-reader" role read access to the
    # employees collection.
    policy = create_policy(graphapi_post, "employee-reader")
    declare_actor(graphapi_post, policy, "role", "employee-reader")
    declare_rule(graphapi_post, policy, "Query", "employees")

    # Become a token carrying only that role and switch to PBAC.
    set_auth(role="employee-reader")

    granted = graphapi_post(READ_EMPLOYEES)
    assert granted.errors is None

    # The role was not granted the policies collection.
    denied = graphapi_post(READ_POLICIES)
    assert denied.errors is not None


@pytest.mark.integration_test
async def test_pbac_grant_respects_activation(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db
) -> None:
    # A deactivated policy does not grant access.
    response = declare_policy(graphapi_post, name="inactive", activated=False)
    policy = response.data["policy_declare"]["uuid"]
    declare_actor(graphapi_post, policy, "role", "employee-reader")
    declare_rule(graphapi_post, policy, "Query", "employees")

    set_auth(role="employee-reader")

    denied = graphapi_post(READ_EMPLOYEES)
    assert denied.errors is not None


@pytest.mark.integration_test
async def test_policy_actor_all_matches_any_filter(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "everyone-policy")
    # An "all" actor has no value and matches every actor.
    declare_actor(graphapi_post, policy, "all", "")

    # It is returned regardless of the queried role...
    assert "everyone-policy" in policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["whatever"]}}
    )
    assert "everyone-policy" in policy_names_for_filter(
        graphapi_post, {"actor": {"roles": ["nobody"]}}
    )
    # ... and by the existence filter.
    assert "everyone-policy" in policy_names_for_filter(graphapi_post, {"actor": {}})


@pytest.mark.integration_test
async def test_administrator_policy_is_removable(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # Unlike the policyadmin policy, Administrator is a normal, removable policy
    # (and deleting it also removes its rules).
    by_name = {p["name"]: p["uuid"] for p in read_policies(graphapi_post)}
    admin_uuid = by_name["Administrator"]

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": admin_uuid})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True

    # Deletion succeeds (its rules are removed too, so no FK violation).
    assert admin_uuid not in {p["uuid"] for p in read_policies(graphapi_post)}


@pytest.mark.integration_test
async def test_policy_delete_removes_actors_and_rules(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "to-delete")
    declare_actor(graphapi_post, policy, "role", "x")
    declare_rule(graphapi_post, policy, "Query", "employees")

    deleted = graphapi_post(DELETE_POLICY, variables={"uuid": policy})
    assert deleted.errors is None
    assert deleted.data["policy_delete"] is True
    assert policy not in {p["uuid"] for p in read_policies(graphapi_post)}


# Rule conditions (CEL)
# ---------------------


@pytest.mark.integration_test
async def test_policy_rule_declare_with_condition(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "conditional")
    declare_rule(
        graphapi_post,
        policy,
        "Query",
        "employees",
        condition='"admin" in token.roles',
    )

    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"], r["condition"]) for r in rules} == {
        ("Query", "employees", '"admin" in token.roles')
    }


@pytest.mark.integration_test
async def test_policy_rule_empty_condition_is_unconditional(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # An empty-string condition is normalised to null (unconditional).
    policy = create_policy(graphapi_post, "p")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="")
    rules = read_policy_rules(graphapi_post, policy)
    assert rules[0]["condition"] is None


@pytest.mark.integration_test
async def test_policy_rule_condition_distinct_per_condition(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The same (type, field) may carry several conditions (each its own rule),
    # while re-declaring an identical (type, field, condition) is idempotent.
    policy = create_policy(graphapi_post, "p")
    declare_rule(graphapi_post, policy, "Query", "employees")  # unconditional
    declare_rule(graphapi_post, policy, "Query", "employees", condition="true")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="false")
    # Idempotent re-declares.
    declare_rule(graphapi_post, policy, "Query", "employees")
    declare_rule(graphapi_post, policy, "Query", "employees", condition="true")

    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"], r["condition"]) for r in rules} == {
        ("Query", "employees", None),
        ("Query", "employees", "true"),
        ("Query", "employees", "false"),
    }


@pytest.mark.integration_test
async def test_policy_rule_declare_rejects_invalid_condition(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {
                "policy": policy,
                "type": "Query",
                "field": "employees",
                "condition": "this is (not valid CEL",
            }
        },
    )
    assert response.errors is not None
    # Nothing was stored.
    assert read_policy_rules(graphapi_post, policy) == []


@pytest.mark.integration_test
async def test_policy_rules_declare_keys_on_condition(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The full-replace mutator treats (type, field, condition) as the identity.
    policy = create_policy(graphapi_post, "p")
    response = graphapi_post(
        DECLARE_RULES,
        variables={
            "input": {
                "policy": policy,
                "rules": [
                    {"type": "Query", "field": "employees"},
                    {
                        "type": "Query",
                        "field": "employees",
                        "condition": '"admin" in token.roles',
                    },
                ],
            }
        },
    )
    assert response.errors is None
    rules = read_policy_rules(graphapi_post, policy)
    assert {(r["type"], r["field"], r["condition"]) for r in rules} == {
        ("Query", "employees", None),
        ("Query", "employees", '"admin" in token.roles'),
    }


@pytest.mark.integration_test
async def test_policy_rule_filter_declare_and_read(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    policy = create_policy(graphapi_post, "filtered-rule")
    value = json.dumps(
        {
            "collection": "ituser",
            "check": "EXISTS",
            "filter": {"employee": {"query": "Bob"}},
        }
    )
    declare_rule(graphapi_post, policy, "Mutation", "ituser_update", filter=value)

    rules = read_policy_rules(graphapi_post, policy)
    assert len(rules) == 1
    assert rules[0]["field"] == "ituser_update"
    assert rules[0]["filter"] == value


@pytest.mark.integration_test
async def test_policy_rule_filter_allowed_on_any_field(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # Any rule may now carry a filter (compile-check only); the collection each
    # check-spec targets is chosen in the filter, not derived from the field. A
    # filter on a previously-"unsupported" field is therefore accepted.
    policy = create_policy(graphapi_post, "any-field-filter")
    for field in ("address_update", "employee_create", "org_unit_terminate"):
        declare_rule(
            graphapi_post,
            policy,
            "Mutation",
            field,
            filter=json.dumps(
                {"collection": "org_unit", "check": "EXISTS", "filter": {}}
            ),
        )
    assert {r["field"] for r in read_policy_rules(graphapi_post, policy)} == {
        "address_update",
        "employee_create",
        "org_unit_terminate",
    }


@pytest.mark.integration_test
async def test_policy_rule_filter_rejects_malformed(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # A filter that is not a compilable CEL expression is rejected at declare
    # time (`not json` references the undeclared variable `json`).
    policy = create_policy(graphapi_post, "malformed-filtered-rule")
    response = graphapi_post(
        DECLARE_RULE,
        variables={
            "input": {
                "policy": policy,
                "type": "Mutation",
                "field": "ituser_update",
                "filter": "not json",
            }
        },
    )
    assert response.errors is not None


@pytest.mark.integration_test
async def test_pbac_rule_filter_cel_scopes_to_caller(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    # The filter is a CEL expression referencing `token`: anyone may update the
    # IT-users linked to *their own* person, and no one else's.
    alice = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    bob = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    create_named_person(graphapi_post, alice, "Alice", "Andersen")
    create_named_person(graphapi_post, bob, "Bob", "Bertelsen")
    itsystem = create_itsystem(graphapi_post)
    alice_ituser = create_ituser_for(graphapi_post, alice, itsystem, "alice-account")
    bob_ituser = create_ituser_for(graphapi_post, bob, itsystem, "bob-account")

    policy = create_policy(graphapi_post, "own-itusers")
    declare_actor(graphapi_post, policy, "all", "")
    declare_rule(
        graphapi_post,
        policy,
        "Mutation",
        "ituser_update",
        filter=ituser_check_spec('{"employee": {"uuids": [token.uuid]}}'),
    )
    set_auth(user_uuid=alice)

    def update(ituser: str) -> object:
        return graphapi_post(
            UPDATE_ITUSER,
            variables={
                "input": {
                    "uuid": ituser,
                    "user_key": "changed",
                    "validity": {"from": "2020-01-01"},
                }
            },
        )

    # Alice may update her own IT-user (linked to her == token.uuid)...
    assert update(alice_ituser).errors is None
    # ...but not Bob's.
    assert update(bob_ituser).errors is not None


TERMINATE_ITUSER = """
  mutation TerminateITUser($input: ITUserTerminateInput!) {
    ituser_terminate(input: $input) {
      uuid
    }
  }
"""


@pytest.mark.integration_test
async def test_pbac_rule_filter_limits_ituser_terminate_by_person(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    # `ituser_terminate` carries the target uuid as `input.uuid`.
    bob = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    carol = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    create_named_person(graphapi_post, bob, "Bob", "Bertelsen")
    create_named_person(graphapi_post, carol, "Carol", "Carlsen")
    itsystem = create_itsystem(graphapi_post)
    bob_ituser = create_ituser_for(graphapi_post, bob, itsystem, "bob-account")
    carol_ituser = create_ituser_for(graphapi_post, carol, itsystem, "carol-account")

    policy = create_policy(graphapi_post, "alice-terminates-bobs-itusers")
    declare_actor(graphapi_post, policy, "role", "editor")
    declare_rule(
        graphapi_post,
        policy,
        "Mutation",
        "ituser_terminate",
        filter=ituser_check_spec('{"employee": {"query": "Bob"}}'),
    )

    set_auth(role="editor")

    def terminate(ituser: str) -> object:
        return graphapi_post(
            TERMINATE_ITUSER,
            variables={"input": {"uuid": ituser, "to": "2021-01-01"}},
        )

    assert terminate(bob_ituser).errors is None
    assert terminate(carol_ituser).errors is not None


@pytest.mark.integration_test
async def test_pbac_rule_filter_limits_ituser_delete_by_person(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    # `ituser_delete` takes the target uuid as a bare `uuid` argument, not an
    # `input`; the gate extracts it just the same.
    bob = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    carol = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    create_named_person(graphapi_post, bob, "Bob", "Bertelsen")
    create_named_person(graphapi_post, carol, "Carol", "Carlsen")
    itsystem = create_itsystem(graphapi_post)
    bob_ituser = create_ituser_for(graphapi_post, bob, itsystem, "bob-account")
    carol_ituser = create_ituser_for(graphapi_post, carol, itsystem, "carol-account")

    policy = create_policy(graphapi_post, "alice-deletes-bobs-itusers")
    declare_actor(graphapi_post, policy, "role", "editor")
    declare_rule(
        graphapi_post,
        policy,
        "Mutation",
        "ituser_delete",
        filter=ituser_check_spec('{"employee": {"query": "Bob"}}'),
    )

    set_auth(role="editor")

    # Carol's does not match -> denied.
    assert graphapi_post(DELETE_ITUSER, variables={"uuid": carol_ituser}).errors
    # Bob's IT-user matches the rule filter -> Alice may delete it.
    assert graphapi_post(DELETE_ITUSER, variables={"uuid": bob_ituser}).errors is None


@pytest.mark.integration_test
async def test_pbac_rule_filter_exists_check_grants(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    # An `EXISTS` check grants when *any* object matches the filter (it does not
    # pin the mutated object). Here an IT-user exists, so the update is granted.
    bob = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    create_named_person(graphapi_post, bob, "Bob", "Bertelsen")
    itsystem = create_itsystem(graphapi_post)
    bob_ituser = create_ituser_for(graphapi_post, bob, itsystem, "bob-account")

    policy = create_policy(graphapi_post, "exists")
    declare_actor(graphapi_post, policy, "all", "")
    declare_rule(
        graphapi_post,
        policy,
        "Mutation",
        "ituser_update",
        filter='{"collection": "ituser", "check": "EXISTS", "filter": {}}',
    )
    set_auth(user_uuid=bob)

    response = graphapi_post(
        UPDATE_ITUSER,
        variables={
            "input": {
                "uuid": bob_ituser,
                "user_key": "changed",
                "validity": {"from": "2020-01-01"},
            }
        },
    )
    assert response.errors is None


@pytest.mark.integration_test
async def test_pbac_denies_when_no_rule_matches(
    graphapi_post: GraphAPIPost, set_auth: SetAuth, empty_db, root_org
) -> None:
    # With every all-actor policy removed and only a policy that grants an
    # unrelated field, a query for which no candidate rule exists is denied.
    for name in ("Legacy", "Administrator", "Reader"):
        uuid = next(
            (p["uuid"] for p in read_policies(graphapi_post) if p["name"] == name),
            None,
        )
        if uuid is not None:
            graphapi_post(DELETE_POLICY, variables={"uuid": uuid})

    policy = create_policy(graphapi_post, "employees-only")
    declare_actor(graphapi_post, policy, "role", "narrow")
    declare_rule(graphapi_post, policy, "Query", "employees")

    set_auth(role="narrow")

    # `employees` is granted, but `policies` has no matching rule -> denied.
    assert graphapi_post(READ_EMPLOYEES).errors is None
    assert graphapi_post(READ_POLICIES).errors is not None


@pytest.mark.integration_test
async def test_policyadmin_actors_and_rules_are_protected(
    graphapi_post: GraphAPIPost, empty_db
) -> None:
    # The bulk actor declare is rejected for the policyadmin policy.
    bulk = graphapi_post(
        DECLARE_ACTORS,
        variables={
            "input": {
                "policy": POLICYADMIN,
                "actors": [{"kind": "role", "value": "mallory"}],
            }
        },
    )
    assert bulk.errors is not None

    # Deleting one of its (hard-bound) actors is rejected.
    read = graphapi_post(READ_POLICY_ACTORS, variables={"uuids": [POLICYADMIN]})
    actors = read.data["policies"]["objects"][0]["actors"]
    del_actor = graphapi_post(DELETE_ACTOR, variables={"uuid": actors[0]["uuid"]})
    assert del_actor.errors is not None

    # Deleting one of its rules is rejected.
    rule_uuid = read_policy_rules(graphapi_post, POLICYADMIN)[0]["uuid"]
    del_rule = graphapi_post(DELETE_RULE, variables={"uuid": rule_uuid})
    assert del_rule.errors is not None
