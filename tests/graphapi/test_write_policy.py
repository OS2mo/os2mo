# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the write policy."""

from collections.abc import Callable
from types import SimpleNamespace
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from graphql import GraphQLError
from more_itertools import one
from sqlalchemy import select
from sqlalchemy import text

from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.db import AsyncSession
from mora.db import Policy
from mora.db import PolicyWriteRule
from mora.graphapi.policies import cel2check
from mora.graphapi.policies import write_policy_load_fn
from mora.graphapi.schema import write_policy
from mora.graphapi.version import LATEST_VERSION
from tests.conftest import BRUCE_UUID
from tests.conftest import DeclarePolicy
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied
from tests.conftest import assert_granted
from tests.conftest import token_getter_of

NOT_FOUND_UUID = UUID("c6720bc8-6e37-4a59-8876-950b2117df22")


@pytest.fixture
def owner_token() -> Token:
    return Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"owner"}))


@pytest.fixture
def address_input(
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> dict[str, Any]:
    """The input creating an email address in the unit `ours`."""
    org_unit = create_org_unit("ours")
    facet = create_facet(
        {"user_key": "org_unit_address_type", "validity": {"from": "2000-01-01"}}
    )
    address_type = create_class(
        {
            "facet_uuid": str(facet),
            "user_key": "email",
            "name": "Email",
            "scope": "EMAIL",
            "validity": {"from": "2000-01-01"},
        }
    )
    return {
        "address_type": str(address_type),
        "org_unit": str(org_unit),
        "value": "unit@example.org",
        "validity": {"from": "2000-01-01"},
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_check_requires_everything_its_condition_names(
    set_auth: SetAuth,
    declare_policy: DeclarePolicy,
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
) -> None:
    """A condition naming two things holds only where both of them exist."""
    mutation = """
    mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
        org_unit_update(input: $input) { uuid }
    }
    """
    org_unit, parent = (create_org_unit(user_key) for user_key in ("ours", "parent"))
    declare_policy(
        str(uuid4()),
        {
            "name": "Unit Owner",
            "role": "unit_owner",
            "write_rules": [
                {
                    "mutator": "org_unit_update",
                    "condition": """
                    [
                        {
                            "collection": "OrganisationUnit",
                            "filter": {"uuids": [args.input.uuid]}
                        },
                        {
                            "collection": "OrganisationUnit",
                            "filter": {"uuids": [args.input.parent]}
                        }
                    ]
                    """,
                    "graphql_version": "VERSION_30",
                }
            ],
        },
    )
    set_auth({"reader", "unit_owner"}, BRUCE_UUID)

    input = {"uuid": str(org_unit), "validity": {"from": "2000-01-01"}}
    assert_granted(graphapi_post(mutation, {"input": {**input, "parent": str(parent)}}))
    assert_denied(
        graphapi_post(mutation, {"input": {**input, "parent": str(NOT_FOUND_UUID)}})
    )


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "condition,error",
    [
        # Allowing or denying outright is what true and false are for
        ("[]", "condition '[]' requires nothing, yield true or false instead"),
        # A collection no rule can reach
        (
            '[{"collection": "Nonsense", "filter": {}}]',
            "__root__ -> 0 -> collection\n  value is not a valid enumeration member",
        ),
        # A condition yields a list, one entry per thing the mutator requires
        (
            '{"collection": "OrganisationUnit", "filter": {}}',
            "__root__\n  value is not a valid list",
        ),
    ],
)
@pytest.mark.usefixtures("empty_db")
async def test_a_condition_yielding_no_check_fails_the_mutator(
    condition: str,
    error: str,
    set_auth: SetAuth,
    declare_policy: DeclarePolicy,
    graphapi_post: GraphAPIPost,
    address_input: dict[str, Any],
) -> None:
    """A condition yielding what cannot be checked fails the mutator, saying why."""
    mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
        address_create(input: $input) { uuid }
    }
    """
    declare_policy(
        str(uuid4()),
        {
            "name": "Unit Owner",
            "role": "unit_owner",
            "write_rules": [
                {
                    "mutator": "address_create",
                    "condition": condition,
                    "graphql_version": "VERSION_30",
                }
            ],
        },
    )
    set_auth({"reader", "unit_owner"}, BRUCE_UUID)

    response = graphapi_post(mutation, {"input": address_input})

    assert response.errors is not None
    assert error in one(response.errors)["message"]


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "condition,assert_decided",
    [
        ("true", assert_granted),
        ("false", assert_denied),
        ("token.uuid != null", assert_granted),
        ("token.uuid == null", assert_denied),
        ("args.input.org_unit != null", assert_granted),
        ("args.input.person != null", assert_denied),
    ],
)
@pytest.mark.usefixtures("empty_db")
async def test_a_condition_deciding_by_itself_becomes_the_answer_it_gives(
    condition: str,
    assert_decided: Callable[[GQLResponse], None],
    set_auth: SetAuth,
    declare_policy: DeclarePolicy,
    graphapi_post: GraphAPIPost,
    address_input: dict[str, Any],
) -> None:
    """A condition the token and the arguments settle grants or denies outright."""
    mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
        address_create(input: $input) { uuid }
    }
    """
    declare_policy(
        str(uuid4()),
        {
            "name": "Unit Owner",
            "role": "unit_owner",
            "write_rules": [
                {
                    "mutator": "address_create",
                    "condition": condition,
                    "graphql_version": "VERSION_30",
                }
            ],
        },
    )
    set_auth({"reader", "unit_owner"}, BRUCE_UUID)

    assert_decided(graphapi_post(mutation, {"input": address_input}))


