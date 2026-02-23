# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import datetime
from collections.abc import Callable
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from mora import mapping
from more_itertools import one

from tests import util
from tests.conftest import GQLResponse
from tests.util import dar_loader

from ..conftest import GraphAPIPost

# HELPERS

org_unit_l1 = UUID("2874e1dc-85e6-4269-823a-e1125484dfd3")
user_andersand = UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a")  # andersand
user_fedtmule = UUID("6ee24785-ee9a-4502-81c2-7697009c9053")  # fedtmule
user_erik = UUID("236e0a78-11a0-4ed9-8545-6286bb8611c7")  # erik_smidt_hansen

addr_type_user_address = UUID("4e337d8e-1fd2-4449-8110-e0c8a22958ed")
addr_type_user_email = UUID("c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0")
addr_type_user_phone = UUID("cbadfa0f-ce4f-40b9-86a0-2e85d8961f5d")

addr_type_orgunit_address = UUID("28d71012-2919-4b67-a2f0-7b59ed52561e")
addr_type_orgunit_email = UUID("73360db1-bad3-4167-ac73-8d827c0c8751")
addr_type_orgunit_phone = UUID("1d1d3711-5af4-4084-99b3-df2b8752fdec")

addr_type_orgunit_ean = UUID("e34d4426-9845-4c72-b31e-709be85d6fa2")
addr_type_orgunit_openhours = UUID("e8ea1a09-d3d4-4203-bfe9-d9a2da100f3b")

engagement_andersand = UUID("d000591f-8705-4324-897a-075e3623f37b")
engagement_type_employee = UUID("06f95678-166a-455a-a2ab-121a8d92ea23")

visibility_uuid_public = UUID("f63ad763-0e53-4972-a6a9-63b42a0f8cb7")

tz_cph = ZoneInfo("Europe/Copenhagen")
now_min_cph = datetime.datetime.combine(
    datetime.datetime.now().date(), datetime.datetime.min.time()
).replace(tzinfo=tz_cph)


def async_lora_return(*args):
    """Returns last positional argument using asyncio.Future.

    This is used to mock lora.Scope methods like 'get' and 'update'."""

    f = asyncio.Future()
    f.set_result(args[-1])
    return f


