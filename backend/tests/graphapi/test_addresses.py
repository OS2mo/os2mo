# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import infer
from hypothesis import strategies as st
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import lora
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.address import terminate_addr
from mora.graphapi.versions.latest.models import AddressCreate
from mora.graphapi.versions.latest.models import AddressTerminate
from mora.graphapi.versions.latest.models import AddressUpdate
from mora.graphapi.versions.latest.types import AddressCreateType
from mora.graphapi.versions.latest.types import AddressType
from ramodels.mo.details import AddressRead
from tests.conftest import GQLResponse


def async_lora_return(*args):
    """Returns last positional argument using asyncio.Future.

    This is used to mock lora.Scope methods like 'get' and 'update'."""

    f = asyncio.Future()
    f.set_result(args[-1])
    return f


@given(test_data=graph_data_strat(AddressRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the address data model."""
    # JSON encode test data
    test_data = jsonable_encoder(test_data)

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                addresses {
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
                        validity {from to}
                    }
                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["addresses"]) == test_data


@given(test_input=graph_data_uuids_strat(AddressRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query addresses by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    addresses(uuids: $uuids) {
                        uuid
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [addr.get("uuid") for addr in response.data["addresses"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


# @given(test_data=...)
@given(data=st.data())
@patch("mora.graphapi.versions.latest.mutators.address_create", new_callable=AsyncMock)
async def test_create_mutator(address_create: AsyncMock, data):
    # Mocking
    address_create.return_value = AddressCreateType(uuid=uuid4())

    # Prepare test_data
    dt_options = {
        "min_value": datetime.datetime(1930, 1, 1, 1),
        "timezones": st.just(ZoneInfo("Europe/Copenhagen")),
    }

    test_datavalidity_tuple = data.draw(
        st.tuples(
            st.datetimes(**dt_options),
            st.datetimes(**dt_options) | st.none(),
        ).filter(lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True)
    )
    test_data_from, test_data_to = test_datavalidity_tuple

    test_data = data.draw(
        st.builds(
            AddressCreate,
            from_date=st.just(test_data_from),
            to_date=st.just(test_data_to),
            # OBS: if we don't use infer, org_unit relations objects will always be set to None
            org_unit=infer,
            person=infer,
            engagement=infer,
        )
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
        "address_create": {"uuid": str(address_create.return_value.uuid)}
    }

    address_create.assert_called_with(test_data)


@given(
    given_uuid=st.uuids(),
    triggerless=st.booleans(),
    given_validity_dts=st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
@patch.object(lora.Scope, "update", async_lora_return)
@patch.object(lora.Scope, "get", async_lora_return)
async def test_terminate(given_uuid, triggerless, given_validity_dts):
    from_date, to_date = given_validity_dts

    # The terminate logic have a check that verifies we don't use times other than:
    # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
    # expect an exception.
    expect_exception = False
    if to_date.time() != datetime.time.min:
        expect_exception = True

    # Configure the addr-terminate we want to perform
    at = AddressTerminate(
        uuid=given_uuid,
        triggerless=triggerless,
        from_date=from_date,
        to_date=to_date,
    )

    terminate_result_uuid = None
    caught_exception = None
    try:
        tr = await terminate_addr(address_terminate=at)
        terminate_result_uuid = tr.uuid if tr else terminate_result_uuid
    except Exception as e:
        caught_exception = e

    # Assert
    if not expect_exception:
        assert terminate_result_uuid == at.uuid
    else:
        assert caught_exception is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_class_reset")
@pytest.mark.parametrize(
    "filter_snippet,expected",
    [
        ("", 7),
        # Address Type filters
        ('(address_type_user_keys: "BrugerPostadresse")', 1),
        ('(address_types: "4e337d8e-1fd2-4449-8110-e0c8a22958ed")', 1),
        ('(address_type_user_keys: "BrugerEmail")', 2),
        ('(address_types: "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0")', 2),
        ('(address_type_user_keys: ["BrugerPostadresse", "BrugerEmail"])', 3),
        (
            """
            (address_types: [
                "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
            ])
        """,
            3,
        ),
        (
            """
            (
                address_type_user_keys: "BrugerPostadresse"
                address_types: "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
            )
        """,
            3,
        ),
        # Employee filters
        ('(employees: "53181ed2-f1de-4c4a-a8fd-ab358c2c454a")', 1),
        ('(employees: "6ee24785-ee9a-4502-81c2-7697009c9053")', 2),
        (
            """
            (employees: [
                "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "6ee24785-ee9a-4502-81c2-7697009c9053"
            ])
        """,
            3,
        ),
        # Mixed filters
        (
            """
            (
                employees: "6ee24785-ee9a-4502-81c2-7697009c9053",
                address_types: "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
            )
        """,
            1,
        ),
        (
            """
            (
                employees: "6ee24785-ee9a-4502-81c2-7697009c9053",
                address_type_user_keys: "BrugerEmail"
            )
        """,
            1,
        ),
    ],
)
async def test_address_filters(graphapi_post, filter_snippet, expected) -> None:
    """Test filters on addresses."""
    address_query = f"""
        query Addresses {{
            addresses{filter_snippet} {{
                uuid
            }}
        }}
    """
    response: GQLResponse = graphapi_post(address_query)
    assert response.errors is None
    assert len(response.data["addresses"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
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
    ],
)
async def test_update_address_integration_test(test_data, graphapi_post) -> None:
    async def query_data(uuid: str) -> GQLResponse:

        query = """
            query ($uuid: [UUID!]!){
                __typename
                addresses(uuids: $uuid){
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

        """
        response: GQLResponse = graphapi_post(query=query, variables={"uuid": uuid})

        return response

    prior_data = await query_data(test_data["uuid"])
    prior_data = one(one(prior_data.data.get("addresses", {})).get("objects"))

    mutate_query = """
        mutation UpdateAddress($input: AddressUpdateInput!) {
            address_update(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutate_query, {"input": jsonable_encoder(test_data)}
    )

    posterior_data = await query_data(test_data["uuid"])

    response_data = one(one(posterior_data.data.get("addresses", {})).get("objects"))

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
    update_address.return_value = AddressType(uuid=address_uuid_to_update)

    payload = jsonable_encoder(test_data)

    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"address_update": {"uuid": str(address_uuid_to_update)}}

    update_address.assert_called_with(test_data)
