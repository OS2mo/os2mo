# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the write policy."""

from collections.abc import Callable
from textwrap import dedent
from types import SimpleNamespace
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from graphql import GraphQLError
from more_itertools import one
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy import text

from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.db import AsyncSession
from mora.db import Collection
from mora.db import Policy
from mora.db import PolicyWriteRule
from mora.graphapi.policies import cel2check
from mora.graphapi.policies import write_policy_load_fn
from mora.graphapi.schema import write_policy
from mora.graphapi.version import LATEST_VERSION
from tests.conftest import ALVIDA_UUID
from tests.conftest import BRUCE_UUID
from tests.conftest import DeclarePolicy
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import SetWriteRules
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
async def test_a_check_asks_whether_what_it_names_exists(
    empty_db: AsyncSession,
    create_org_unit: Callable[..., UUID],
    owner_token: Token,
) -> None:
    """A check holds for the unit the arguments name, and for no other."""
    org_unit = create_org_unit("test")
    condition = """
    [{
        "collection": "OrganisationUnit",
        "filter": {"uuids": [args.input.org_unit]}
    }]
    """
    checks = (
        cel2check(
            settings=Settings(),
            graphql_version=LATEST_VERSION,
            condition=condition,
            token=owner_token,
            args={"input": {"org_unit": uuid}},
        )
        for uuid in (org_unit, NOT_FOUND_UUID)
    )

    found = [await empty_db.scalar(select(check)) for check in checks]

    assert found == [True, False]


@pytest.mark.integration_test
async def test_a_check_requires_everything_its_condition_names(
    empty_db: AsyncSession,
    create_org_unit: Callable[..., UUID],
    owner_token: Token,
) -> None:
    """A condition naming two things holds only where both of them exist."""
    org_unit, parent = (create_org_unit(user_key) for user_key in ("ours", "parent"))
    condition = """
    [
        {"collection": "OrganisationUnit", "filter": {"uuids": [args.uuid]}},
        {"collection": "OrganisationUnit", "filter": {"uuids": [args.parent]}}
    ]
    """
    checks = (
        cel2check(
            settings=Settings(),
            graphql_version=LATEST_VERSION,
            condition=condition,
            token=owner_token,
            args={"uuid": org_unit, "parent": parent},
        )
        for parent in (parent, NOT_FOUND_UUID)
    )

    found = [await empty_db.scalar(select(check)) for check in checks]

    assert found == [True, False]


async def test_a_check_requiring_nothing_fails(owner_token: Token) -> None:
    """A condition allowing or denying outright yields true or false, not []."""
    with pytest.raises(ValueError) as raised:
        cel2check(
            settings=Settings(),
            graphql_version=LATEST_VERSION,
            condition="[]",
            token=owner_token,
            args={},
        )

    assert str(raised.value) == (
        "condition '[]' requires nothing, yield true or false instead"
    )


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "condition,decided",
    [
        ("true", True),
        ("false", False),
        ("token.uuid != null", True),
        ("token.uuid == null", False),
        ("args.input.org_unit != null", True),
        ("args.input.person != null", False),
    ],
)
async def test_a_condition_deciding_by_itself_becomes_the_answer_it_gives(
    condition: str, decided: bool, empty_db: AsyncSession, owner_token: Token
) -> None:
    """A condition the token and the arguments settle answers with a plain bool."""
    check = cel2check(
        settings=Settings(),
        graphql_version=LATEST_VERSION,
        condition=condition,
        token=owner_token,
        args={"input": {"org_unit": ALVIDA_UUID, "person": None}},
    )

    assert await empty_db.scalar(select(check)) is decided


async def test_a_check_of_an_unknown_collection_fails(owner_token: Token) -> None:
    """A condition naming a collection no rule can reach is an error."""
    with pytest.raises(ValidationError) as raised:
        cel2check(
            settings=Settings(),
            graphql_version=LATEST_VERSION,
            condition='[{"collection": "Nonsense", "filter": {}}]',
            token=owner_token,
            args={},
        )

    permitted = ", ".join(repr(collection.value) for collection in Collection)
    enum_values = ", ".join(repr(collection) for collection in Collection)
    assert str(raised.value) == dedent(
        f"""\
        1 validation error for ParsingModel[list[mora.graphapi.policies.WriteCondition]]
        __root__ -> 0 -> collection
          value is not a valid enumeration member; permitted: {permitted} (type=type_error.enum; enum_values=[{enum_values}])"""
    )


async def test_a_check_yielding_one_condition_alone_fails(owner_token: Token) -> None:
    """A condition yields a list, one entry per thing the mutator requires."""
    with pytest.raises(ValidationError) as raised:
        cel2check(
            settings=Settings(),
            graphql_version=LATEST_VERSION,
            condition='{"collection": "OrganisationUnit", "filter": {}}',
            token=owner_token,
            args={},
        )

    assert str(raised.value) == dedent(
        """\
        1 validation error for ParsingModel[list[mora.graphapi.policies.WriteCondition]]
        __root__
          value is not a valid list (type=type_error.list)"""
    )


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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_condition_deciding_by_itself_decides_the_mutator(
    set_auth: SetAuth,
    set_write_rules: SetWriteRules,
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    """A condition yielding a bool grants or denies the mutator."""
    mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
        address_create(input: $input) { uuid }
    }
    """
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
    input = {
        "address_type": str(address_type),
        "org_unit": str(org_unit),
        "value": "unit@example.org",
        "validity": {"from": "2000-01-01"},
    }
    await set_write_rules(
        role="unit_owner",
        mutator="address_create",
        condition="args.input.org_unit != null",
    )
    set_auth({"reader", "unit_owner"}, BRUCE_UUID)

    assert_granted(graphapi_post(mutation, {"input": input}))
    assert_denied(
        graphapi_post(
            mutation,
            {"input": {**input, "org_unit": None, "person": str(BRUCE_UUID)}},
        )
    )
