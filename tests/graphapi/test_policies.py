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
from sqlalchemy import true

from mora.graphapi.policies import Rule
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import SetRules

DENIED = "No policy approved the access"


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

VALUES = ("first@example.org", "second@example.org")


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_a_field_no_rule_grants_is_denied_where_it_is_read(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    create_org_unit: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_address: Callable[[dict[str, Any]], UUID],
) -> None:
    """Each field of each address is checked at its own path.

    The uuid a rule grants comes back while the value none grants is denied,
    nulling the object holding it and reporting an error at the path it was read.
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
        for value in VALUES
    ]
    set_rules([Rule("reader", "Address", true(), frozenset({"uuid"}))])
    set_auth({"reader"}, uuid4())

    response = graphapi_post(TOP_LEVEL)
    assert response.data
    objects = response.data["addresses"]["objects"]
    assert {x["uuid"] for x in objects} == {str(uuid) for uuid in addresses}
    assert [x["current"] for x in objects] == [None, None]
    assert _failures(response) == {
        (DENIED, ("addresses", "objects", index, "current", "value"))
        for index in (0, 1)
    }
