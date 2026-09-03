# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Address reads are guarded by policy rather than by route.

It does not matter how an address is reached: what the caller may read of it
is decided per address, by the rules of their roles' policies (see
`mora.graphapi.policies`).
"""

from collections.abc import Callable
from collections.abc import Iterator
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from graphql import parse

from mora.graphapi import policies
from mora.graphapi.policies import Policy
from mora.graphapi.policies import Read
from mora.graphapi.policies import Rule
from mora.graphapi.policies import requested_fields
from mora.graphapi.schema import get_schema
from mora.graphapi.version import LATEST_VERSION
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

SetPolicy = Callable[[str, Policy], None]


@pytest.fixture
def set_policy() -> Iterator[SetPolicy]:
    """Install a role's policy for the duration of a test.

    Policies have no store of their own yet, so a test supplies one directly.
    """
    original = dict(policies.ROLE_POLICIES)

    def inner(role: str, policy: Policy) -> None:
        policies.ROLE_POLICIES[role] = policy

    yield inner
    policies.ROLE_POLICIES.clear()
    policies.ROLE_POLICIES.update(original)


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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_reader_reads_addresses_wherever_reached(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, org_unit_with_address: UUID
) -> None:
    set_auth({"reader"}, uuid4())

    response = graphapi_post(TOP_LEVEL)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "uuid": str(org_unit_with_address),
                    "current": {"value": "unit@example.org"},
                }
            ]
        }
    }

    response = graphapi_post(NESTED)
    assert response.errors is None
    assert response.data == {
        "org_units": {
            "objects": [
                {
                    "current": {
                        "addresses": [
                            {
                                "uuid": str(org_unit_with_address),
                                "value": "unit@example.org",
                            }
                        ]
                    }
                }
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_fields_are_checked_per_object_however_reached(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_policy: SetPolicy,
    org_unit_with_address: UUID,
) -> None:
    """A field no rule grants is denied even off the collection's resolver.

    The registrations reach an address by UUID, so no resolver stands between
    the caller and the object: only the check of the field itself does.
    """
    set_policy("reader", Policy(rules=(Rule("address", fields=frozenset({"uuid"})),)))
    set_auth({"reader"}, uuid4())

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

    assert response.errors
    assert {error["message"] for error in response.errors} == {
        "No policy approved the access"
    }
    assert {tuple(error["path"]) for error in response.errors} == {
        ("registrations", "objects", 0, "current", "value")
    }
    assert response.data == {"registrations": {"objects": [{"current": None}]}}

    response = graphapi_post(
        """
        query {
            registrations(filter: {models: ["address"]}) {
                objects {
                    ... on AddressRegistration { current { uuid } }
                }
            }
        }
        """
    )
    assert response.errors is None
    assert response.data == {
        "registrations": {
            "objects": [{"current": {"uuid": str(org_unit_with_address)}}]
        }
    }


@pytest.mark.parametrize(
    "query,variables,expected",
    [
        # The fields below every container count, the page's own do not
        (
            """
            query {
                addresses {
                    objects {
                        uuid
                        current { value }
                        validities { user_key }
                        registrations { note current { href } }
                    }
                    page_info { next_cursor }
                }
            }
            """,
            None,
            {
                Read("address", ("addresses",)): frozenset(
                    {"uuid", "value", "user_key", "note", "href"}
                )
            },
        ),
        # Each read has its own fields
        (
            """
            query {
                a: addresses { objects { current { value } } }
                b: addresses { objects { current { user_key } } }
            }
            """,
            None,
            {
                Read("address", ("a",)): frozenset({"value"}),
                Read("address", ("b",)): frozenset({"user_key"}),
            },
        ),
        # Fragments are only a way of writing the selection down
        (
            """
            query {
                addresses { objects { ...response } }
            }
            fragment response on AddressResponse {
                current { ... on Address { value } }
            }
            """,
            None,
            {Read("address", ("addresses",)): frozenset({"value"})},
        ),
        # Fields left out by a directive are not asked for
        (
            """
            query($show: Boolean!) {
                addresses {
                    objects {
                        current {
                            value @include(if: $show)
                            user_key @skip(if: true)
                            name
                        }
                    }
                }
            }
            """,
            {"show": False},
            {Read("address", ("addresses",)): frozenset({"name"})},
        ),
        # An edge is a field of the object it leaves. What lies beyond belongs
        # to the other end, until a field leads into the collection anew.
        (
            """
            query {
                org_units {
                    objects {
                        current {
                            addresses {
                                value
                                org_unit_response {
                                    current { addresses { user_key } }
                                }
                            }
                        }
                    }
                }
            }
            """,
            None,
            {
                Read(
                    "address", ("org_units", "objects", "current", "addresses")
                ): frozenset({"value", "org_unit_response"}),
                Read(
                    "address",
                    (
                        "org_units",
                        "objects",
                        "current",
                        "addresses",
                        "org_unit_response",
                        "current",
                        "addresses",
                    ),
                ): frozenset({"user_key"}),
            },
        ),
        # Reached through the registrations, without a resolver of its own
        (
            """
            query {
                registrations {
                    objects {
                        ... on AddressRegistration { current { value } }
                    }
                }
            }
            """,
            None,
            {
                Read("address", ("registrations", "objects", "current")): frozenset(
                    {"value"}
                )
            },
        ),
    ],
)
def test_requested_fields(
    query: str, variables: dict[str, Any] | None, expected: dict[Read, frozenset[str]]
) -> None:
    schema = get_schema(LATEST_VERSION)._schema

    assert requested_fields(schema, parse(query), None, variables) == expected
