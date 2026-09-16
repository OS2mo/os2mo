# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The fields of an address are guarded by read policies rather than by role.

Wherever an address is reached, what the caller may read of it is decided per
address: the fields granted by the rules of their roles matching it (see
`mora.graphapi.policies`).
"""

from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy import Boolean
from sqlalchemy import delete
from sqlalchemy import literal
from sqlalchemy import true
from sqlalchemy import update

from mora.db import OrganisationFunktionRegistrering
from mora.db import Policy
from mora.db import PolicyReader
from mora.db import PolicySelector
from mora.db import PolicySelectorKind
from mora.graphapi import schema
from mora.graphapi.policy import ReadRule
from mora.graphapi.policy import Rules
from tests.conftest import AnotherTransaction
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

SetPolicy = Callable[[list[ReadRule]], None]

DENIED = "No policy approved the access"


@pytest.fixture
def set_policy(monkeypatch: pytest.MonkeyPatch) -> SetPolicy:
    """Install the read rules for the duration of a test.

    A condition is a SQL expression, which a policy writes as a CEL filter over
    its collection; a test states the SQL itself, in place of what the policies
    in the database grant.
    """

    def inner(rules: list[ReadRule]) -> None:
        async def loaded(*args: Any) -> Rules:
            return Rules(read=rules, mutators=frozenset())

        monkeypatch.setattr(schema, "load_rules", loaded)

    return inner


def _failures(response: Any) -> set[tuple[str, tuple[str | int, ...]]]:
    """The errors of *response*, as (message, path) pairs."""
    return {(error["message"], tuple(error["path"])) for error in response.errors}


TOP_LEVEL = """
query {
    addresses {
        objects { uuid current { value } }
    }
}
"""

NESTED = """
query {
    org_units {
        objects {
            current { addresses { uuid value } }
        }
    }
}
"""

VALUES = ("first@example.org", "second@example.org")


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_reader_reads_addresses_wherever_reached(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, two_addresses: tuple[UUID, UUID]
) -> None:
    set_auth({"reader"}, uuid4())
    expected = {
        (str(uuid), value) for uuid, value in zip(two_addresses, VALUES, strict=True)
    }

    response = graphapi_post(TOP_LEVEL)
    assert response.errors is None
    assert response.data
    objects = response.data["addresses"]["objects"]
    assert {(x["uuid"], x["current"]["value"]) for x in objects} == expected

    response = graphapi_post(NESTED)
    assert response.errors is None
    assert response.data
    addresses = response.data["org_units"]["objects"][0]["current"]["addresses"]
    assert {(x["uuid"], x["value"]) for x in addresses} == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_field_no_rule_grants_is_denied_where_it_is_read(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_policy: SetPolicy,
    two_addresses: tuple[UUID, UUID],
) -> None:
    """Each field of each address is checked at its own path.

    Through the registrations too, which reach an address by UUID with no
    resolver in between: only the check of each field stands there.
    """
    set_policy([ReadRule("Address", true(), frozenset({"uuid"}))])
    set_auth({"reader"}, uuid4())

    response = graphapi_post(TOP_LEVEL)
    assert response.data
    objects = response.data["addresses"]["objects"]
    assert {x["uuid"] for x in objects} == {str(uuid) for uuid in two_addresses}
    assert [x["current"] for x in objects] == [None, None]
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "current", "value"))
        for index in (0, 1)
    }

    response = graphapi_post(
        """
        query {
            registrations(filter: {models: ["address"]}) {
                objects {
                    ... on AddressRegistration { current { uuid value } }
                }
            }
        }
        """
    )
    assert response.data == {
        "registrations": {"objects": [{"current": None}, {"current": None}]}
    }
    assert _failures(response) == {
        (DENIED, ("registrations", "objects", index, "current", "value"))
        for index in (0, 1)
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_an_object_gets_the_fields_of_every_rule_matching_it(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_policy: SetPolicy,
    two_addresses: tuple[UUID, UUID],
) -> None:
    """A rule grants its fields on the objects its predicate matches only."""
    matched, unmatched = two_addresses
    set_policy(
        [
            ReadRule("Address", true(), frozenset({"uuid"})),
            ReadRule(
                "Address",
                OrganisationFunktionRegistrering.organisationfunktion_id == matched,
                frozenset({"value"}),
            ),
        ]
    )
    set_auth({"reader"}, uuid4())

    response = graphapi_post(TOP_LEVEL)

    assert response.data
    objects = response.data["addresses"]["objects"]
    current = {x["uuid"]: x["current"] for x in objects}
    assert current == {str(matched): {"value": VALUES[0]}, str(unmatched): None}
    index = objects.index({"uuid": str(unmatched), "current": None})
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "current", "value"))
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_condition_unknown_of_an_object_grants_nothing_on_it(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_policy: SetPolicy,
    two_addresses: tuple[UUID, UUID],
) -> None:
    """A rule grants its fields where its condition is true, not where it is unknown.

    SQL is three-valued: a condition touching a NULL is NULL of an object, and
    NULL is not a grant. Alone, such a rule denies; beside a rule that does match
    the object, the disjunction of the two is true and the fields are granted.
    """
    matched, unmatched = two_addresses
    set_policy(
        [
            ReadRule("Address", true(), frozenset({"uuid"})),
            ReadRule("Address", literal(None, Boolean), frozenset({"value"})),
            ReadRule(
                "Address",
                OrganisationFunktionRegistrering.organisationfunktion_id == matched,
                frozenset({"value"}),
            ),
        ]
    )
    set_auth({"reader"}, uuid4())

    response = graphapi_post(TOP_LEVEL)

    assert response.data
    objects = response.data["addresses"]["objects"]
    current = {x["uuid"]: x["current"] for x in objects}
    assert current == {str(matched): {"value": VALUES[0]}, str(unmatched): None}
    index = objects.index({"uuid": str(unmatched), "current": None})
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "current", "value"))
    }


ADDRESS_READER = delete(PolicyReader).where(PolicyReader.collection == "Address")

# `uuid` on the address itself, which only a read rule grants, unlike the
# `uuid` of the response wrapping it, which the RBAC map grants
ADDRESS_UUID = """
query {
    addresses {
        objects { current { uuid } }
    }
}
"""

NO_ADDRESS = {"addresses": {"objects": [{"current": None}, {"current": None}]}}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "two_addresses")
async def test_a_reader_dropped_from_the_database_grants_nothing(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
) -> None:
    """Every read is decided by the policies the database holds at the time."""
    async with another_transaction() as (_, session):
        await session.execute(ADDRESS_READER)
    set_auth({"reader"}, uuid4())

    response = graphapi_post(ADDRESS_UUID)

    assert response.data == NO_ADDRESS
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "current", "uuid")) for index in (0, 1)
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "two_addresses")
async def test_a_policy_grants_the_callers_its_selector_names(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
) -> None:
    """A policy is the caller's when one of its selectors matches their roles."""
    async with another_transaction() as (_, session):
        await session.execute(ADDRESS_READER)
        session.add(
            Policy(
                name="HR",
                active=True,
                selectors=[PolicySelector(kind=PolicySelectorKind.role, value="hr")],
                readers=[PolicyReader(collection="Address", fields=["uuid"])],
            )
        )

    # The `reader` role names no policy granting an address any more
    set_auth({"reader"}, uuid4())
    response = graphapi_post(ADDRESS_UUID)
    assert response.data == NO_ADDRESS
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "current", "uuid")) for index in (0, 1)
    }

    # ... but `hr` names one, and holding both roles is holding both policies
    set_auth({"reader", "hr"}, uuid4())
    response = graphapi_post(ADDRESS_UUID)
    assert response.errors is None
    assert response.data
    objects = response.data["addresses"]["objects"]
    assert len(objects) == 2


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_readers_filter_names_the_objects_it_reaches(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
    two_addresses: tuple[UUID, UUID],
) -> None:
    """A reader reaches the objects its CEL filter names, and no others.

    The filter is the GraphQL filter a caller would write on the collection,
    so the objects it names are the ones that query would return.
    """
    matched, unmatched = two_addresses
    async with another_transaction() as (_, session):
        # The seeded reader grants the uuid of every address ...
        await session.execute(
            update(PolicyReader)
            .where(PolicyReader.collection == "Address")
            .values(fields=["uuid"])
        )
        # ... and a second one grants the value of one address only
        session.add(
            Policy(
                name="Values",
                active=True,
                selectors=[
                    PolicySelector(kind=PolicySelectorKind.role, value="reader")
                ],
                readers=[
                    PolicyReader(
                        collection="Address",
                        fields=["value"],
                        filter=f'{{"uuids": ["{matched}"]}}',
                    )
                ],
            )
        )
    set_auth({"reader"}, uuid4())

    response = graphapi_post(TOP_LEVEL)

    assert response.data
    objects = response.data["addresses"]["objects"]
    current = {x["uuid"]: x["current"] for x in objects}
    assert current == {str(matched): {"value": VALUES[0]}, str(unmatched): None}
    index = objects.index({"uuid": str(unmatched), "current": None})
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "current", "value"))
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "two_addresses")
async def test_a_readers_condition_must_hold_for_it_to_apply(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
) -> None:
    """A reader whose CEL condition the caller fails grants them nothing."""
    async with another_transaction() as (_, session):
        await session.execute(
            update(PolicyReader)
            .where(PolicyReader.collection == "Address")
            .values(condition='token.preferred_username == "alice"')
        )

    set_auth({"reader"}, uuid4(), "bruce")
    response = graphapi_post(ADDRESS_UUID)
    assert response.data == NO_ADDRESS
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "current", "uuid")) for index in (0, 1)
    }

    set_auth({"reader"}, uuid4(), "alice")
    response = graphapi_post(ADDRESS_UUID)
    assert response.errors is None
