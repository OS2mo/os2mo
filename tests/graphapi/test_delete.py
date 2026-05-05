# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import first

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "collection,mutator",
    [
        ("addresses", "address_delete"),
        ("employees", "employee_delete"),
        ("engagements", "engagement_delete"),
        ("itusers", "ituser_delete"),
    ],
)
async def test_delete_integration_test(
    graphapi_post: GraphAPIPost, collection, mutator
) -> None:
    # Read existing objects
    read_query = f"""
        query ReadQuery {{
          {collection} {{
            objects {{
              uuid
            }}
          }}
        }}
    """
    response = graphapi_post(read_query)

    # Select an arbitrary object for deletion
    some_object = first(response.data[collection]["objects"])
    object_uuid = some_object["uuid"]

    # Delete the object
    mutate_query = f"""
        mutation DeleteMutation($uuid: UUID!) {{
          {mutator}(uuid: $uuid) {{
            uuid
          }}
        }}
    """
    response = graphapi_post(
        mutate_query,
        variables={"uuid": object_uuid},
    )
    assert response.errors is None
    assert response.data[mutator]["uuid"] == object_uuid

    # Read objects again; check that it was deleted
    response = graphapi_post(read_query)
    uuids = {o["uuid"] for o in response.data[collection]["objects"]}
    assert object_uuid not in uuids
