# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from datetime import time
from unittest import mock
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

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
from mora import lora
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.engagements import terminate_engagement
from mora.graphapi.versions.latest.models import EngagementCreate
from mora.graphapi.versions.latest.models import EngagementTerminate
from mora.graphapi.versions.latest.models import EngagementUpdate
from mora.graphapi.versions.latest.types import EngagementType
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import EngagementRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(EngagementRead))
def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the engagement data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                engagements {
                    uuid
                    objects {
                        uuid
                        org_unit_uuid
                        employee_uuid
                        engagement_type_uuid
                        job_function_uuid
                        leave_uuid
                        primary_uuid
                        type
                        user_key
                        fraction
                        validity {from to}
                        extension_1
                        extension_2
                        extension_3
                        extension_4
                        extension_5
                        extension_6
                        extension_7
                        extension_8
                        extension_9
                        extension_10
                    }
                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["engagements"]) == test_data


@given(test_input=graph_data_uuids_strat(EngagementRead))
def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query engagements by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    engagements(uuids: $uuids) {
                        uuid
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [assoc.get("uuid") for assoc in response.data["engagements"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@given(test_data=graph_data_strat(EngagementRead))
def test_query_is_primary(test_data, graphapi_post, patch_loader):
    """Test that we can query 'is_primary' from the engagement data model."""

    query = """
            query {
                engagements {
                    uuid
                    objects {
                        uuid
                        is_primary
                    }
                }
            }
        """
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        # Patch check for is_primary
        with mock.patch(
            "mora.graphapi.versions.latest.schema.is_class_uuid_primary",
            return_value=True,
        ) as primary_mock:
            response: GQLResponse = graphapi_post(query)

    assert response.errors is None

    for e in response.data["engagements"]:

        if test_data[0]["primary_uuid"]:
            # primary_uuid is optional.
            # If it exists the patched is_primary returns True
            expected = True
            primary_mock.assert_called_once_with(test_data[0]["uuid"])
        else:
            # If primary_uuid is None the check is not done and is_primary is False
            expected = False
            primary_mock.assert_not_called()

        assert e["objects"][0]["is_primary"] == expected


@given(
    st.uuids(),
    st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
async def test_terminate_response(given_uuid, given_validity_dts):
    # Init
    from_date, to_date = given_validity_dts

    # The terminate logic have a check that verifies we don't use times other than:
    # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
    # expect an exception.
    expect_exception = False
    if to_date is None or to_date.time() != time.min:
        expect_exception = True

    # Configure the addr-terminate we want to perform
    test_data = EngagementTerminate(
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
            tr = await terminate_engagement(input=test_data)
            terminate_result_uuid = tr.uuid if tr else terminate_result_uuid
        except Exception as e:
            caught_exception = e

    # Assert
    if not expect_exception:
        assert terminate_result_uuid == test_data.uuid
    else:
        assert caught_exception is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_class_reset")
@pytest.mark.parametrize(
    "filter_snippet,expected",
    [
        ("", 3),
        # Employee filters
        ('(employees: "236e0a78-11a0-4ed9-8545-6286bb8611c7")', 2),
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
        ('(org_units: "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e")', 3),
        ('(org_units: "2874e1dc-85e6-4269-823a-e1125484dfd3")', 0),
        (
            """
            (org_units: [
                "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
            ])
        """,
            3,
        ),
        # Mixed filters
        (
            """
            (
                employees: "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                org_units: "2874e1dc-85e6-4269-823a-e1125484dfd3"
            )
        """,
            0,
        ),
        (
            """
            (
                employees: "236e0a78-11a0-4ed9-8545-6286bb8611c7",
                org_units: "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
            )
        """,
            2,
        ),
    ],
)
async def test_engagement_filters(graphapi_post, filter_snippet, expected) -> None:
    """Test filters on engagements."""
    engagement_query = f"""
        query Managers {{
            engagements{filter_snippet} {{
                uuid
            }}
        }}
    """
    response: GQLResponse = graphapi_post(engagement_query)
    assert response.errors is None
    assert len(response.data["engagements"]) == expected


@given(test_data=...)
@patch(
    "mora.graphapi.versions.latest.mutators.create_engagement", new_callable=AsyncMock
)
async def test_create_engagement(
    create_engagement: AsyncMock, test_data: EngagementCreate
) -> None:
    """Test that pydantic jsons are passed through to engagement_create."""

    mutate_query = """
        mutation CreateEngagement($input: EngagementCreateInput!) {
            engagement_create(input: $input) {
                uuid
            }
        }
    """
    created_uuid = uuid4()
    create_engagement.return_value = EngagementType(uuid=created_uuid)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"engagement_create": {"uuid": str(created_uuid)}}

    create_engagement.assert_called_with(test_data)


@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_engagement_integration_test(
    data, graphapi_post, org_uuids, employee_uuids
) -> None:
    """Test that engagements can be created in LoRa via GraphQL."""

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

    engagement_type_uuids = fetch_class_uuids(graphapi_post, "engagement_type")
    job_function_uuids = fetch_class_uuids(graphapi_post, "engagement_job_function")

    test_data = data.draw(
        st.builds(
            EngagementCreate,
            org_unit=st.just(org_uuid),
            employee=st.sampled_from(employee_uuids),
            engagement_type=st.sampled_from(engagement_type_uuids),
            job_function=st.sampled_from(job_function_uuids),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutate_query = """
        mutation CreateEngagement($input: EngagementCreateInput!) {
            engagement_create(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutate_query, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuid = UUID(response.data["engagement_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            engagements(uuids: [$uuid], from_date: null, to_date: null) {
                objects {
                    user_key
                    org_unit: org_unit_uuid
                    employee: employee_uuid
                    engagement_type: engagement_type_uuid
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
    obj = one(one(response.data["engagements"])["objects"])
    assert obj["user_key"] == test_data.user_key or str(uuid)
    assert UUID(obj["org_unit"]) == test_data.org_unit
    assert UUID(obj["employee"]) == test_data.employee
    assert UUID(obj["engagement_type"]) == test_data.engagement_type
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


@given(test_data=...)
@patch(
    "mora.graphapi.versions.latest.mutators.update_engagement", new_callable=AsyncMock
)
async def test_update_engagement_unit_test(
    update_engagement: AsyncMock, test_data: EngagementUpdate
) -> None:
    """Test that pydantic jsons are passed through to engagement_update."""

    mutate_query = """
        mutation UpdateEngagement($input: EngagementUpdateInput!) {
            engagement_update(input: $input) {
                uuid
            }
        }
    """

    engagement_uuid_to_update = uuid4()
    update_engagement.return_value = EngagementType(uuid=engagement_uuid_to_update)

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )

    assert response.errors is None
    assert response.data == {
        "engagement_update": {"uuid": str(engagement_uuid_to_update)}
    }

    update_engagement.assert_called_with(test_data)


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "d000591f-8705-4324-897a-075e3623f37b",
            "user_key": "-",
            "job_function": "62ec821f-4179-4758-bfdf-134529d186e9",
            "org_unit": None,
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "d000591f-8705-4324-897a-075e3623f37b",
            "user_key": None,
            "job_function": "62ec821f-4179-4758-bfdf-134529d186e9",
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "d000591f-8705-4324-897a-075e3623f37b",
            "user_key": "-",
            "job_function": None,
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "employee": None,
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
        {
            "uuid": "d000591f-8705-4324-897a-075e3623f37b",
            "user_key": None,
            "job_function": None,
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "employee": None,
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
    ],
)
async def test_update_engagement_integration_test(graphapi_post, test_data) -> None:

    uuid = test_data["uuid"]

    query = """
        query MyQuery($uuid: UUID!) {
            engagements(uuids: [$uuid]) {
                objects {
                    user_key
                    job_function: job_function_uuid
                    org_unit: org_unit_uuid
                    employee: employee_uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None

    pre_update_engagement = one(one(response.data["engagements"])["objects"])

    mutate_query = """
        mutation UpdateEngagement($input: EngagementUpdateInput!) {
            engagement_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response: GQLResponse = graphapi_post(
        mutate_query, {"input": jsonable_encoder(test_data)}
    )
    assert mutation_response.errors is None

    """Query data to check that it actually gets written to database"""
    verify_query = """
        query VerifyQuery($uuid: [UUID!]!) {
            engagements(uuids: $uuid){
                objects {
                    uuid
                    user_key
                    job_function: job_function_uuid
                    org_unit: org_unit_uuid
                    employee: employee_uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """

    verify_response: GQLResponse = graphapi_post(
        query=verify_query, variables={"uuid": uuid}
    )

    assert verify_response.errors is None

    post_update_engagement = one(one(verify_response.data["engagements"])["objects"])

    # If value is None, we use data from our original query
    # to ensure that the field has not been updated
    expected_updated_engagement = {
        k: v or pre_update_engagement[k] for k, v in test_data.items()
    }

    assert post_update_engagement == expected_updated_engagement
