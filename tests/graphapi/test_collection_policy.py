# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the collection policy."""

from collections.abc import Callable
from types import SimpleNamespace
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy import Boolean
from sqlalchemy import literal
from sqlalchemy import true

from mora.db import AsyncSession
from mora.db import OrganisationFunktionRegistrering
from mora.graphapi.policies import AccessKey
from mora.graphapi.policies import Rule
from mora.graphapi.policies import access_load_fn
from mora.graphapi.schema import collection_policy
from tests.conftest import SetRules
from tests.conftest import token_getter_of


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
    set_rules: SetRules,
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
    set_rules(
        [
            Rule(
                role="reader",
                collection="Address",
                condition=true(),
                fields=frozenset({"user_key"}),
            ),
            Rule(
                role="reader",
                collection="Address",
                condition=OrganisationFunktionRegistrering.organisationfunktion_id
                == matched,
                fields=frozenset({"value"}),
            ),
        ]
    )

    allowed = await access_load_fn(
        empty_db,
        token_getter_of("reader"),
        [
            AccessKey("Address", matched, "value"),
            AccessKey("Address", matched, "user_key"),
            AccessKey("Address", matched, "name"),
            AccessKey("Address", unmatched, "value"),
            AccessKey("Address", unmatched, "user_key"),
            AccessKey("Address", unmatched, "name"),
        ],
    )

    assert allowed == [True, True, False, False, True, False]


@pytest.mark.integration_test
async def test_a_rule_of_a_role_the_caller_lacks_grants_nothing(
    empty_db: AsyncSession,
    set_rules: SetRules,
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """The rules that decide an access are those of the caller's own roles."""
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
    set_rules(
        [
            Rule(
                role="reader",
                collection="Address",
                condition=true(),
                fields=frozenset({"value"}),
            )
        ]
    )

    allowed = await access_load_fn(
        empty_db, token_getter_of("owner"), [AccessKey("Address", address, "value")]
    )

    assert allowed == [False]


@pytest.mark.integration_test
async def test_a_batch_spans_collections_and_grants_only_where_a_rule_names_one(
    empty_db: AsyncSession,
    set_rules: SetRules,
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
    set_rules(
        [
            Rule(
                role="reader",
                collection="Address",
                condition=true(),
                fields=frozenset({"value"}),
            )
        ]
    )

    allowed = await access_load_fn(
        empty_db,
        token_getter_of("reader"),
        [
            AccessKey("Address", address, "value"),
            AccessKey("Employee", uuid4(), "cpr_number"),
        ],
    )

    assert allowed == [True, False]


@pytest.mark.integration_test
async def test_a_condition_unknown_of_an_object_grants_nothing_on_it(
    empty_db: AsyncSession,
    set_rules: SetRules,
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
    set_rules(
        [
            Rule(
                role="reader",
                collection="Address",
                condition=literal(None, Boolean),
                fields=frozenset({"value"}),
            ),
            Rule(
                role="reader",
                collection="Address",
                condition=OrganisationFunktionRegistrering.organisationfunktion_id
                == matched,
                fields=frozenset({"value"}),
            ),
        ]
    )

    allowed = await access_load_fn(
        empty_db,
        token_getter_of("reader"),
        [
            AccessKey("Address", matched, "value"),
            AccessKey("Address", unmatched, "value"),
        ],
    )

    assert allowed == [True, False]
