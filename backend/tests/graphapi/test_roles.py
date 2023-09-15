# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one
from pytest import MonkeyPatch

from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import RoleCreate
from mora.graphapi.versions.latest.models import RoleUpdate
from mora.util import POSITIVE_INFINITY
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import RoleRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(RoleRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the role data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                roles {
                    objects {
                        uuid
                        objects {
                            uuid
                            user_key
                            employee_uuid
                            org_unit_uuid
                            role_type_uuid
                            type
                            validity {from to}
                        }
                    }
                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["roles"]["objects"]) == test_data


@given(test_input=graph_data_uuids_strat(RoleRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query roles by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    roles(filter: {uuids: $uuids}) {
                        objects {
                            uuid
                        }
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [role.get("uuid") for role in response.data["roles"]["objects"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.create_role", new_callable=AsyncMock)
async def test_create_role_mutation_unit_test(
    create_role: AsyncMock, test_data: RoleCreate
) -> None:
    """Tests that the mutator function for creating a role passes through, with the
    defined pydantic model."""

    mutation = """
        mutation CreateRole($input: RoleCreateInput!) {
            role_create(input: $input) {
                uuid
            }
        }
    """

    create_role.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"role_create": {"uuid": str(test_data.uuid)}}

    create_role.assert_called_with(test_data)


@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_role_integration_test(
    data, graphapi_post, employee_uuids, org_uuids
) -> None:
    """Test that roles can be created in LoRa via GraphQL."""

    # This must be done as to not receive validation errors of the employee upon
    # creating the employee conflicting the dates.
    org_uuid = data.draw(st.sampled_from(org_uuids))
    org_from, org_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=org_from, max_value=org_to or datetime.max)
    )
    if org_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=org_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    role_type = fetch_class_uuids(graphapi_post, "role_type")

    test_data = data.draw(
        st.builds(
            RoleCreate,
            uuid=st.uuids() | st.none(),
            person=st.sampled_from(employee_uuids),
            role_type=st.sampled_from(role_type),
            org_unit=st.just(org_uuid),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutation = """
        mutation CreateRole($input: RoleCreateInput!) {
            role_create(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutation, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuid = UUID(response.data["role_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            roles(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        employee: employee_uuid
                        org_unit: org_unit_uuid
                        role_type: role_type_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    obj = one(one(response.data["roles"]["objects"])["objects"])

    assert UUID(obj["org_unit"]) == test_data.org_unit
    assert UUID(obj["employee"]) == test_data.person
    assert UUID(obj["role_type"]) == test_data.role_type
    assert obj["user_key"] == test_data.user_key or str(uuid)

    assert (
        datetime.fromisoformat(obj["validity"]["from"]).date()
        == test_data.validity.from_date.date()
    )

    # FYI: "backend/mora/util.py::to_iso_date()" does a check for POSITIVE_INFINITY.year
    if (
        not test_data.validity.to_date
        or test_data.validity.to_date.year == POSITIVE_INFINITY.year
    ):
        assert obj["validity"]["to"] is None
    else:
        assert (
            datetime.fromisoformat(obj["validity"]["to"]).date()
            == test_data.validity.to_date.date()
        )


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.update_role", new_callable=AsyncMock)
async def test_update_role_unit_test(
    update_role: AsyncMock, test_data: RoleUpdate
) -> None:
    """Tests that the mutator function for updating a role passes through, with the
    defined pydantic model."""

    mutation = """
        mutation UpdateRole($input: RoleUpdateInput!) {
            role_update(input: $input) {
                uuid
            }
        }
    """

    update_role.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"role_update": {"uuid": str(test_data.uuid)}}

    update_role.assert_called_with(test_data)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "user_key": "random_user_key",
            "role_type": "8ca636d8-d70f-4ce4-992b-4bf4dcfc2559",
            "org_unit": "5942ce50-2be8-476f-914b-6769a888a7c8",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "user_key": None,
            "role_type": "8ca636d8-d70f-4ce4-992b-4bf4dcfc2559",
            "org_unit": "b688513d-11f7-4efc-b679-ab082a2055d0",
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "user_key": "New_cool_user_key",
            "role_type": None,
            "org_unit": None,
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "user_key": None,
            "role_type": "8ca636d8-d70f-4ce4-992b-4bf4dcfc2559",
            "org_unit": None,
            "validity": {"from": "2023-07-10T00:00:00+02:00", "to": None},
        },
    ],
)
async def test_update_role_integration_test(test_data, graphapi_post) -> None:
    """Test that roles can be updated in LoRa via GraphQL."""

    uuid = test_data["uuid"]

    query = """
        query RoleQuery($uuid: UUID!) {
            roles(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        user_key
                        role_type: role_type_uuid
                        org_unit: org_unit_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(query, {"uuid": str(uuid)})

    assert response.errors is None

    pre_update_role = one(one(response.data["roles"]["objects"])["objects"])

    mutation = """
        mutation UpdateRole($input: RoleUpdateInput!) {
            role_update(input: $input) {
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
            roles(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        user_key
                        role_type: role_type_uuid
                        org_unit: org_unit_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    verify_response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None

    role_objects_post_update = one(
        one(verify_response.data["roles"]["objects"])["objects"]
    )

    expected_updated_role = {k: v or pre_update_role[k] for k, v in test_data.items()}

    assert expected_updated_role == role_objects_post_update


@pytest.mark.integration_test
@freezegun.freeze_time("2023-07-13", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "to": "2023-07-25T00:00:00+02:00",
        },
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "to": "2040-01-01T00:00:00+01:00",
        },
    ],
)
async def test_role_terminate_integration(test_data, graphapi_post) -> None:
    uuid = test_data["uuid"]
    mutation = """
        mutation TerminateRole($input: RoleTerminateInput!) {
            role_terminate(input: $input) {
                uuid
            }
        }
    """
    mutation_response: GQLResponse = graphapi_post(
        mutation, {"input": jsonable_encoder(test_data)}
    )

    assert mutation_response.errors is None

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            roles(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        validity {
                            to
                        }
                    }
                }
            }
        }
    """

    verify_response: GQLResponse = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None
    role_objects_post_terminate = one(
        one(verify_response.data["roles"]["objects"])["objects"]
    )
    assert test_data["uuid"] == role_objects_post_terminate["uuid"]
    assert test_data["to"] == role_objects_post_terminate["validity"]["to"]
