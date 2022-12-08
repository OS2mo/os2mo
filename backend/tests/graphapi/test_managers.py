# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import datetime as dt
from _datetime import datetime
from unittest import mock
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from .utils import fetch_class_uuids
from .utils import fetch_employee_validity
from mora import lora
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.manager import terminate_manager
from mora.graphapi.versions.latest.models import ManagerCreate
from mora.graphapi.versions.latest.models import ManagerTerminate
from mora.graphapi.versions.latest.models import ManagerUpdate
from mora.graphapi.versions.latest.types import ManagerType
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import ManagerRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(ManagerRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the manager data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                managers {
                    uuid
                    objects {
                        uuid
                        user_key
                        employee_uuid
                        manager_level_uuid
                        manager_type_uuid
                        org_unit_uuid
                        responsibility_uuids
                        type
                        validity {from to}
                    }
                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["managers"]) == test_data


@given(test_input=graph_data_uuids_strat(ManagerRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query managers by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    managers(uuids: $uuids) {
                        uuid
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [manager.get("uuid") for manager in response.data["managers"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_class_reset")
@pytest.mark.parametrize(
    "filter_snippet,expected",
    [
        ("", 1),
        # Employee filters
        ('(employees: "53181ed2-f1de-4c4a-a8fd-ab358c2c454a")', 1),
        ('(employees: "6ee24785-ee9a-4502-81c2-7697009c9053")', 0),
        (
            """
            (employees: [
                "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "6ee24785-ee9a-4502-81c2-7697009c9053"
            ])
        """,
            1,
        ),
        # Organisation Unit filter
        ('(org_units: "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e")', 1),
        ('(org_units: "2874e1dc-85e6-4269-823a-e1125484dfd3")', 0),
        (
            """
            (org_units: [
                "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
            ])
        """,
            1,
        ),
        # Mixed filters
        (
            """
            (
                employees: "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                org_units: "2874e1dc-85e6-4269-823a-e1125484dfd3"
            )
        """,
            0,
        ),
        (
            """
            (
                employees: "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                org_units: "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
            )
        """,
            1,
        ),
    ],
)
async def test_manager_employees_filters(
    graphapi_post, filter_snippet, expected
) -> None:
    """Test filters on managers."""
    manager_query = f"""
        query Managers {{
            managers{filter_snippet} {{
                uuid
            }}
        }}
    """
    response: GQLResponse = graphapi_post(manager_query)
    assert response.errors is None
    assert len(response.data["managers"]) == expected


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.create_manager", new_callable=AsyncMock)
async def test_create_manager_mutation_unit_test(
    create_manager: AsyncMock, test_data: ManagerCreate
) -> None:
    """Tests that the mutator function for creating a manager passes through, with the
    defined pydantic model."""

    mutation = """
        mutation CreateManager($input: ManagerCreateInput!) {
            manager_create(input: $input) {
                uuid
            }
        }
    """

    create_manager.return_value = ManagerType(uuid=test_data.uuid)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"manager_create": {"uuid": str(test_data.uuid)}}

    create_manager.assert_called_with(test_data)


@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_manager_integration_test(
    data, graphapi_post, employee_uuids, org_uuids
) -> None:
    """Test that managers can be created in LoRa via GraphQL."""

    # This must be done as to not receive validation errors of the employee upon
    # creating the employee conflicting the dates.
    employee_uuid = data.draw(st.sampled_from(employee_uuids))
    parent_from, parent_to = fetch_employee_validity(graphapi_post, employee_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=parent_from, max_value=parent_to or datetime.max)
    )
    if parent_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=parent_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    manager_level_uuids = fetch_class_uuids(graphapi_post, "manager_level")
    manager_type_uuids = fetch_class_uuids(graphapi_post, "manager_type")
    responsibility_uuids = fetch_class_uuids(graphapi_post, "responsibility")

    test_data = data.draw(
        st.builds(
            ManagerCreate,
            person=st.just(employee_uuid),
            responsibility=st.just(responsibility_uuids),
            org_unit=st.sampled_from(org_uuids),
            manager_type=st.sampled_from(manager_type_uuids),
            manager_level=st.sampled_from(manager_level_uuids),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutation = """
        mutation CreateManager($input: ManagerCreateInput!) {
            manager_create(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutation, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuid = UUID(response.data["manager_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            managers(uuids: [$uuid], from_date: null, to_date: null) {
                objects {
                    user_key
                    type
                    employee: employee_uuid
                    responsibility: responsibility_uuids
                    org_unit: org_unit_uuid
                    manager_type: manager_type_uuid
                    manager_level: manager_level_uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    obj = one(one(response.data["managers"])["objects"])

    assert obj["type"] == test_data.type_
    responsibility_list = [
        UUID(responsibility) for responsibility in obj["responsibility"]
    ]

    assert responsibility_list == test_data.responsibility
    assert UUID(obj["org_unit"]) == test_data.org_unit
    assert UUID(obj["employee"]) == test_data.person
    assert UUID(obj["manager_type"]) == test_data.manager_type
    assert UUID(obj["manager_level"]) == test_data.manager_level
    assert obj["user_key"] == test_data.user_key or str(uuid)

    assert (
        datetime.fromisoformat(obj["validity"]["from"]).date()
        == test_data.validity.from_date.date()
    )
    if obj["validity"]["to"] is not None:
        assert (
            datetime.fromisoformat(obj["validity"]["to"]).date()
            == test_data.validity.to_date.date()
        )
    else:
        assert test_data.validity.to_date is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": None,
            "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "responsibility": None,
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "manager_level": None,
            "manager_type": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": None,
            "person": None,
            "responsibility": None,
            "org_unit": None,
            "manager_type": None,
            # This is a known issue: if "manager_level" is set to None, the
            # "responsibility" field may NOT be updated. If manager_level is set to be
            # updated, the "responsibility" field may NOT be set to None. In other
            # words: if "manager_level" is to be updated, then "responsibility" is also
            # expected to be updated, and if "manager_level" is not set to be updated,
            # then neither may "responsibility" be updated.
            "manager_level": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": None,
            "person": None,
            "responsibility": ["93ea44f9-127c-4465-a34c-77d149e3e928"],
            "org_unit": None,
            "manager_level": "ca76a441-6226-404f-88a9-31e02e420e52",
            "manager_type": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": "-",
            "person": None,
            "responsibility": None,
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "manager_level": None,
            "manager_type": "a22f8575-89b4-480b-a7ba-b3f1372e25a4",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": "-",
            "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "responsibility": [
                "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                "452e1dd0-658b-477a-8dd8-efba105c06d6",
                "93ea44f9-127c-4465-a34c-77d149e3e928",
            ],
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "manager_level": "d56f174d-c45d-4b55-bdc6-c57bf68238b9",
            "manager_type": "a22f8575-89b4-480b-a7ba-b3f1372e25a4",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
    ],
)
async def test_update_manager_integration_test(test_data, graphapi_post) -> None:
    """Test that managers can be updated in LoRa via GraphQL."""

    uuid = test_data["uuid"]

    query = """
        query MyQuery($uuid: UUID!) {
            managers(uuids: [$uuid]) {
                objects {
                    uuid
                    user_key
                    person: employee_uuid
                    responsibility: responsibility_uuids
                    org_unit: org_unit_uuid
                    manager_type: manager_type_uuid
                    manager_level: manager_level_uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(query, {"uuid": str(uuid)})
    assert response.errors is None

    pre_update_manager = one(one(response.data["managers"])["objects"])

    mutation = """
        mutation UpdateManager($input: ManagerUpdateInput!) {
            manager_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response: GQLResponse = graphapi_post(
        mutation, {"input": jsonable_encoder(test_data)}
    )

    assert mutation_response.errors is None

    # Writing verify query to retrieve objects containing data on the desired uuids.
    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            managers(uuids: [$uuid]){
                objects {
                    uuid
                    user_key
                    person: employee_uuid
                    responsibility: responsibility_uuids
                    org_unit: org_unit_uuid
                    manager_type: manager_type_uuid
                    manager_level: manager_level_uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    verify_response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None

    manager_objects_post_update = one(one(verify_response.data["managers"])["objects"])

    expected_updated_manager = {
        k: v or pre_update_manager[k] for k, v in test_data.items()
    }
    assert manager_objects_post_update == expected_updated_manager


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.update_manager", new_callable=AsyncMock)
async def test_update_manager_mutation_unit_test(
    update_manager: AsyncMock, test_data: ManagerUpdate
) -> None:
    """Tests that the mutator function for updating a manager passes through, with the
    defined pydantic model."""

    mutation = """
        mutation UpdateManager($input: ManagerUpdateInput!) {
            manager_update(input: $input) {
                uuid
            }
        }
    """

    update_manager.return_value = ManagerType(uuid=test_data.uuid)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"manager_update": {"uuid": str(test_data.uuid)}}

    update_manager.assert_called_with(test_data)


@given(
    given_uuid=st.uuids(),
    given_validity_dts=st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
async def test_manager_terminate(given_uuid, given_validity_dts):
    from_date, to_date = given_validity_dts

    # The terminate logic have a check that verifies we don't use times other than:
    # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
    # expect an exception.
    expect_exception = False
    if to_date.time() != dt.time.min:
        expect_exception = True

    test_data = ManagerTerminate(
        uuid=given_uuid,
        from_date=from_date,
        to_date=to_date,
    )

    # Patching / Mocking
    async def mock_update(*args):
        return args[-1]

    terminate_result_uuid = None
    caught_exception = None

    with mock.patch.object(lora.Scope, "update", new=mock_update):
        try:
            tr = await terminate_manager(input=test_data)
            terminate_result_uuid = tr.uuid if tr else terminate_result_uuid
        except Exception as e:
            caught_exception = e

    # Assert
    if not expect_exception:
        assert terminate_result_uuid == test_data.uuid
    else:
        assert caught_exception is not None