async def test_a_check_yielding_what_the_filter_rejects_fails(
    owner_token: Token,
) -> None:
    """The filter a condition yields is coerced into its collection's filter."""
    with pytest.raises(GraphQLError) as raised:
        cel2check(
            settings=Settings(),
            graphql_version=LATEST_VERSION,
            condition='[{"collection": "OrganisationUnit", "filter": {"uuids": ["not-a-uuid"]}}]',
            token=owner_token,
            args={},
        )

    assert str(raised.value) == (
        """Invalid value 'not-a-uuid' at 'value.uuids[0]': Value cannot represent a UUID: "not-a-uuid". badly formed hexadecimal UUID string"""
    )


@pytest.mark.integration_test
async def test_a_rule_keeps_its_mutator_condition_and_version(
    empty_db: AsyncSession,
) -> None:
    """A rule reads back as it was written, the version as the enum it went in as."""
    condition = """
    [{
        "collection": "OrganisationUnit",
        "filter": {"uuids": [args.input.org_unit]}
    }]
    """
    empty_db.add(
        Policy(
            name="Unit Owner",
            description="Allows unit owners to create addresses in their own unit",
            active=True,
            role="unit_owner",
            write_rules=[
                PolicyWriteRule(
                    mutator="address_create",
                    condition=condition,
                    graphql_version=LATEST_VERSION,
                )
            ],
        )
    )
    await empty_db.flush()
    # Read it back rather than out of the identity map
    empty_db.expunge_all()

    rule = one(
        (
            await empty_db.scalars(
                select(PolicyWriteRule).join(Policy).where(Policy.role == "unit_owner")
            )
        ).all()
    )
    assert rule.mutator == "address_create"
    assert rule.condition == condition
    assert rule.graphql_version is LATEST_VERSION
    assert (
        await empty_db.scalar(
            text("SELECT graphql_version FROM policy_write_rule WHERE pk = :pk"),
            {"pk": rule.pk},
        )
        == LATEST_VERSION.value
    )


