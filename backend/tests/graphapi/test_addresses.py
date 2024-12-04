# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import datetime
from datetime import datetime as dt
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import HealthCheck
from hypothesis import settings
from hypothesis import strategies as st
from more_itertools import one

from ..conftest import GraphAPIPost
from mora import mapping
from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.models import AddressCreate
from mora.graphapi.versions.latest.models import AddressUpdate
from mora.graphapi.versions.latest.models import RAValidity
from tests import util
from tests.conftest import GQLResponse
from tests.graphapi.utils import fetch_employee_validity
from tests.graphapi.utils import fetch_org_unit_validity
from tests.util import dar_loader

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


def _create_address_create_hypothesis_test_data(
    data, graphapi_post: GraphAPIPost, test_data_samples
):
    (
        test_data_org_unit_uuid,
        test_data_person_uuid,
        test_data_engagement_uuid,
        address_type,
    ) = data.draw(st.sampled_from(test_data_samples))

    dt_options_min_from = datetime.datetime(1930, 1, 1, 1)
    if test_data_org_unit_uuid and graphapi_post:
        org_unit_validity_from, _ = fetch_org_unit_validity(
            graphapi_post, test_data_org_unit_uuid
        )
        dt_options_min_from = org_unit_validity_from
    elif test_data_person_uuid and graphapi_post:
        person_validity_from, _ = fetch_employee_validity(
            graphapi_post, test_data_person_uuid
        )
        dt_options_min_from = person_validity_from

    dt_options = {
        "min_value": dt_options_min_from,
        "timezones": st.just(ZoneInfo("Europe/Copenhagen")),
    }
    test_datavalidity_tuple = data.draw(
        st.tuples(
            st.datetimes(**dt_options),
            st.datetimes(**dt_options) | st.none(),
        ).filter(lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True)
    )
    test_data_from, test_data_to = test_datavalidity_tuple

    if address_type in (addr_type_orgunit_address, addr_type_user_address):
        # FYI: The UUIDs we sample from, are the ones found in:
        # backend/tests/mocking/dawa-addresses.json
        test_data_value = data.draw(
            st.sampled_from(
                [
                    "0a3f50a0-23c9-32b8-e044-0003ba298018",
                    "44c532e1-f617-4174-b144-d37ce9fda2bd",
                    "606cf42e-9dc2-4477-bf70-594830fcbdec",
                    "ae95777c-7ec1-4039-8025-e2ecce5099fb",
                    "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                    "bae093df-3b06-4f23-90a8-92eabedb3622",
                    "d901ff7e-8ad9-4581-84c7-5759aaa82f7b",
                ]
            )
        )
    elif address_type in (addr_type_user_email, addr_type_orgunit_email):
        test_data_value = data.draw(st.emails())
    elif address_type in (addr_type_user_phone, addr_type_orgunit_phone):
        test_data_value = data.draw(st.from_regex(r"^\+?\d+$"))
    elif address_type in (addr_type_orgunit_ean,):
        test_data_value = data.draw(st.from_regex(r"^\d{13}$"))
    else:
        test_data_value = data.draw(
            st.text(
                alphabet=st.characters(
                    blacklist_categories=(
                        "Cs",  # st.text() default blacklist_categories (surrogate chars)
                        "Cc",  # prevent hypothesis from creating control chars (ex: "\x00")
                    )
                )
            )
        )

    return data.draw(
        st.builds(
            AddressCreate,
            value=st.just(test_data_value),
            address_type=st.just(address_type),
            visibility=st.just(visibility_uuid_public),
            org_unit=st.just(test_data_org_unit_uuid),
            person=st.just(test_data_person_uuid),
            engagement=st.just(test_data_engagement_uuid),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_from),
                to_date=st.just(test_data_to),
            ),
        )
    )


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


