# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest

from tests.util import load_fixture


@pytest.mark.integration_test
@pytest.mark.usefixtures("sample_structures_minimal")
async def test_dangling_foreign_key(graphapi_post: Callable) -> None:
    engagement_uuid = "301a906b-ef51-4d5c-9c77-386fb8410459"
    employee_uuid = "236e0a78-11a0-4ed9-8545-6286bb8611c7"
    address_type_uuid = "cbadfa0f-ce4f-40b9-86a0-2e85d8961f5d"
    employee_address_type_uuid = "baddc4eb-406e-4c6b-8229-17e4a21d3550"

    await load_fixture(
        "klassifikation/facet",
        "create_facet_employee_address_type.json",
        employee_address_type_uuid,
    )
    await load_fixture(
        "klassifikation/klasse", "create_klasse_bruger_telefon.json", address_type_uuid
    )

    # Create a new address bound to both a user and their engagement
    response = graphapi_post(
        """
        mutation CreateAddress(
            $employee_uuid: UUID!,
            $engagement_uuid: UUID!,
            $address_type_uuid: UUID!,
        ) {
          address_create(input: {
            value: "12345678",
            person: $employee_uuid,
            engagement: $engagement_uuid,
            address_type: $address_type_uuid,
            validity: {
              from: "2000-01-01"
            }
          }) {
            uuid
          }
        }
        """,
        {
            "employee_uuid": employee_uuid,
            "engagement_uuid": engagement_uuid,
            "address_type_uuid": address_type_uuid,
        },
    )
    assert response.errors is None
    address_uuid = response.data["address_create"]["uuid"]
    assert response.data == {"address_create": {"uuid": address_uuid}}

    # Check that we can read out the address as ẃe expect
    address_read_query = """
        query ReadAddress($uuid: UUID!) {
          addresses(uuids: [$uuid]) {
            objects {
              current {
                engagement_uuid
                engagement {
                  uuid
                }
              }
            }
          }
        }
    """
    response = graphapi_post(address_read_query, {"uuid": address_uuid})
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "engagement_uuid": engagement_uuid,
                        "engagement": [{"uuid": engagement_uuid}],
                    }
                }
            ]
        }
    }

    # Now lets delete the engagement, this creates a dangling foreign key
    response = graphapi_post(
        """
        mutation DeleteEngagement($engagement_uuid: UUID!){
          engagement_delete(uuid: $engagement_uuid) {
            uuid
          }
        }
        """,
        {"engagement_uuid": engagement_uuid},
    )
    assert response.errors is None
    assert response.data == {"engagement_delete": {"uuid": engagement_uuid}}

    # So if we read the address now, we have a dangling reference
    response = graphapi_post(address_read_query, {"uuid": address_uuid})
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        # UUID is still set
                        "engagement_uuid": engagement_uuid,
                        # But engagement is empty since the foreign key is dangling
                        "engagement": [],
                    }
                }
            ]
        }
    }
