# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Address reads are guarded by policy rather than by route.

It does not matter how an address is reached: what the caller may read of it
is decided per address, by the rules of their roles' policies (see
`mora.graphapi.policies`).
"""

from typing import Any

import pytest
from graphql import parse

from mora.graphapi.policies import Read
from mora.graphapi.policies import requested_fields
from mora.graphapi.schema import get_schema
from mora.graphapi.version import LATEST_VERSION


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
