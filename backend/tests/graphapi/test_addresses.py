# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora import lora
from mora import mapping
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.address import terminate as terminate_addr
from mora.graphapi.versions.latest.models import AddressCreate
from mora.graphapi.versions.latest.models import AddressTerminate
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


# --------------------------------------------------------------------------------------
# CREATE tests
# --------------------------------------------------------------------------------------

# Address UUID: Nordre Ringgade 1, 8000 Aarhus C
addr_uuid_nordre_ring = "b1f1817d-5f02-4331-b8b3-97330a5d3197"

addr_type_user_email = UUID("c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0")
addr_type_user_address = UUID("4e337d8e-1fd2-4449-8110-e0c8a22958ed")
addr_type_user_phone = UUID("cbadfa0f-ce4f-40b9-86a0-2e85d8961f5d")
addr_type_orgunit_address = UUID("28d71012-2919-4b67-a2f0-7b59ed52561e")
addr_type_orgunit_email = UUID("73360db1-bad3-4167-ac73-8d827c0c8751")
addr_type_orgunit_ean = UUID("e34d4426-9845-4c72-b31e-709be85d6fa2")  # regex: ^\d{13}$
addr_type_orgunit_phone = UUID("1d1d3711-5af4-4084-99b3-df2b8752fdec")
addr_type_orgunit_openhours = UUID("e8ea1a09-d3d4-4203-bfe9-d9a2da100f3b")

engagement_type_employee = UUID("06f95678-166a-455a-a2ab-121a8d92ea23")

visibility_uuid_public = UUID("f63ad763-0e53-4972-a6a9-63b42a0f8cb7")


@given(data=st.data())
async def test_create_mutator(data):
    # Create test data
    dt_options = {
        "min_value": datetime.datetime(1930, 1, 1, 1),
        "timezones": st.just(ZoneInfo("Europe/Copenhagen")),
    }
    validity_tuple = data.draw(
        st.tuples(
            st.datetimes(**dt_options),
            st.datetimes(**dt_options) | st.none(),
        ).filter(lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True)
    )
    test_data_from, test_data_to = validity_tuple

    test_data = data.draw(
        st.builds(
            AddressCreate,
            from_date=st.just(test_data_from),
            to_date=st.just(test_data_to),
            type=st.sampled_from(
                [mapping.ORG_UNIT, mapping.PERSON, mapping.ENGAGEMENT]
            ),
        )
    )
    payload = jsonable_encoder(test_data.dict(by_alias=True))

    # Execute the mutation query
    with patch(
        "mora.graphapi.versions.latest.address.AddressRequestHandler.construct"
    ) as mock_construct, patch(
        "mora.graphapi.versions.latest.models.lora.Scope.get"
    ), patch(
        "mora.graphapi.versions.latest.models.AddressCreate._get_lora_validity"
    ) as mock_get_lora_validity, patch(
        "mora.graphapi.versions.latest.models.get_configured_organisation"
    ) as mock_get_configured_organisation:
        new_uuid = uuid4()
        mock_construct.return_value = AsyncMock(submit=AsyncMock(return_value=new_uuid))

        mock_get_lora_validity.return_value = {
            mapping.FROM: test_data_from,
            mapping.TO: None,
        }
        mock_get_configured_organisation.return_value = {
            mapping.UUID: "456362c4-0ee4-4e5e-a72c-751239745e62"
        }

        mutate_query = """
            mutation($input: AddressCreateInput!) {
                address_create(input: $input) {
                    uuid
                }
            }
        """
        mutation_response = await execute_graphql(
            query=mutate_query, variable_values={"input": payload}
        )
        assert mutation_response.errors is None

        mutation_response_uuid = mutation_response.data.get("address_create", {}).get(
            "uuid", None
        )
        assert str(new_uuid) == mutation_response_uuid


