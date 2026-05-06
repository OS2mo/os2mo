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
from .utils import fetch_org_unit_validity


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the rolebinding data model."""
    query = """
        query {
            rolebindings {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        org_unit { uuid }
                        ituser { uuid }
                        role { uuid }
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
async def test_create_rolebinding_integration_test(
    graphapi_post: GraphAPIPost, ituser_uuids, org_uuids
) -> None:
    """Test that roles can be created in LoRa via GraphQL."""

    # This must be done as to not receive validation errors of the employee upon
    # creating the employee conflicting the dates.
    org_uuid = org_uuids[0]
    org_from, org_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    ituser_uuid = ituser_uuids[0]

    start_date = org_from

    role_type = fetch_class_uuids(graphapi_post, "role")

    test_data = {
        "uuid": str(uuid4()),
        "user_key": "asd123",
        "ituser": str(ituser_uuid),
        "role": str(role_type[0]),
        "org_unit": str(org_uuid),
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutation = """
        mutation CreateRolebinding($input: RoleBindingCreateInput!) {
            rolebinding_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"input": test_data})
    assert response.errors is None
    uuid = UUID(response.data["rolebinding_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            rolebindings(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        ituser { uuid }
                        org_unit { uuid }
                        role { uuid }
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
    assert response.data is not None
    obj = one(one(response.data["rolebindings"]["objects"])["objects"])

    assert one(obj["org_unit"])["uuid"] == test_data["org_unit"]
    assert one(obj["ituser"])["uuid"] == test_data["ituser"]
    assert one(obj["role"])["uuid"] == test_data["role"]
    assert obj["user_key"] == test_data["user_key"]
    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "ituser": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "user_key": "random_user_key",
            "role": "8ca636d8-d70f-4ce4-992b-4bf4dcfc2559",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "ituser": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "user_key": None,
            "role": "8ca636d8-d70f-4ce4-992b-4bf4dcfc2559",
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "ituser": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "user_key": None,
            "role": "8ca636d8-d70f-4ce4-992b-4bf4dcfc2559",
            "validity": {"from": "2023-07-10T00:00:00+02:00", "to": None},
        },
        {
            "uuid": "1b20d0b9-96a0-42a6-b196-293bb86e62e8",
            "ituser": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "user_key": "New_cool_user_key",
            "role": "8ca636d8-d70f-4ce4-992b-4bf4dcfc2559",
            "validity": {"from": "2023-01-01T00:00:00+01:00", "to": None},
        },
    ],
)
async def test_update_role_integration_test(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    """Test that roles can be updated in LoRa via GraphQL."""

    uuid = test_data["uuid"]

    query = """
        query RoleQuery($uuid: UUID!) {
            rolebindings(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        user_key
                        ituser { uuid }
                        role { uuid }
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

    pre_update_role = one(one(response.data["rolebindings"]["objects"])["objects"])

    mutation = """
        mutation UpdateRolebinding($input: RoleBindingUpdateInput!) {
            rolebinding_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    # Writing verify query to retrieve objects containing data on the desired uuids.
    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            rolebindings(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        user_key
                        role { uuid }
                        ituser { uuid }
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

    role_objects_post_update = one(
        one(verify_response.data["rolebindings"]["objects"])["objects"]
    )

    assert role_objects_post_update["uuid"] == test_data["uuid"]
    assert (
        role_objects_post_update["user_key"] == test_data["user_key"]
        or pre_update_role["user_key"]
    )
    assert role_objects_post_update["role"] == [{"uuid": test_data["role"]}]
    assert role_objects_post_update["ituser"] == [{"uuid": test_data["ituser"]}]
    assert role_objects_post_update["validity"] == test_data["validity"]


@pytest.mark.integration_test
@freezegun.freeze_time("2023-07-13", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
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
async def test_role_terminate_integration(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    uuid = test_data["uuid"]
    mutation = """
        mutation TerminateRolebinding($input: RoleBindingTerminateInput!) {
            rolebinding_terminate(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            rolebindings(filter: {uuids: [$uuid]}){
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
    role_objects_post_terminate = one(
        one(verify_response.data["rolebindings"]["objects"])["objects"]
    )
    assert test_data["uuid"] == role_objects_post_terminate["uuid"]
    assert test_data["to"] == role_objects_post_terminate["validity"]["to"]
