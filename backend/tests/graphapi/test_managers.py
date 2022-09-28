# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from _datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID

import pytest
from fastapi.encoders import jsonable_encoder

from hypothesis import given
from hypothesis import infer
from hypothesis import strategies as st
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import ManagerCreate
from mora.graphapi.versions.latest.types import ManagerType
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
@pytest.mark.usefixtures("sample_structures_no_reset")
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
async def test_create_manager_mutation(
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
    data,
    graphapi_post,
) -> None:
    """Test that managers can be created in LoRa via GraphQL."""

    test_data = data.draw(
        st.builds(
            ManagerCreate,
            responsibility=infer,
            org_unit=st.just(UUID("68c5d78e-ae26-441f-a143-0103eca8b62a")),
            org_unit_level=infer,
            org_unit_type=infer,
            time_planning=infer,
            org=st.just(UUID("456362c4-0ee4-4e5e-a72c-751239745e62")),
            manager_type=st.just(UUID("a22f8575-89b4-480b-a7ba-b3f1372e25a4")),
            manager_level=st.just(UUID("d56f174d-c45d-4b55-bdc6-c57bf68238b9")),
            validity=infer,
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
            managers(uuids: [$uuid]) {
                objects {
                    responsibilities: responsibility_uuids
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

    assert UUID(obj["manager_type"]) == test_data.manager_type
    assert UUID(obj["manager_level"]) == test_data.manager_level

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