def _get_address_query():
    return """
        query VerifyQuery($uuid: UUID!) {
          addresses(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
            objects {
              uuid
              objects {
                uuid

                validity {
                  from
                  to
                }

                type
                value
                address_type {
                  uuid
                }

                visibility {
                  uuid
                }

                employee {
                  uuid
                }

                org_unit {
                  uuid
                }

                engagement_uuid
              }
            }
          }
        }
    """


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the address data model."""
    query = """
        query {
            addresses {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        address_type_uuid
                        employee_uuid
                        org_unit_uuid
                        engagement_uuid
                        visibility_uuid
                        type
                        value
                        value2
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_integration(graphapi_post: GraphAPIPost):
    """Integration test for create address."""
    test_data = {
        "value": "0a3f50a0-23c9-32b8-e044-0003ba298018",
        "address_type": str(addr_type_orgunit_address),
        "visibility": str(visibility_uuid_public),
        "org_unit": str(org_unit_l1),
        "validity": {
            "from": "2021-01-01T00:00:00+01:00",
            "to": None,
        },
    }

    # mutation invoke
    mutate_query = """
        mutation($input: AddressCreateInput!) {
            address_create(input: $input) {
                uuid
            }
        }
    """

    with util.darmock("dawa-addresses.json", real_http=True), dar_loader():
        response = graphapi_post(query=mutate_query, variables={"input": test_data})

    assert response.errors is None
    assert response.data is not None
    test_data_uuid_new = UUID(response.data["address_create"]["uuid"])

    # query invoke after mutation
    verify_query = _get_address_query()
    verify_response = graphapi_post(
        verify_query,
        {
            "uuid": str(test_data_uuid_new),
        },
    )

    assert verify_response.errors is None
    assert verify_response.data is not None
    new_addr = one(one(verify_response.data["addresses"]["objects"])["objects"])

    # Asserts
    assert new_addr[mapping.UUID] is not None

    assert new_addr["validity"]["from"] == "2021-01-01T00:00:00+01:00"
    assert new_addr["validity"]["to"] is None
    assert new_addr["value"] == test_data["value"]
    assert new_addr["address_type"][mapping.UUID] == test_data["address_type"]
    assert new_addr["visibility"]["uuid"] == test_data["visibility"]
    assert one(new_addr["org_unit"])["uuid"] == test_data["org_unit"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 10),
        # Address Type filters
        ({"address_type_user_keys": "BrugerPostadresse"}, 3),
        ({"address_types": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"}, 3),
        ({"address_type_user_keys": "BrugerEmail"}, 2),
        ({"address_types": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"}, 2),
        ({"address_type_user_keys": ["BrugerPostadresse", "BrugerEmail"]}, 5),
        (
            {
                "address_types": [
                    "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                    "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0",
                ]
            },
            5,
        ),
        # Employee filters
        ({"employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"}, 1),
        ({"employees": "6ee24785-ee9a-4502-81c2-7697009c9053"}, 2),
        (
            {
                "employees": [
                    "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    "6ee24785-ee9a-4502-81c2-7697009c9053",
                ]
            },
            3,
        ),
        # Engagement filters
        ({"engagements": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab"}, 0),
        ({"engagements": "d000591f-8705-4324-897a-075e3623f37b"}, 1),
        # Mixed filters
        (
            {
                "employees": "6ee24785-ee9a-4502-81c2-7697009c9053",
                "address_types": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0",
            },
            1,
        ),
        (
            {
                "employees": "6ee24785-ee9a-4502-81c2-7697009c9053",
                "address_type_user_keys": "BrugerEmail",
            },
            1,
        ),
        # Visibility filter (public)
        ({"visibility": {"uuids": ["f63ad763-0e53-4972-a6a9-63b42a0f8cb7"]}}, 0),
    ],
)
async def test_address_filters(graphapi_post: GraphAPIPost, filter, expected) -> None:
    """Test filters on addresses."""
    address_query = """
        query Addresses($filter: AddressFilter!) {
            addresses(filter: $filter) {
                objects {
                  uuid
                }
            }
        }
    """
    response = graphapi_post(address_query, variables=dict(filter=filter))
    assert response.errors is None
    assert len(response.data["addresses"]["objects"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "fba61e38-b553-47cc-94bf-8c7c3c2a6887",
            "user_key": "bruger@example.comw",
            "org_unit": None,
            "employee": None,
            "address_type": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0",
            "engagement": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab",
            "value": "Giraf@elefant.nu",
            "visibility": None,
            "validity": {"to": None, "from": "1934-06-09T00:00:00+01:00"},
        },
        {
            "uuid": "cd6008bc-1ad2-4272-bc1c-d349ef733f52",
            "user_key": "Christiansborg Slotsplads 1, 1218 København K",
            "org_unit": None,
            "employee": "6ee24785-ee9a-4502-81c2-7697009c9053",
            "address_type": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
            "engagement": None,
            "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
            "visibility": None,
            "validity": {"to": None, "from": "1932-05-12T00:00:00+01:00"},
        },
        {
            "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
            "user_key": "8715 0222",
            "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "employee": None,
            "address_type": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
            "engagement": None,
            "value": "+4587150222",
            "visibility": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
            "validity": {"to": None, "from": "2016-01-01T00:00:00+01:00"},
        },
        {
            "uuid": "a0fe7d43-1e0d-4232-a220-87098024b34d",
            "user_key": "5798000420526",
            "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "employee": None,
            "address_type": "e34d4426-9845-4c72-b31e-709be85d6fa2",
            "engagement": None,
            "value": "5798000420526",
            "visibility": None,
            "validity": {"to": None, "from": "2016-01-01T00:00:00+01:00"},
        },
        {
            "uuid": "a0fe7d43-1e0d-4232-a220-87098024b34d",
            "user_key": "5798000420526",
            "org_unit": None,
            "employee": None,
            "address_type": "e34d4426-9845-4c72-b31e-709be85d6fa2",
            "engagement": "00e96933-91e4-42ac-9881-0fe1738b2e59",
            "value": "5798000420526",
            "visibility": None,
            "validity": {"to": None, "from": "2016-01-01T00:00:00+01:00"},
        },
    ],
)
async def test_update_address_integration_test(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    async def query_data(uuid: str) -> GQLResponse:
        query = """
            query ($uuid: [UUID!]!){
                __typename
                addresses(filter: {uuids: $uuid}){
                    objects {
                        objects {
                            uuid
                            user_key
                            org_unit: org_unit_uuid
                            employee: employee_uuid
                            address_type: address_type_uuid
                            engagement: engagement_uuid
                            value
                            visibility: visibility_uuid
                            validity {
                                to
                                from
                            }
                        }
                    }
                }
            }

        """
        response = graphapi_post(query=query, variables={"uuid": uuid})

        return response

    prior_data = await query_data(test_data["uuid"])
    prior_data = one(
        one(prior_data.data.get("addresses", {})["objects"]).get("objects")
    )

    mutate_query = """
        mutation UpdateAddress($input: AddressUpdateInput!) {
            address_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": test_data})

    posterior_data = await query_data(test_data["uuid"])

    response_data = one(
        one(posterior_data.data.get("addresses", {})["objects"]).get("objects")
    )

    """Assert returned UUID from mutator is correct"""
    assert response.errors is None
    assert response.data.get("address_update", {}).get("uuid", {}) == test_data["uuid"]

    updated_test_data = {k: v or prior_data[k] for k, v in test_data.items()}

    """Asssert data written to db is correct when queried"""
    assert posterior_data.errors is None
    assert updated_test_data == response_data


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_address_resolver(graphapi_post: GraphAPIPost) -> None:
    query = """
        query ResolveAddresses {
          addresses {
            objects {
              current {
                uuid
                value
                resolve {
                  value
                  # Catch all non-overridden address types
                  ... on DefaultAddress {
                    __typename
                    value
                  }
                  # For DAR addresses
                  ... on DARAddress {
                    __typename
                    value

                    description
                    name

                    road_code
                    road_name
                    house_number
                    floor
                    door
                    zip_code
                    zip_code_name
                    municipality_code

                    longitude
                    latitude

                    href
                    streetmap_href
                  }
                  # For Multifield addresses
                  ... on MultifieldAddress {
                    __typename
                    value

                    value2
                    name
                  }
                }
              }
            }
          }
        }
    """

    nordre_ringgade = {
        "__typename": "DARAddress",
        "description": "Nordre Ringgade 1, 8000 Aarhus C",
        "door": None,
        "floor": None,
        "house_number": "1",
        "href": "https://api.dataforsyningen.dk/adresser/b1f1817d-5f02-4331-b8b3-97330a5d3197",
        "latitude": 56.17102843,
        "longitude": 10.19938084,
        "municipality_code": "0751",
        "name": "Nordre Ringgade 1, 8000 Aarhus C",
        "road_code": 5902,
        "road_name": "Nordre Ringgade",
        "streetmap_href": "https://www.openstreetmap.org/?mlon=10.19938084&mlat=56.17102843&zoom=16",
        "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
        "zip_code": "8000",
        "zip_code_name": "Aarhus C",
    }

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "resolve": nordre_ringgade,
                        "uuid": "00e96933-91e4-42ac-9881-0fe1738b2e59",
                        "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                    }
                },
                {
                    "current": {
                        "resolve": nordre_ringgade,
                        "uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80",
                        "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                    }
                },
                {
                    "current": {
                        "resolve": {
                            "__typename": "DefaultAddress",
                            "value": "Fake afdelingskode",
                        },
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0441",
                        "value": "Fake afdelingskode",
                    }
                },
                {
                    "current": {
                        "resolve": nordre_ringgade,
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0444",
                        "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                    }
                },
                {
                    "current": {
                        "resolve": {
                            "__typename": "DefaultAddress",
                            "value": "+4587150000",
                        },
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
                        "value": "+4587150000",
                    }
                },
                {
                    "current": {
                        "resolve": {
                            "__typename": "DefaultAddress",
                            "value": "goofy@example.com",
                        },
                        "uuid": "64ea02e2-8469-4c54-a523-3d46729e86a7",
                        "value": "goofy@example.com",
                    }
                },
                {
                    "current": {
                        "resolve": {
                            "__typename": "DefaultAddress",
                            "value": "5798000420526",
                        },
                        "uuid": "a0fe7d43-1e0d-4232-a220-87098024b34d",
                        "value": "5798000420526",
                    }
                },
                {
                    "current": {
                        "resolve": nordre_ringgade,
                        "uuid": "cd6008bc-1ad2-4272-bc1c-d349ef733f52",
                        "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                    }
                },
                {
                    "current": {
                        "resolve": nordre_ringgade,
                        "uuid": "e1a9cede-8c9b-4367-b628-113834361871",
                        "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                    }
                },
                {
                    "current": {
                        "resolve": {
                            "__typename": "DefaultAddress",
                            "value": "bruger@example.com",
                        },
                        "uuid": "fba61e38-b553-47cc-94bf-8c7c3c2a6887",
                        "value": "bruger@example.com",
                    }
                },
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_address_resolver_supplementary_city(
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    employee_address_type_facet = create_facet(
        {
            "user_key": "employee_address_type",
            "validity": {"from": "1970-01-01"},
        }
    )
    post_address_class = create_class(
        {
            "user_key": "AdressePostEmployee",
            "scope": "DAR",
            "name": "Postadresse",
            "facet_uuid": str(employee_address_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )

    person_uuid = create_person()
    value = "1a6da4cb-e2b4-40a3-b9c0-ff4f2f5fba97"

    create_address_mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
      address_create(input: $input) {
        uuid
      }
    }
    """
    input = {
        "address_type": str(post_address_class),
        "value": value,
        "person": str(person_uuid),
        "validity": {"from": "2000-01-01T00:00:00Z"},
    }
    response = graphapi_post(create_address_mutation, variables={"input": input})
    assert response.errors is None
    assert response.data is not None
    address_uuid = response.data["address_create"]["uuid"]

    query = """
        query ResolveAddresses {
          addresses {
            objects {
              current {
                uuid
                value
                resolve {
                  ... on DARAddress {
                    __typename
                    name
                    road_name
                    house_number
                    supplementary_city
                    zip_code
                    zip_code_name
                  }
                }
              }
            }
          }
        }
    """

    jonstrupvangvej = {
        "__typename": "DARAddress",
        "name": "Jonstrupvangvej 150D, Jonstrup, 3500 Værløse",
        "road_name": "Jonstrupvangvej",
        "house_number": "150D",
        "supplementary_city": "Jonstrup",
        "zip_code": "3500",
        "zip_code_name": "Værløse",
    }

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "resolve": jonstrupvangvej,
                        "uuid": address_uuid,
                        "value": value,
                    }
                }
            ]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_address_resolver_missing_fields(
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> None:
    employee_address_type_facet = create_facet(
        {
            "user_key": "employee_address_type",
            "validity": {"from": "1970-01-01"},
        }
    )
    post_address_class = create_class(
        {
            "user_key": "AdressePostEmployee",
            "scope": "DAR",
            "name": "Postadresse",
            "facet_uuid": str(employee_address_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )

    person_uuid = create_person()
    # Kirke Værløsevej 36, 3500 Værløse is a historic DAR address, thus missing fields
    # compared to a current address.
    value = "0a3f507e-31b9-32b8-e044-0003ba298018"

    create_address_mutation = """
    mutation CreateAddress($input: AddressCreateInput!) {
      address_create(input: $input) {
        uuid
      }
    }
    """
    input = {
        "address_type": str(post_address_class),
        "value": value,
        "person": str(person_uuid),
        "validity": {"from": "2000-01-01T00:00:00Z"},
    }
    response = graphapi_post(create_address_mutation, variables={"input": input})
    assert response.errors is None
    assert response.data is not None
    address_uuid = response.data["address_create"]["uuid"]

    query = """
        query ResolveAddresses {
          addresses {
            objects {
              current {
                uuid
                value
                resolve {
                  ... on DARAddress {
                    __typename
                    name
                    floor
                    door
                  }
                }
              }
            }
          }
        }
    """

    jonstrupvangvej = {
        "__typename": "DARAddress",
        "name": "Kirke Værløsevej 36, 3500 Værløse",
        "floor": None,
        "door": None,
    }

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "addresses": {
            "objects": [
                {
                    "current": {
                        "resolve": jonstrupvangvej,
                        "uuid": address_uuid,
                        "value": value,
                    }
                }
            ]
        }
    }
