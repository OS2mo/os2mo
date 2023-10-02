# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime as dt
from datetime import datetime
from unittest import mock
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

from ..conftest import GraphAPIPost
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from .utils import fetch_class_uuids
from .utils import fetch_engagement_validity
from mora import lora
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.leave import terminate_leave
from mora.graphapi.versions.latest.models import LeaveCreate
from mora.graphapi.versions.latest.models import LeaveTerminate
from mora.graphapi.versions.latest.models import LeaveUpdate
from mora.util import POSITIVE_INFINITY
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import LeaveRead


@given(test_data=graph_data_strat(LeaveRead))
def test_query_all(test_data, graphapi_post: GraphAPIPost, patch_loader):
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
        response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["leaves"]["objects"]) == test_data


@given(test_input=graph_data_uuids_strat(LeaveRead))
def test_query_by_uuid(test_input, graphapi_post: GraphAPIPost, patch_loader):
    """Test that we can query leaves by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    leaves(filter: {uuids: $uuids}) {
                        objects {
                            uuid
                        }
                    }
                }
            """
        response = graphapi_post(query, {"uuids": test_uuids})

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
    data, graphapi_post: GraphAPIPost, employee_and_engagement_uuids
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
    response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert response.errors is None
    uuid = UUID(response.data["leave_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            leaves(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
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

    response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    obj = one(one(response.data["leaves"]["objects"])["objects"])

    assert UUID(obj["employee"]) == test_data.person
    assert UUID(obj["engagement"]) == test_data.engagement
    assert UUID(obj["leave_type"]) == test_data.leave_type

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
@patch("mora.graphapi.versions.latest.mutators.update_leave", new_callable=AsyncMock)
async def test_update_leave_unit_test(
    update_leave: AsyncMock, test_data: LeaveUpdate
) -> None:
    """Tests that the mutator function for updating a leave passes through, with the
    defined pydantic model."""

    mutation = """
        mutation UpdateLeave($input: LeaveUpdateInput!) {
            leave_update(input: $input) {
                uuid
            }
        }
    """

    update_leave.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"leave_update": {"uuid": str(test_data.uuid)}}

    update_leave.assert_called_with(test_data)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "engagement": "301a906b-ef51-4d5c-9c77-386fb8410459",
            "leave_type": "ad1b7d09-5452-4bec-9381-e4c876331ac0",
            "person": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "engagement": None,
            "leave_type": "ad1b7d09-5452-4bec-9381-e4c876331ac0",
            "person": None,
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "engagement": "301a906b-ef51-4d5c-9c77-386fb8410459",
            "leave_type": None,
            "person": None,
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
    ],
)
async def test_update_leave_integration_test(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    """Test that leaves can be updated in LoRa via GraphQL."""

    uuid = test_data["uuid"]

    query = """
        query LeaveQuery($uuid: UUID!) {
            leaves(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        leave_type: leave_type_uuid
                        person: employee_uuid
                        engagement: engagement_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, {"uuid": str(uuid)})

    assert response.errors is None

    pre_update_leave = one(one(response.data["leaves"]["objects"])["objects"])

    mutation = """
        mutation UpdateLeave($input: LeaveUpdateInput!) {
            leave_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    # Writing verify query to retrieve objects containing data on the desired uuids.
    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            leaves(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        leave_type: leave_type_uuid
                        person: employee_uuid
                        engagement: engagement_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    verify_response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None

    leave_objects_post_update = one(
        one(verify_response.data["leaves"]["objects"])["objects"]
    )

    expected_updated_leave = {k: v or pre_update_leave[k] for k, v in test_data.items()}

    assert (
        leave_objects_post_update["leave_type"] == expected_updated_leave["leave_type"]
    )
    assert leave_objects_post_update["person"] == expected_updated_leave["person"]
    assert (
        leave_objects_post_update["engagement"] == expected_updated_leave["engagement"]
    )
    assert leave_objects_post_update["validity"] == expected_updated_leave["validity"]


@given(
    given_uuid=st.uuids(),
    given_validity_dts=st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
async def test_leave_terminate_unit(given_uuid, given_validity_dts):
    # Around 80% of test-runs ends in `caught_exception` which equals a skip.
    # This "template" is used on quite a few models and doesn't seem to provide
    # reliable tests.
    from_date, to_date = given_validity_dts

    # The terminate logic have a check that verifies we don't use times other than:
    # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
    # expect an exception.
    expect_exception = False
    if to_date.time() != dt.time.min:
        expect_exception = True

    test_data = LeaveTerminate(
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
            terminate_result_uuid = await terminate_leave(input=test_data)
        except Exception as e:
            caught_exception = e

    # Assert
    if not expect_exception:
        assert terminate_result_uuid == test_data.uuid
    else:
        assert caught_exception is not None


@pytest.mark.integration_test
@freezegun.freeze_time("2023-07-13", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "to": "2023-07-25T00:00:00+02:00",
        },
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "to": "2040-01-01T00:00:00+01:00",
        },
    ],
)
async def test_leave_terminate_integration(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    uuid = test_data["uuid"]
    mutation = """
        mutation TerminateLeave($input: LeaveTerminateInput!) {
            leave_terminate(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            leaves(filter: {uuids: [$uuid]}){
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

    verify_response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None
    leave_objects_post_terminate = one(
        one(verify_response.data["leaves"]["objects"])["objects"]
    )
    assert test_data["uuid"] == leave_objects_post_terminate["uuid"]
    assert test_data["to"] == leave_objects_post_terminate["validity"]["to"]
