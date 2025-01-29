# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from mora.graphapi.gmodels.mo import Validity as RAValidity
from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.models import RoleBindingCreate
from mora.graphapi.versions.latest.models import RoleBindingUpdate
from mora.util import POSITIVE_INFINITY
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


@given(test_data=...)
@patch(
    "mora.graphapi.versions.latest.mutators.create_rolebinding", new_callable=AsyncMock
)
async def test_create_role_mutation_unit_test(
    create_rolebinding: AsyncMock, test_data: RoleBindingCreate
) -> None:
    """Tests that the mutator function for creating a role passes through, with the
    defined pydantic model."""

    mutation = """
        mutation CreateRolebinding($input: RoleBindingCreateInput!) {
            rolebinding_create(input: $input) {
                uuid
            }
        }
    """

    create_rolebinding.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"rolebinding_create": {"uuid": str(test_data.uuid)}}

    create_rolebinding.assert_called_with(test_data)


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_rolebinding_integration_test(
    data, graphapi_post: GraphAPIPost, ituser_uuids, org_uuids
) -> None:
    """Test that roles can be created in LoRa via GraphQL."""

    # This must be done as to not receive validation errors of the employee upon
    # creating the employee conflicting the dates.
    org_uuid = data.draw(st.sampled_from(org_uuids))
    org_from, org_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    ituser_uuid = data.draw(st.sampled_from(ituser_uuids))

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

    role_type = fetch_class_uuids(graphapi_post, "role")

    test_data = data.draw(
        st.builds(
            RoleBindingCreate,
            uuid=st.uuids() | st.none(),
            ituser=st.just(ituser_uuid),
            role=st.sampled_from(role_type),
            org_unit=st.just(org_uuid),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutation = """
        mutation CreateRolebinding($input: RoleBindingCreateInput!) {
            rolebinding_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})
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
    obj = one(one(response.data["rolebindings"]["objects"])["objects"])

    assert UUID(one(obj["org_unit"])["uuid"]) == test_data.org_unit
    assert UUID(one(obj["ituser"])["uuid"]) == test_data.ituser
    assert UUID(one(obj["role"])["uuid"]) == test_data.role
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


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_multiple_rolebindings_integration_test(
    data, graphapi_post: GraphAPIPost, ituser_uuids, org_uuids
) -> None:
    """Test that multiple rolebindings can be created using the list mutator."""

    # This must be done as to not receive validation errors of the employee upon
    # creating the employee conflicting the dates.
    org_uuid = data.draw(st.sampled_from(org_uuids))
    org_from, org_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    ituser_uuid = data.draw(st.sampled_from(ituser_uuids))

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

    role_type = fetch_class_uuids(graphapi_post, "role")

    test_data = data.draw(
        st.lists(
            st.builds(
                RoleBindingCreate,
                uuid=st.uuids() | st.none(),
                ituser=st.just(ituser_uuid),
                role=st.sampled_from(role_type),
                org_unit=st.just(org_uuid),
                validity=st.builds(
                    RAValidity,
                    from_date=st.just(test_data_validity_start),
                    to_date=test_data_validity_end_strat,
                ),
            )
        )
    )

    CREATE_ROLEBINDINGS_QUERY = """
        mutation CreateRolebindings($input: [RoleBindingCreateInput!]!) {
            rolebindings_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        CREATE_ROLEBINDINGS_QUERY, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuids = [
        rolebinding["uuid"] for rolebinding in response.data["rolebindings_create"]
    ]
    assert len(uuids) == len(test_data)


@given(test_data=...)
@patch(
    "mora.graphapi.versions.latest.mutators.update_rolebinding", new_callable=AsyncMock
)
async def test_update_role_unit_test(
    update_rolebinding: AsyncMock, test_data: RoleBindingUpdate
) -> None:
    """Tests that the mutator function for updating a role passes through, with the
    defined pydantic model."""

    mutation = """
        mutation UpdateRole($input: RoleBindingUpdateInput!) {
            rolebinding_update(input: $input) {
                uuid
            }
        }
    """

    update_rolebinding.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"rolebinding_update": {"uuid": str(test_data.uuid)}}

    update_rolebinding.assert_called_with(test_data)


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
