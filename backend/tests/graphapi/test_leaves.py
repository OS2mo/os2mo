# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from uuid import uuid4

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from ..conftest import GraphAPIPost
from .utils import fetch_class_uuids
from .utils import fetch_engagement_validity


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the leave data model."""
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_leave_integration_test(
    graphapi_post: GraphAPIPost, employee_and_engagement_uuids
) -> None:
    """Test that leave can be created in LoRa via GraphQL."""

    employee = employee_and_engagement_uuids[0]
    engagement = employee["engagement_uuids"][0]

    parent_from, parent_to = fetch_engagement_validity(graphapi_post, engagement)

    start_date = parent_from

    leave_type_uuids = fetch_class_uuids(graphapi_post, "leave_type")

    test_data = {
        "uuid": str(uuid4()),
        "user_key": "leave_key",
        "person": str(employee["uuid"]),
        "engagement": str(engagement),
        "leave_type": str(leave_type_uuids[0]),
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutation = """
        mutation CreateLeave($input: LeaveCreateInput!) {
            leave_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"input": test_data})

    assert response.errors is None
    uuid = UUID(response.data["leave_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            leaves(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
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

    assert obj["user_key"] == test_data["user_key"]
    assert obj["employee"] == test_data["person"]
    assert obj["engagement"] == test_data["engagement"]
    assert obj["leave_type"] == test_data["leave_type"]
    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "user_key": None,
            "engagement": "301a906b-ef51-4d5c-9c77-386fb8410459",
            "leave_type": "ad1b7d09-5452-4bec-9381-e4c876331ac0",
            "person": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "user_key": "v3ry_n1c3_us3r_k3y",
            "engagement": None,
            "leave_type": "ad1b7d09-5452-4bec-9381-e4c876331ac0",
            "person": None,
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "0895b7f5-86ac-45c5-8fb1-c3047d45b643",
            "user_key": "-",
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
                        user_key
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
                        user_key
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

    assert leave_objects_post_update["user_key"] == expected_updated_leave["user_key"]
    assert (
        leave_objects_post_update["leave_type"] == expected_updated_leave["leave_type"]
    )
    assert leave_objects_post_update["person"] == expected_updated_leave["person"]
    assert (
        leave_objects_post_update["engagement"] == expected_updated_leave["engagement"]
    )
    assert leave_objects_post_update["validity"] == expected_updated_leave["validity"]


@pytest.mark.integration_test
@freezegun.freeze_time("2023-07-13", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
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