@pytest.mark.integration_test
async def test_the_write_rules_of_the_callers_policies_are_loaded(
    empty_db: AsyncSession,
) -> None:
    """The caller gets the rules of the policies of the roles it carries."""
    condition = """
    [{
        "collection": "OrganisationUnit",
        "filter": {"uuids": [args.input.org_unit]}
    }]
    """
    empty_db.add_all(
        [
            Policy(
                name="Unit Owner",
                description="Allows unit owners to write in their own unit",
                active=True,
                role="unit_owner",
                write_rules=[
                    PolicyWriteRule(
                        mutator="address_create",
                        condition=condition,
                        graphql_version=LATEST_VERSION,
                    ),
                    PolicyWriteRule(
                        mutator="ituser_create",
                        condition=condition,
                        graphql_version=LATEST_VERSION,
                    ),
                ],
            ),
            Policy(
                name="Class Writer",
                description="Allows class writers to create classes",
                active=True,
                role="class_writer",
                write_rules=[
                    PolicyWriteRule(
                        mutator="class_create",
                        condition="true",
                        graphql_version=LATEST_VERSION,
                    )
                ],
            ),
        ]
    )
    await empty_db.flush()

    rules = one(
        await write_policy_load_fn(
            session=empty_db,
            settings=Settings(),
            get_token=token_getter_of("unit_owner"),
            keys=[0],
        )
    )

    assert {rule.mutator for rule in rules} == {"address_create", "ituser_create"}
    assert {rule.role for rule in rules} == {"unit_owner"}


@pytest.mark.integration_test
async def test_a_policy_switched_off_grants_no_mutator(empty_db: AsyncSession) -> None:
    """An inactive policy hands its write rules to nobody."""
    empty_db.add(
        Policy(
            name="Unit Owner",
            description="Allows unit owners to write in their own unit",
            active=False,
            role="unit_owner",
            write_rules=[
                PolicyWriteRule(
                    mutator="address_create",
                    condition="""
                    [{
                        "collection": "OrganisationUnit",
                        "filter": {"uuids": [args.input.org_unit]}
                    }]
                    """,
                    graphql_version=LATEST_VERSION,
                )
            ],
        )
    )
    await empty_db.flush()

    assert await write_policy_load_fn(
        session=empty_db,
        settings=Settings(),
        get_token=token_getter_of("unit_owner"),
        keys=[0],
    ) == [[]]


async def test_a_field_which_is_no_mutator_is_rejected_without_asking() -> None:
    """The policy answers at once, rather than handing back a coroutine to await."""
    info = SimpleNamespace(parent_type=SimpleNamespace(name="AddressResponse"))

    assert write_policy(None, info, {}) is False


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_mutator_is_granted_where_its_rule_finds_what_it_names(
    set_auth: SetAuth,
    declare_policy: DeclarePolicy,
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    address_input: dict[str, Any],
) -> None:
    """The rule grants the mutator on the unit it names, and on no other."""
    mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
        address_create(input: $input) { uuid }
    }
    """
    theirs = create_org_unit("theirs")
    declare_policy(
        str(uuid4()),
        {
            "name": "Unit Owner",
            "role": "unit_owner",
            "write_rules": [
                {
                    "mutator": "address_create",
                    "condition": """
                    [{
                        "collection": "OrganisationUnit",
                        "filter": {"uuids": [args.input.org_unit], "user_keys": ["ours"]}
                    }]
                    """,
                    "graphql_version": "VERSION_30",
                }
            ],
        },
    )
    set_auth({"reader", "unit_owner"}, BRUCE_UUID)

    assert_granted(graphapi_post(mutation, {"input": address_input}))
    assert_denied(
        graphapi_post(mutation, {"input": {**address_input, "org_unit": str(theirs)}})
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_mutator_no_rule_names_is_denied(
    set_auth: SetAuth,
    declare_policy: DeclarePolicy,
    graphapi_post: GraphAPIPost,
    address_input: dict[str, Any],
) -> None:
    """A rule grants the mutator it binds to, and nothing else."""
    mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
        address_create(input: $input) { uuid }
    }
    """
    declare_policy(
        str(uuid4()),
        {
            "name": "Unit Owner",
            "role": "unit_owner",
            "write_rules": [
                {
                    "mutator": "ituser_create",
                    "condition": """
                    [{
                        "collection": "OrganisationUnit",
                        "filter": {"uuids": [args.input.org_unit]}
                    }]
                    """,
                    "graphql_version": "VERSION_30",
                }
            ],
        },
    )
    set_auth({"reader", "unit_owner"}, BRUCE_UUID)

    assert_denied(graphapi_post(mutation, {"input": address_input}))
