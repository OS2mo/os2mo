# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the collection policy."""

from collections.abc import Callable
from functools import partial
from types import SimpleNamespace
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from graphql import GraphQLError
from more_itertools import one
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import true
from strawberry.dataloader import DataLoader

from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.db import AsyncSession
from mora.db import Collection
from mora.db import Policy
from mora.db import PolicyReadRule
from mora.db import PolicyReadRuleField
from mora.graphapi.graphql_utils import AccessKey
from mora.graphapi.policies import Rule
from mora.graphapi.policies import access_load_fn
from mora.graphapi.policies import cel2predicate
from mora.graphapi.policies import policy_load_fn
from mora.graphapi.schema import collection_policy
from mora.graphapi.version import LATEST_VERSION
from tests.conftest import BRUCE_UUID
from tests.conftest import DENIED
from tests.conftest import DeclarePolicy
from tests.conftest import GraphAPIPost
from tests.conftest import MayRead
from tests.conftest import SetAuth
from tests.conftest import token_getter_of


async def test_a_type_which_is_no_collection_is_rejected_without_asking() -> None:
    """The policy answers at once, rather than handing back a future to await.

    A type with no objects of its own, the paged wrapper here, has nothing a
    rule could reach, and only `info.parent_type.name` is read to tell.
    """
    info = SimpleNamespace(parent_type=SimpleNamespace(name="AddressPaged"))

    assert collection_policy(None, info, {}) is False


