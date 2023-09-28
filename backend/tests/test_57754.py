from uuid import UUID
from datetime import datetime
from mora.service.address_handler.dar import dar_loader_context

import pytest
import freezegun
from mora.common import get_connector
from mora.handler.impl.address import AddressReader


@freezegun.freeze_time("2023-09-19T7:39:42")
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_57754(graphapi_post):

    print(datetime.now().isoformat())

    org = "456362c4-0ee4-4e5e-a72c-751239745e62"
    org_unit_address = "28d71012-2919-4b67-a2f0-7b59ed52561e"

    org_create_mutation = """
        mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
            org_unit_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        org_create_mutation,
        {
            "input": {
                "name": "AddressTester",
                "parent": org,
                "validity": {"from": "2000-01-01"},
                "org_unit_type": "ca76a441-6226-404f-88a9-31e02e420e52",
            }
        },
    )
    assert response.errors is None
    org_uuid = str(UUID(response.data["org_unit_create"]["uuid"]))

    create_mutation = """
        mutation CreateAddress($input: AddressCreateInput!) {
            address_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        create_mutation,
        {
            "input": {
                # TODO: tidspunkt off
                "validity": {"from": "2005-11-30 23:00:00+00"},
                "value": "0a3f50c2-f7aa-32b8-e044-0003ba298018",
                "address_type": org_unit_address,
                "org_unit": org_uuid,
            }
        },
    )
    assert response.errors is None
    address_uuid = str(UUID(response.data["address_create"]["uuid"]))

    # Ingen 2007 i respons dataene

    update_mutation = """
        mutation UpdateAddress($input: AddressUpdateInput!) {
            address_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        update_mutation,
        {
            "input": {
                "uuid": address_uuid,
                "validity": {"from": "2007-02-01 23:00:00+00"},
                "value": "5eebbcd0-126f-4967-b97a-9d68c4edade5",
                "address_type": org_unit_address,
                "org_unit": org_uuid,
            }
        },
    )
    assert response.errors is None

    response = graphapi_post(
        update_mutation,
        {
            "input": {
                "uuid": address_uuid,
                "validity": {"from": "2019-02-01 23:00:00+00"},
                "value": "bea54716-ac75-4400-8bed-4da1bfb9a1ad",
                "address_type": org_unit_address,
                "org_unit": org_uuid,
            }
        },
    )
    assert response.errors is None

    query = """
        query OrgUnitDecorate($uuids: [UUID!]) {
            org_units(uuids: $uuids, from_date: null, to_date: null) {
                objects {
                    uuid

                    current {
                        ...orgunit_details
                    }
                    objects {
                        ...orgunit_details
                    }
                }
            }
        }

        fragment orgunit_details on OrganisationUnit {
            uuid
            name
            user_key
            validity {
                from
                to
            }

            ancestors {
                name
            }

            addresses {
                uuid
                name
                address_type {
                    uuid
                    name
                }
            }
        }
    """
    response = graphapi_post(query, {"uuids": [org_uuid]}, url="/graphql/v8")
    assert response.errors is None
    print(response)

    assert False