@given(data=st.data())
@patch("mora.graphapi.versions.latest.mutators.create_address", new_callable=AsyncMock)
async def test_create_mutator(create_address: AsyncMock, data):
    # Mocking
    create_address.return_value = uuid4()

    # Prepare test_data
    test_data_samples = [
        # org units
        (
            org_unit_l1,
            None,
            None,
            addr_type_orgunit_address,
        ),
        (
            org_unit_l1,
            None,
            None,
            addr_type_orgunit_email,
        ),
        (
            org_unit_l1,
            None,
            None,
            addr_type_orgunit_phone,
        ),
        (
            org_unit_l1,
            None,
            None,
            addr_type_orgunit_ean,
        ),
        (
            org_unit_l1,
            None,
            engagement_andersand,
            addr_type_orgunit_openhours,
        ),
        # Users
        (
            None,
            user_andersand,
            None,
            addr_type_user_address,
        ),
        (
            None,
            user_andersand,
            None,
            addr_type_user_email,
        ),
        (
            None,
            user_andersand,
            engagement_andersand,
            addr_type_user_phone,
        ),
    ]

    test_data = _create_address_create_hypothesis_test_data(
        data, None, test_data_samples
    )
    payload = jsonable_encoder(test_data)

    # Invoke the mutator
    mutate_query = """
        mutation($input: AddressCreateInput!) {
            address_create(input: $input) {
                uuid
            }
        }
    """
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {
        "address_create": {"uuid": str(create_address.return_value)}
    }

    create_address.assert_called_with(test_data)


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_multiple_addresses_integration_test(
    data, graphapi_post: GraphAPIPost, org_uuids, employee_uuids
) -> None:
    """Test that multiple addresses can be created using the list mutator."""

    org_uuid = data.draw(st.sampled_from(org_uuids))
    org_from, org_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=org_from, max_value=org_to or dt.max)
    )
    if org_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=org_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    test_data = data.draw(
        st.lists(
            st.builds(
                AddressCreate,
                person=st.sampled_from(employee_uuids),
                address_type=st.just(addr_type_user_email),
                value=st.emails(),
                validity=st.builds(
                    RAValidity,
                    from_date=st.just(test_data_validity_start),
                    to_date=test_data_validity_end_strat,
                ),
            ),
        )
    )

    CREATE_ADDRESSES_QUERY = """
        mutation CreateAddress($input: [AddressCreateInput!]!) {
            addresses_create(input: $input) {
                uuid
            }
        }
    """

    response = graphapi_post(
        CREATE_ADDRESSES_QUERY, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuids = [address["uuid"] for address in response.data["addresses_create"]]
    assert len(uuids) == len(test_data)


@pytest.mark.parametrize(
    "given_mutator_args",
    [
        {  # Desc: verify fails, when dates are invalid.
            "from_date": now_min_cph,
            "to_date": now_min_cph - datetime.timedelta(days=1),
            "value": "YeeHaaamagenta.dk",
            "address_type": addr_type_user_email,
            "visibility": visibility_uuid_public,
            "person": user_andersand,
        },
        {  # Desc: verify fails when No relation was supplied
            "from_date": now_min_cph,
            "to_date": None,
            "value": "YeeHaaa@magenta.dk",
            "address_type": addr_type_user_email,
            "visibility": visibility_uuid_public,
        },
        {  # Desc: verify fails when more than one relation was supplied
            "from_date": now_min_cph,
            "to_date": None,
            "value": "YeeHaaa@magenta.dk",
            "address_type": addr_type_user_email,
            "visibility": visibility_uuid_public,
            "person": user_andersand,
            "org_unit": org_unit_l1,
        },
    ],
)
@patch("mora.graphapi.versions.latest.mutators.create_address", new_callable=AsyncMock)
async def test_create_mutator_fails(create_address: AsyncMock, given_mutator_args):
    payload = {
        "from": given_mutator_args["from_date"].isoformat(),
        "to": given_mutator_args["to_date"].isoformat()
        if given_mutator_args.get("to_date", None)
        else None,
        "value": given_mutator_args["value"],
        "address_type": str(given_mutator_args["address_type"]),
        "visibility": str(given_mutator_args["visibility"]),
    }

    mutate_query = """
        mutation($input: AddressCreateInput!) {
            address_create(input: $input) {
                uuid
            }
        }
    """
    _ = await execute_graphql(query=mutate_query, variable_values={"input": payload})

    create_address.assert_not_called()


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_integration(data, graphapi_post: GraphAPIPost):
    """Integration test for create address.

    OBS: Does currently not test address-relation to engagements.
    """

    # Configre test data samples
    test_data_samples_addrs = [
        (
            UUID("2874e1dc-85e6-4269-823a-e1125484dfd3"),
            None,
            None,
            addr_type_orgunit_address,
        ),
        (
            None,
            UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            None,
            addr_type_user_address,
        ),
        (
            None,
            UUID("6ee24785-ee9a-4502-81c2-7697009c9053"),
            None,
            addr_type_user_address,
        ),
        (
            None,
            UUID("236e0a78-11a0-4ed9-8545-6286bb8611c7"),
            None,
            addr_type_user_address,
        ),
    ]

    test_data_samples_emails = [
        (
            org_unit_l1,
            None,
            None,
            addr_type_orgunit_email,
        ),
        (
            None,
            user_andersand,
            None,
            addr_type_user_email,
        ),
        (
            None,
            user_fedtmule,
            None,
            addr_type_user_email,
        ),
        (
            None,
            user_erik,
            None,
            addr_type_user_email,
        ),
    ]

    test_data_samples_phone = [
        (
            org_unit_l1,
            None,
            None,
            addr_type_orgunit_phone,
        ),
        (
            None,
            user_andersand,
            None,
            addr_type_user_phone,
        ),
        (
            None,
            user_fedtmule,
            None,
            addr_type_user_phone,
        ),
        (
            None,
            user_erik,
            None,
            addr_type_user_phone,
        ),
    ]

    test_data_samples_ean = [
        (
            org_unit_l1,
            None,
            None,
            addr_type_orgunit_ean,
        ),
    ]

    test_data_samples_openhours = [
        (
            org_unit_l1,
            None,
            None,
            addr_type_orgunit_openhours,
        ),
    ]

    test_data_samples = (
        test_data_samples_addrs
        + test_data_samples_emails
        + test_data_samples_phone
        + test_data_samples_ean
        + test_data_samples_openhours
    )

    test_data = _create_address_create_hypothesis_test_data(
        data, graphapi_post, test_data_samples
    )

    payload = jsonable_encoder(test_data)

    # mutation invoke
    mutate_query = """
        mutation($input: AddressCreateInput!) {
            address_create(input: $input) {
                uuid
            }
        }
    """

    with util.darmock("dawa-addresses.json", real_http=True), dar_loader():
        response = graphapi_post(query=mutate_query, variables={"input": payload})

    assert response.errors is None
    test_data_uuid_new = UUID(response.data["address_create"]["uuid"])

    # query invoke after mutation
    verify_query = _get_address_query()
    verify_response = graphapi_post(
        verify_query,
        {mapping.UUID: str(test_data_uuid_new)},
    )

    assert verify_response.errors is None
    new_addr = one(one(verify_response.data["addresses"]["objects"])["objects"])

    # Asserts
    assert new_addr[mapping.UUID] is not None

    assert (
        new_addr[mapping.VALIDITY][mapping.FROM]
        == datetime.datetime.combine(
            test_data.validity.from_date.date(), datetime.datetime.min.time()
        )
        .replace(tzinfo=tz_cph)
        .isoformat()
    )
    assert new_addr[mapping.VALIDITY][mapping.TO] == (
        datetime.datetime.combine(
            test_data.validity.to_date.date(), datetime.datetime.min.time()
        )
        .replace(tzinfo=tz_cph)
        .isoformat()
        if test_data.validity.to_date
        else None
    )

    assert new_addr[mapping.VALUE] == test_data.value
    assert new_addr[mapping.ADDRESS_TYPE][mapping.UUID] == str(test_data.address_type)
    assert new_addr[mapping.VISIBILITY][mapping.UUID] == str(test_data.visibility)

    if test_data.org_unit:
        assert one(new_addr[mapping.ORG_UNIT])[mapping.UUID] == str(test_data.org_unit)
    elif test_data.person:
        # INFO: here is a confusing part where we create using PERSON, but fetch using EMPLOYEE:
        assert one(new_addr[mapping.EMPLOYEE])[mapping.UUID] == str(test_data.person)
    elif test_data.engagement:
        assert new_addr["engagement_uuid"] == str(test_data.engagement)


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
    response = graphapi_post(mutate_query, {"input": jsonable_encoder(test_data)})

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


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.update_address", new_callable=AsyncMock)
async def test_update_address_unit_test(
    update_address: AsyncMock, test_data: AddressUpdate
) -> None:
    """Test that pydantic jsons are passed through to address_update."""

    mutate_query = """
        mutation UpdateAddress($input: AddressUpdateInput!) {
            address_update(input: $input) {
                uuid
            }
        }
    """

    address_uuid_to_update = uuid4()
    update_address.return_value = address_uuid_to_update

    payload = jsonable_encoder(test_data)

    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"address_update": {"uuid": str(address_uuid_to_update)}}

    update_address.assert_called_with(test_data)


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