@pytest.mark.integration_test
@pytest.mark.usefixtures("no_seeded_policies")
async def test_an_object_gets_the_fields_of_every_rule_matching_it(
    set_auth: SetAuth,
    declare_policy: DeclarePolicy,
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """An object gets the fields of every rule matching it, and no others.

    A field no rule names is denied of both addresses, and the field of the
    rule matching only one of them is denied of the other.
    """
    # Each field is read on a `current` of its own, as a denied field nulls the
    # object holding it, hiding the denials of the fields beside it
    query = """
        query ReadAddresses {
            addresses {
                objects {
                    uuid
                    value: current { value }
                    user_key: current { user_key }
                    name: current { name }
                }
            }
        }
    """
    org_unit = create_org_unit("test")
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
    matched, unmatched = (
        create_address(
            {
                "address_type": str(address_type),
                "org_unit": str(org_unit),
                "value": value,
                "validity": {"from": "2000-01-01"},
            }
        )
        for value in ("first@example.org", "second@example.org")
    )
    declare_policy(
        str(uuid4()),
        {
            "name": "Address Auditor",
            "role": "address_auditor",
            "read_rules": [
                {
                    "collection": "Address",
                    "fields": ["user_key"],
                    "graphql_version": "VERSION_30",
                },
                {
                    "collection": "Address",
                    "fields": ["value"],
                    "condition": f'{{"uuids": ["{matched}"]}}',
                    "graphql_version": "VERSION_30",
                },
            ],
        },
    )
    set_auth({"reader", "address_auditor"}, BRUCE_UUID)

    response = graphapi_post(query)

    assert response.data is not None
    assert response.errors is not None
    objects = response.data["addresses"]["objects"]
    assert {obj["uuid"] for obj in objects} == {str(matched), str(unmatched)}
    assert {error["message"] for error in response.errors} == {DENIED}
    denied = {
        (objects[index]["uuid"], field)
        for _, _, index, field, _ in (error["path"] for error in response.errors)
    }
    assert denied == {
        (str(matched), "name"),
        (str(unmatched), "value"),
        (str(unmatched), "name"),
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("no_seeded_policies")
async def test_a_condition_unknown_of_an_object_grants_nothing_on_it(
    set_auth: SetAuth,
    declare_policy: DeclarePolicy,
    graphapi_post: GraphAPIPost,
    may_read: MayRead,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_org_unit: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    """A rule grants its fields where its condition is true, not where it is unknown.

    SQL is three-valued: a condition touching a NULL is NULL of an object, and
    NULL is not a grant. Alone, such a rule denies; beside a rule that does match
    the object, the disjunction of the two is true and the fields are granted.

    Clearing the engagements of an IT user relates it to an engagement of no uuid,
    so whether an IT user names an engagement is NULL of every engagement.
    """
    mutation = """
    mutation ClearEngagements($input: ITUserUpdateInput!) {
        ituser_update(input: $input) { uuid }
    }
    """
    person = create_person(None)
    org_unit = create_org_unit("test")
    matched, unmatched = (
        create_engagement(
            {
                "user_key": user_key,
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "org_unit": str(org_unit),
                "person": str(person),
                "validity": {"from": "2000-01-01"},
            }
        )
        for user_key in ("matched", "unmatched")
    )
    itsystem = create_itsystem(
        {"user_key": "AD", "name": "AD", "validity": {"from": "2000-01-01"}}
    )
    ituser = create_ituser(
        {
            "user_key": "cleared",
            "itsystem": str(itsystem),
            "person": str(person),
            "validity": {"from": "2000-01-01"},
        }
    )
    response = graphapi_post(
        mutation,
        {
            "input": {
                "uuid": str(ituser),
                "engagements": [],
                "validity": {"from": "2010-01-01"},
            }
        },
    )
    assert response.errors is None
    declare_policy(
        str(uuid4()),
        {
            "name": "Engagement Auditor",
            "role": "engagement_auditor",
            "read_rules": [
                {
                    "collection": "Engagement",
                    "fields": ["user_key"],
                    "condition": '{"ituser": {}}',
                    "graphql_version": "VERSION_30",
                },
                {
                    "collection": "Engagement",
                    "fields": ["user_key"],
                    "condition": f'{{"uuids": ["{matched}"]}}',
                    "graphql_version": "VERSION_30",
                },
            ],
        },
    )
    set_auth({"reader", "engagement_auditor"}, BRUCE_UUID)

    allowed = [
        may_read("engagements", uuid, "user_key") for uuid in (matched, unmatched)
    ]

    assert allowed == [True, False]


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "condition,reached",
    [
        # A rule yielding true reaches every object of its collection, false none
        ("true", {"mine@example.org", "theirs@example.org", "11111111"}),
        ("false", set()),
        (
            '{"address_type": {"scope": ["EMAIL"]}}',
            {"mine@example.org", "theirs@example.org"},
        ),
        ('{"employee": {"uuids": [token.uuid]}}', {"mine@example.org", "11111111"}),
        (
            '{"employee": {"uuids": [token.uuid]}, "address_type": {"scope": ["EMAIL"]}}',
            {"mine@example.org"},
        ),
        # A filter naming no filter of its own narrows by nothing
        (
            '{"employee": null}',
            {"mine@example.org", "theirs@example.org", "11111111"},
        ),
    ],
)
@pytest.mark.usefixtures("no_seeded_policies")
async def test_a_condition_becomes_the_clause_its_filter_names(
    condition: str,
    reached: set[str],
    set_auth: SetAuth,
    declare_policy: DeclarePolicy,
    may_read: MayRead,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """A condition reaches the objects its filter names, evaluated on the token."""
    caller = create_person(
        {"given_name": "Bruce", "surname": "Lee", "uuid": str(BRUCE_UUID)}
    )
    other = create_person(None)
    facet = create_facet(
        {"user_key": "employee_address_type", "validity": {"from": "2000-01-01"}}
    )
    email, phone = (
        create_class(
            {
                "facet_uuid": str(facet),
                "user_key": user_key,
                "name": user_key.title(),
                "scope": scope,
                "validity": {"from": "2000-01-01"},
            }
        )
        for user_key, scope in (("email", "EMAIL"), ("phone", "PHONE"))
    )
    addresses = {
        value: create_address(
            {
                "address_type": str(address_type),
                "person": str(person),
                "value": value,
                "validity": {"from": "2000-01-01"},
            }
        )
        for person, address_type, value in (
            (caller, email, "mine@example.org"),
            (other, email, "theirs@example.org"),
            (caller, phone, "11111111"),
        )
    }
    declare_policy(
        str(uuid4()),
        {
            "name": "Reader",
            "role": "reader",
            "read_rules": [
                {
                    "collection": "Address",
                    "fields": ["value"],
                    "condition": condition,
                    "graphql_version": "VERSION_30",
                }
            ],
        },
    )
    set_auth("reader", BRUCE_UUID)

    readable = {
        value
        for value, uuid in addresses.items()
        if may_read("addresses", uuid, "value")
    }

    assert readable == reached


async def test_a_condition_yielding_what_the_filter_rejects_fails() -> None:
    """The map a condition yields is coerced into the collection's filter."""
    token = Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"reader"}))

    with pytest.raises(GraphQLError) as raised:
        cel2predicate(
            Settings(),
            Collection.Address,
            LATEST_VERSION,
            '{"uuids": ["not-a-uuid"]}',
            token,
        )

    assert str(raised.value) == (
        "Invalid value 'not-a-uuid' at 'value.uuids[0]': "
        'Value cannot represent a UUID: "not-a-uuid". '
        "badly formed hexadecimal UUID string"
    )


