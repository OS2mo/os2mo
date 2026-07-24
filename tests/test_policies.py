# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the policy-based access control (PBAC) engine.

The policies are database-managed; until the policy CRUD API is introduced,
the tests declare them directly through the ORM.
"""

from uuid import UUID

import pytest
from more_itertools import first
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
