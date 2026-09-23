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

from tests.conftest import DeclarePolicy
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

DENIED = "No policy approved the access"


def _failures(response: Any) -> set[tuple[str, tuple[str | int, ...]]]:
    """The errors of *response*, as (message, path) pairs."""
    return {(error["message"], tuple(error["path"])) for error in response.errors}


@pytest.mark.integration_test
@pytest.mark.usefixtures("no_seeded_policies")
async def test_a_field_no_rule_grants_is_denied_where_it_is_read(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    declare_policy: DeclarePolicy,
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """Each field of each address is checked at its own path.

    The uuid a rule grants comes back while the value none grants is denied,
    nulling the object holding it and reporting an error at the path it was read.
    """
    # The value is read on a `current` of its own, so denying it keeps the uuid
    query = """
        query ReadAddresses {
            addresses {
                objects {
                    current { uuid }
                    value: current { value }
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
    addresses = [
        create_address(
            {
                "address_type": str(address_type),
                "org_unit": str(org_unit),
                "value": value,
                "validity": {"from": "2000-01-01"},
            }
        )
        for value in ("first@example.org", "second@example.org")
    ]
    declare_policy(
        str(uuid4()),
        {
            "name": "Reader",
            "role": "reader",
            "read_rules": [
                {
                    "collection": "Address",
                    "fields": ["uuid"],
                    "graphql_version": "VERSION_30",
                }
            ],
        },
    )
    set_auth({"reader"}, uuid4())

    response = graphapi_post(query)
    assert response.data
    objects = response.data["addresses"]["objects"]
    assert {x["current"]["uuid"] for x in objects} == {str(uuid) for uuid in addresses}
    assert [x["value"] for x in objects] == [None, None]
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "value", "value")) for index in (0, 1)
    }
