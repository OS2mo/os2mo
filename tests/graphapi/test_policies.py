# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The fields of an address are guarded by read policies rather than by role.

Wherever an address is reached, what the caller may read of it is decided per
address: the fields granted by the rules of their roles matching it (see
`mora.graphapi.policies`).
"""

from collections.abc import Callable
from collections.abc import Iterator
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy import true

from mora.db import OrganisationFunktionRegistrering
from mora.graphapi import policies
from mora.graphapi.policies import Rule
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

SetPolicy = Callable[[str, list[Rule]], None]

DENIED = "No policy approved the access"


@pytest.fixture
def set_policy() -> Iterator[SetPolicy]:
    """Install a role's rules for the duration of a test.

    Policies have no store of their own yet, so a test supplies them directly.
    """
    original = dict(policies.ROLE_POLICIES)

    def inner(role: str, rules: list[Rule]) -> None:
        policies.ROLE_POLICIES[role] = rules

    yield inner
    policies.ROLE_POLICIES.clear()
    policies.ROLE_POLICIES.update(original)


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
    set_policy("reader", [("Address", true(), frozenset({"uuid"}))])
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
        "reader",
        [
            ("Address", true(), frozenset({"uuid"})),
            (
                "Address",
                OrganisationFunktionRegistrering.organisationfunktion_id == matched,
                frozenset({"value"}),
            ),
        ],
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
