# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_address_update_ituser_null_is_noop(
    graphapi_post: GraphAPIPost,
    create_address: Callable[[dict[str, Any]], UUID],
    read_address_ituser_uuid: Callable[[UUID], UUID | None],
    address_ituser_structure: dict[str, UUID],
) -> None:
    """`ituser: null` is no-op and leaves the relation alone."""
    ituser_uuid = address_ituser_structure["ituser_uuid"]
    address_type = address_ituser_structure["address_type"]

    address_uuid = create_address(
        {
            "value": "user@example.com",
            "address_type": str(address_type),
            "person": str(address_ituser_structure["person_uuid"]),
            "ituser": str(ituser_uuid),
            "validity": {"from": "2020-01-01"},
        }
    )
    assert read_address_ituser_uuid(address_uuid) == ituser_uuid

    mutation = """
        mutation UpdateAddress($input: AddressUpdateInput!) {
            address_update(input: $input) {
                uuid
            }
        }
    """
    variables = {
        "input": {
            "uuid": str(address_uuid),
            "value": "new@example.com",
            "address_type": str(address_type),
            "ituser": None,
            "validity": {"from": "2021-01-01"},
        }
    }
    response = graphapi_post(mutation, variables=variables, url="/graphql/v30")
    assert response.errors is None
    assert response.data is not None

    # Relation untouched, unlike on v31 and later.
    assert read_address_ituser_uuid(address_uuid) == ituser_uuid