@pytest.mark.integration_test
async def test_a_condition_narrows_a_rule_to_the_objects_it_names(
    empty_db: AsyncSession,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """A read rule grants fields access only on the objects its condition names."""
    caller = create_person(
        {"given_name": "Bruce", "surname": "Lee", "uuid": str(BRUCE_UUID)}
    )
    other = create_person(None)
    facet = create_facet(
        {"user_key": "employee_address_type", "validity": {"from": "2000-01-01"}}
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
    mine, theirs = (
        create_address(
            {
                "address_type": str(address_type),
                "person": str(person),
                "value": value,
                "validity": {"from": "2000-01-01"},
            }
        )
        for person, value in (
            (caller, "first@example.org"),
            (other, "second@example.org"),
        )
    )
    empty_db.add(
        Policy(
            name="Self Auditor",
            description="Allows self auditors to read the addresses of their own person",
            active=True,
            role="self_auditor",
            read_rules=[
                PolicyReadRule(
                    collection=Collection.Address,
                    graphql_version=LATEST_VERSION,
                    condition='{"employee": {"uuids": [token.uuid]}}',
                    fields=[PolicyReadRuleField(field="value")],
                )
            ],
        )
    )
    await empty_db.flush()
    policy_loader: DataLoader[int, list[Rule]] = DataLoader(
        load_fn=partial(
            policy_load_fn, empty_db, Settings(), token_getter_of("self_auditor")
        )
    )

    allowed = await access_load_fn(
        empty_db,
        policy_loader,
        [
            AccessKey(Collection.Address, mine, "value"),
            AccessKey(Collection.Address, theirs, "value"),
        ],
    )

    assert allowed == [True, False]


@pytest.mark.integration_test
async def test_a_rule_keeps_its_condition_and_version(empty_db: AsyncSession) -> None:
    """A rule reads back as it was written, the version as the enum it went in as."""
    empty_db.add(
        Policy(
            name="Email Auditor",
            description="Allows auditors to read all email addresses",
            active=True,
            role="email_auditor",
            read_rules=[
                PolicyReadRule(
                    collection=Collection.Address,
                    condition='{"address_type": {"scope": ["EMAIL"]}}',
                    graphql_version=LATEST_VERSION,
                    fields=[PolicyReadRuleField(field="value")],
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
                select(PolicyReadRule)
                .join(Policy)
                .where(Policy.role == "email_auditor")
            )
        ).all()
    )
    assert rule.condition == '{"address_type": {"scope": ["EMAIL"]}}'
    assert rule.graphql_version is LATEST_VERSION
    assert (
        await empty_db.scalar(
            text("SELECT graphql_version FROM policy_read_rule WHERE pk = :pk"),
            {"pk": rule.pk},
        )
        == LATEST_VERSION.value
    )


@pytest.mark.integration_test
async def test_the_rules_of_the_callers_policies_are_loaded(
    empty_db: AsyncSession,
) -> None:
    """Only the rules of the caller's own policies are loaded.

    The roles here are ones the migrated policies do not already name.
    """
    empty_db.add_all(
        [
            Policy(
                name="auditor",
                description="Reads the uuid and the value of addresses",
                active=True,
                role="auditor",
                read_rules=[
                    PolicyReadRule(
                        collection=Collection.Address,
                        condition="true",
                        graphql_version=LATEST_VERSION,
                        fields=[
                            PolicyReadRuleField(field="uuid"),
                            PolicyReadRuleField(field="value"),
                        ],
                    )
                ],
            ),
            Policy(
                name="owner",
                description="Reads the name of employees",
                active=True,
                role="owner",
                read_rules=[
                    PolicyReadRule(
                        collection=Collection.Employee,
                        condition="true",
                        graphql_version=LATEST_VERSION,
                        fields=[PolicyReadRuleField(field="name")],
                    )
                ],
            ),
        ]
    )
    await empty_db.flush()

    rules = one(
        await policy_load_fn(empty_db, Settings(), token_getter_of("auditor"), [0])
    )
    rule = one(rules)

    assert rule.role == "auditor"
    assert rule.collection == Collection.Address
    assert rule.fields == frozenset({"uuid", "value"})
    # The row's condition is true, so its rule reaches every object
    assert rule.condition.compare(true())


@pytest.mark.integration_test
async def test_a_policy_switched_off_grants_nothing(empty_db: AsyncSession) -> None:
    """The rules of an inactive policy are left where they are, unread."""
    empty_db.add(
        Policy(
            name="auditor",
            description="Reads the uuid of addresses, were it active",
            role="auditor",
            active=False,
            read_rules=[
                PolicyReadRule(
                    collection=Collection.Address,
                    condition="true",
                    graphql_version=LATEST_VERSION,
                    fields=[PolicyReadRuleField(field="uuid")],
                )
            ],
        )
    )
    await empty_db.flush()

    assert await policy_load_fn(
        empty_db, Settings(), token_getter_of("auditor"), [0]
    ) == [[]]
