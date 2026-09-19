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
from more_itertools import one
from pydantic import ValidationError
from sqlalchemy import Boolean
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import true
from strawberry.dataloader import DataLoader

from mora.auth.keycloak.models import RealmAccess
from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.db import AsyncSession
from mora.db import Collection
from mora.db import OrganisationFunktionRegistrering
from mora.db import Policy
from mora.db import PolicyReadRule
from mora.db import PolicyReadRuleField
from mora.graphapi.policies import AccessKey
from mora.graphapi.policies import Rule
from mora.graphapi.policies import access_load_fn
from mora.graphapi.policies import cel2predicate
from mora.graphapi.policies import policy_load_fn
from mora.graphapi.schema import collection_policy
from mora.graphapi.version import LATEST_VERSION
from tests.conftest import BRUCE_UUID
from tests.conftest import token_getter_of


async def fake_policy_loader(rules: list[Rule], keys: list[int]) -> list[list[Rule]]:
    """Stand in for `policy_load_fn`, for rules whose condition no row can hold."""
    return [rules for _ in keys]


async def test_a_type_which_is_no_collection_is_rejected_without_asking() -> None:
    """The policy answers at once, rather than handing back a future to await.

    A type with no objects of its own, the paged wrapper here, has nothing a
    rule could reach, and only `info.parent_type.name` is read to tell.
    """
    info = SimpleNamespace(parent_type=SimpleNamespace(name="AddressPaged"))

    assert collection_policy(None, info, {}) is False


@pytest.mark.integration_test
async def test_an_object_gets_the_fields_of_every_rule_matching_it(
    empty_db: AsyncSession,
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """An object gets the fields of every rule matching it, and no others.

    A field no rule names is denied of both addresses, and the field of the
    rule matching only one of them is denied of the other.
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
    rules = [
        Rule(
            role="reader",
            collection=Collection.Address,
            condition=true(),
            fields=frozenset({"user_key"}),
        ),
        Rule(
            role="reader",
            collection=Collection.Address,
            condition=OrganisationFunktionRegistrering.organisationfunktion_id
            == matched,
            fields=frozenset({"value"}),
        ),
    ]

    allowed = await access_load_fn(
        empty_db,
        DataLoader(load_fn=partial(fake_policy_loader, rules)),
        [
            AccessKey(Collection.Address, matched, "value"),
            AccessKey(Collection.Address, matched, "user_key"),
            AccessKey(Collection.Address, matched, "name"),
            AccessKey(Collection.Address, unmatched, "value"),
            AccessKey(Collection.Address, unmatched, "user_key"),
            AccessKey(Collection.Address, unmatched, "name"),
        ],
    )

    assert allowed == [True, True, False, False, True, False]


@pytest.mark.integration_test
async def test_a_batch_spans_collections_and_grants_only_where_a_rule_names_one(
    empty_db: AsyncSession,
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """Accesses to a collection no rule names are denied beside those granted."""
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
    address = create_address(
        {
            "address_type": str(address_type),
            "org_unit": str(org_unit),
            "value": "first@example.org",
            "validity": {"from": "2000-01-01"},
        }
    )
    rules = [
        Rule(
            role="reader",
            collection=Collection.Address,
            condition=true(),
            fields=frozenset({"value"}),
        )
    ]

    allowed = await access_load_fn(
        empty_db,
        DataLoader(load_fn=partial(fake_policy_loader, rules)),
        [
            AccessKey(Collection.Address, address, "value"),
            AccessKey(Collection.Employee, uuid4(), "cpr_number"),
        ],
    )

    assert allowed == [True, False]


@pytest.mark.integration_test
async def test_a_condition_unknown_of_an_object_grants_nothing_on_it(
    empty_db: AsyncSession,
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """A rule grants its fields where its condition is true, not where it is unknown.

    SQL is three-valued: a condition touching a NULL is NULL of an object, and
    NULL is not a grant. Alone, such a rule denies; beside a rule that does match
    the object, the disjunction of the two is true and the fields are granted.
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
    rules = [
        Rule(
            role="reader",
            collection=Collection.Address,
            condition=literal(None, Boolean),
            fields=frozenset({"value"}),
        ),
        Rule(
            role="reader",
            collection=Collection.Address,
            condition=OrganisationFunktionRegistrering.organisationfunktion_id
            == matched,
            fields=frozenset({"value"}),
        ),
    ]

    allowed = await access_load_fn(
        empty_db,
        DataLoader(load_fn=partial(fake_policy_loader, rules)),
        [
            AccessKey(Collection.Address, matched, "value"),
            AccessKey(Collection.Address, unmatched, "value"),
        ],
    )

    assert allowed == [True, False]


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "condition,reached",
    [
        # A rule without a condition reaches every object of its collection
        ("", {"mine@example.org", "theirs@example.org", "11111111"}),
        (
            '{"address_type": {"scope": ["EMAIL"]}}',
            {"mine@example.org", "theirs@example.org"},
        ),
        ('{"employee": {"uuids": [token.uuid]}}', {"mine@example.org", "11111111"}),
        (
            '{"employee": {"uuids": [token.uuid]}, "address_type": {"scope": ["EMAIL"]}}',
            {"mine@example.org"},
        ),
    ],
)
async def test_a_condition_becomes_the_clause_its_filter_names(
    condition: str,
    reached: set[str],
    empty_db: AsyncSession,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """A condition reaches the objects its filter names, evaluated on the token."""
    token = await token_getter_of("reader")()
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
    clause = cel2predicate(
        Settings(), Collection.Address, LATEST_VERSION, condition, token
    )

    rows = await empty_db.scalars(
        select(OrganisationFunktionRegistrering.uuid).where(clause)
    )

    assert set(rows) == {addresses[value] for value in reached}


async def test_a_condition_yielding_what_the_filter_rejects_fails() -> None:
    """The map a condition yields is instantiated against the collection's filter."""
    token = Token(azp="mo", uuid=BRUCE_UUID, realm_access=RealmAccess(roles={"reader"}))

    with pytest.raises(ValidationError) as raised:
        cel2predicate(
            Settings(),
            Collection.Address,
            LATEST_VERSION,
            '{"uuids": ["not-a-uuid"]}',
            token,
        )

    assert "value is not a valid uuid" in str(raised.value)


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
                        condition="",
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
                        condition="",
                        graphql_version=LATEST_VERSION,
                        fields=[PolicyReadRuleField(field="name")],
                    )
                ],
            ),
        ]
    )
    await empty_db.flush()

    rules = one(await policy_load_fn(empty_db, token_getter_of("auditor"), [0]))
    rule = one(rules)

    assert rule.role == "auditor"
    assert rule.collection == Collection.Address
    assert rule.fields == frozenset({"uuid", "value"})
    # A row carries no condition, so its rule reaches every object
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
                    condition="",
                    graphql_version=LATEST_VERSION,
                    fields=[PolicyReadRuleField(field="uuid")],
                )
            ],
        )
    )
    await empty_db.flush()

    assert await policy_load_fn(empty_db, token_getter_of("auditor"), [0]) == [[]]