@pytest.mark.parametrize(
    "given_mutator_args",
    [
        {
            "from_date": datetime.datetime.combine(
                datetime.datetime.now().date(), datetime.datetime.min.time()
            ).replace(tzinfo=ZoneInfo("Europe/Copenhagen")),
            "to_date": datetime.datetime.combine(
                datetime.datetime.now().date(), datetime.datetime.min.time()
            ).replace(tzinfo=ZoneInfo("Europe/Copenhagen"))
            - datetime.timedelta(days=1),
            "value": "YeeHaaamagenta.dk",
            "address_type": UUID("c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"),
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.PERSON,
                "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            },
        },
        {
            "from_date": datetime.datetime.combine(
                datetime.datetime.now().date(), datetime.datetime.min.time()
            ).replace(tzinfo=ZoneInfo("Europe/Copenhagen")),
            "to_date": None,
            "value": "YeeHaaamagenta.dk",
            "address_type": UUID("c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"),
            "visibility": visibility_uuid_public,
            "relation": {
                "type": "some-random-type",
                "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            },
        },
    ],
)
async def test_create_mutator_fails(given_mutator_args):
    # Create payload directly, instead of newing the model,
    # Oterwise the model will come with validation errors on instantiations.
    payload = {
        "from": given_mutator_args["from_date"].isoformat(),
        "to": given_mutator_args["to_date"].isoformat()
        if given_mutator_args.get("to_date", None)
        else None,
        "value": given_mutator_args["value"],
        "address_type": str(given_mutator_args["address_type"]),
        "visibility": str(given_mutator_args["visibility"]),
        "type": given_mutator_args["relation"]["type"],
        "relation_uuid": str(given_mutator_args["relation"]["uuid"]),
    }

    with patch(
        "mora.graphapi.versions.latest.address.AddressRequestHandler.construct"
    ) as mock_construct, patch(
        "mora.graphapi.versions.latest.models.lora.Scope.get"
    ), patch(
        "mora.graphapi.versions.latest.models.AddressCreate._get_lora_validity"
    ) as mock_get_lora_validity, patch(
        "mora.graphapi.versions.latest.models.get_configured_organisation"
    ) as mock_get_configured_organisation:
        new_uuid = uuid4()
        mock_construct.return_value = AsyncMock(submit=AsyncMock(return_value=new_uuid))

        mock_get_lora_validity.return_value = {
            mapping.FROM: given_mutator_args["from_date"],
            mapping.TO: None,
        }
        mock_get_configured_organisation.return_value = {
            mapping.UUID: "456362c4-0ee4-4e5e-a72c-751239745e62"
        }

        mutate_query = """
                    mutation($input: AddressCreateInput!) {
                        address_create(input: $input) {
                            uuid
                        }
                    }
                """

        _ = await execute_graphql(
            query=mutate_query, variable_values={"input": payload}
        )

        mock_construct.assert_not_called()


@pytest.mark.parametrize(
    "given_mutator_args",
    [
        {
            "value": "YeeHaaa@magenta.dk",
            "address_type": addr_type_user_email,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.PERSON,
                "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": addr_uuid_nordre_ring,
            "address_type": addr_type_user_address,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.PERSON,
                "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": "11223344",
            "address_type": addr_type_user_phone,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.PERSON,
                "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": "YeeHaaa@magenta.dk",
            "address_type": addr_type_user_email,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.ENGAGEMENT,
                "uuid": engagement_type_employee,
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": addr_uuid_nordre_ring,
            "address_type": addr_type_orgunit_address,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.ORG_UNIT,
                "uuid": UUID("2874e1dc-85e6-4269-823a-e1125484dfd3"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": "YeeHaaa@magenta.dk",
            "address_type": addr_type_orgunit_email,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.ORG_UNIT,
                "uuid": UUID("2874e1dc-85e6-4269-823a-e1125484dfd3"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": "8008580085000",
            "address_type": addr_type_orgunit_ean,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.ORG_UNIT,
                "uuid": UUID("2874e1dc-85e6-4269-823a-e1125484dfd3"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": "55667788",
            "address_type": addr_type_orgunit_phone,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.ORG_UNIT,
                "uuid": UUID("2874e1dc-85e6-4269-823a-e1125484dfd3"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": "8-17",
            "address_type": addr_type_orgunit_openhours,
            "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.ORG_UNIT,
                "uuid": UUID("2874e1dc-85e6-4269-823a-e1125484dfd3"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
        {
            "value": "YeeHaaa@magenta.dk",
            "address_type": addr_type_user_email,
            # "visibility": visibility_uuid_public,
            "relation": {
                "type": mapping.PERSON,
                "uuid": UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a"),
            },
            "org": UUID("456362c4-0ee4-4e5e-a72c-751239745e62"),
        },
    ],
)
@pytest.mark.integration_test
@pytest.mark.usefixtures("sample_structures")
async def test_create_integration(graphapi_post, given_mutator_args):
    validity_from = datetime.datetime.combine(
        datetime.datetime.now().date(), datetime.datetime.min.time()
    ).replace(tzinfo=ZoneInfo("Europe/Copenhagen"))

    test_data = AddressCreate(
        from_date=validity_from,
        value=given_mutator_args["value"],
        address_type=given_mutator_args["address_type"],
        visibility=given_mutator_args.get("visibility", None),
        type=given_mutator_args["relation"]["type"],
        relation_uuid=given_mutator_args["relation"]["uuid"],
    )
    payload = jsonable_encoder(test_data.dict(by_alias=True))

    # Execute the mutation query
    mutation_query = """
        mutation($input: AddressCreateInput!) {
            address_create(input: $input) {
                uuid
            }
        }
    """
    mutation_response: GQLResponse = graphapi_post(mutation_query, {"input": payload})
    assert mutation_response.errors is None

    mutation_response_uuid = mutation_response.data.get("address_create", {}).get(
        "uuid", None
    )
    assert mutation_response_uuid is not None

    # Verify/assert the new address was created
    verify_query = _get_address_query()
    verify_response: GQLResponse = graphapi_post(
        verify_query,
        {mapping.UUID: mutation_response_uuid},
    )
    assert verify_response.errors is None

    new_addr = one(one(verify_response.data["addresses"])["objects"])
    assert new_addr is not None
    assert new_addr[mapping.UUID] is not None
    assert new_addr[mapping.VALUE] == test_data.value
    assert new_addr[mapping.ADDRESS_TYPE][mapping.UUID] == str(test_data.address_type)

    new_addr_visibility = (
        new_addr[mapping.VISIBILITY][mapping.UUID]
        if new_addr[mapping.VISIBILITY]
        else None
    )
    test_addr_visibility_uuid_str = (
        str(test_data.visibility) if test_data.visibility else None
    )
    assert new_addr_visibility == test_addr_visibility_uuid_str

    rel_uuid_str = str(test_data.relation_uuid)
    if test_data.type == mapping.PERSON:
        assert one(new_addr[mapping.EMPLOYEE])[mapping.UUID] == rel_uuid_str
    elif test_data.type == mapping.ORG_UNIT:
        assert one(new_addr[mapping.ORG_UNIT])[mapping.UUID] == rel_uuid_str
    elif test_data.type == mapping.ENGAGEMENT:
        assert new_addr["engagement_uuid"] == rel_uuid_str


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


def _get_address_query():
    return """
        query VerifyQuery($uuid: UUID!) {
          addresses(uuids: [$uuid], from_date: null, to_date: null) {
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
    """
