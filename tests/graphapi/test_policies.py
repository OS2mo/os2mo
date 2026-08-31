# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Address reads are guarded collection-based, not route-based.

It does not matter how an address is reached: every read resolves the same
addresses, the ones the caller may see per the collection's predicate (see
`mora.graphapi.policies`). Reaching for addresses is therefore never
forbidden; without the reader role the collection is simply empty.
"""

from uuid import UUID
from uuid import uuid4

import pytest

from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

TOP_LEVEL = """
query {
    addresses {
        objects { uuid }
    }
}
"""

NESTED = """
query {
    org_units {
        objects {
            objects {
                addresses { uuid }
            }
        }
    }
}
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
@pytest.mark.parametrize("roles", [set(), {"no_such_role"}])
async def test_addresses_empty_without_reader(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    roles: set[str],
) -> None:
    """Without the reader role the collection is empty, not forbidden."""
    set_auth(roles, uuid4())

    response = graphapi_post(TOP_LEVEL)

    assert response.errors is None
    assert response.data == {"addresses": {"objects": []}}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
async def test_addresses_readable_via_query(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, org_unit_with_address: UUID
) -> None:
    """The reader sees the address through the top-level collection."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(TOP_LEVEL)

    assert response.errors is None
    assert response.data
    assert {x["uuid"] for x in response.data["addresses"]["objects"]} == {
        str(org_unit_with_address)
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "org_unit_with_address")
async def test_addresses_readable_nested(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, org_unit_with_address: UUID
) -> None:
    """The reader sees the same address hanging off its org-unit."""
    set_auth({"reader"}, uuid4())

    response = graphapi_post(NESTED)

    assert response.errors is None
    assert response.data
    assert {
        address["uuid"]
        for org_unit in response.data["org_units"]["objects"]
        for validity in org_unit["objects"]
        for address in validity["addresses"]
    } == {str(org_unit_with_address)}
