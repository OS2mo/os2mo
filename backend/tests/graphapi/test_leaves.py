# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from _datetime import datetime
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
from .utils import fetch_engagement_validity
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import LeaveCreate
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import LeaveRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(LeaveRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the leave data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                leaves {
                    objects {
                        uuid
                        objects {
                            uuid
                            user_key
                            employee_uuid
                            engagement_uuid
                            leave_type_uuid
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
    assert flatten_data(response.data["leaves"]["objects"]) == test_data


@given(test_input=graph_data_uuids_strat(LeaveRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query leaves by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    leaves(uuids: $uuids) {
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
    result_uuids = [leave.get("uuid") for leave in response.data["leaves"]["objects"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.create_leave", new_callable=AsyncMock)
async def test_create_leave_mutation_unit_test(
    create_leave: AsyncMock, test_data: LeaveCreate
) -> None:
    """Tests that the mutator function for creating a leave passes through,
    with the defined pydantic model."""

    mutation = """
        mutation CreateLeave($input: LeaveCreateInput!) {
            leave_create(input: $input) {
                uuid
            }
        }
    """

    create_leave.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"leave_create": {"uuid": str(test_data.uuid)}}

    create_leave.assert_called_with(test_data)


@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_leave_integration_test(
    data, graphapi_post, employee_and_engagement_uuids
) -> None:
    """Test that leave can be created in LoRa via GraphQL."""

    employee = data.draw(st.sampled_from(employee_and_engagement_uuids))
    engagement = data.draw(st.sampled_from(employee["engagement_uuids"]))

    parent_from, parent_to = fetch_engagement_validity(graphapi_post, engagement)

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

    leave_type_uuids = fetch_class_uuids(graphapi_post, "leave_type")

    test_data = data.draw(
        st.builds(
            LeaveCreate,
            uuid=st.uuids() | st.none(),
            person=st.just(employee["uuid"]),
            engagement=st.just(engagement),
            leave_type=st.sampled_from(leave_type_uuids),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutation = """
        mutation CreateLeave($input: LeaveCreateInput!) {
            leave_create(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutation, {"input": jsonable_encoder(test_data)}
    )

    assert response.errors is None
    uuid = UUID(response.data["leave_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            leaves(uuids: [$uuid], from_date: null, to_date: null) {
                objects {
                    objects {
                        employee: employee_uuid
                        engagement: engagement_uuid
                        leave_type: leave_type_uuid
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
    obj = one(one(response.data["leaves"]["objects"])["objects"])

    assert UUID(obj["employee"]) == test_data.person
    assert UUID(obj["engagement"]) == test_data.engagement
    assert UUID(obj["leave_type"]) == test_data.leave_type

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
