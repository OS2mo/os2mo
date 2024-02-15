# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from unittest import mock

from hypothesis import HealthCheck
from hypothesis import settings
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import characters
from more_itertools import one
from pytest import MonkeyPatch

from ..conftest import GraphAPIPost
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import EngagementCreate
from mora.graphapi.versions.latest.models import EngagementUpdate
from mora.util import POSITIVE_INFINITY
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import EngagementRead


@settings(
    suppress_health_check=[
        # Database access is mocked, so it's okay to run the test with the same
        # graphapi_post fixture multiple times.
        HealthCheck.function_scoped_fixture,
    ],
)
@given(test_data=graph_data_strat(EngagementRead))
def test_query_all(test_data, graphapi_post: GraphAPIPost, patch_loader):
    """Test that we can query all attributes of the engagement data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                engagements {
                    objects {
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
            }
        """
        response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["engagements"]["objects"]) == test_data


@settings(
    suppress_health_check=[
        # Database access is mocked, so it's okay to run the test with the same
        # graphapi_post fixture multiple times.
        HealthCheck.function_scoped_fixture,
    ],
)
@given(test_input=graph_data_uuids_strat(EngagementRead))
def test_query_by_uuid(test_input, graphapi_post: GraphAPIPost, patch_loader):
    """Test that we can query engagements by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    engagements(filter: {uuids: $uuids}) {
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
    result_uuids = [
        assoc.get("uuid") for assoc in response.data["engagements"]["objects"]
    ]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@settings(
    suppress_health_check=[
        # Database access is mocked, so it's okay to run the test with the same
        # graphapi_post fixture multiple times.
        HealthCheck.function_scoped_fixture,
    ],
)
@given(test_data=graph_data_strat(EngagementRead))
def test_query_is_primary(test_data, graphapi_post: GraphAPIPost, patch_loader):
    """Test that we can query 'is_primary' from the engagement data model."""

    query = """
            query {
                engagements {
                    objects {
                        uuid
                        objects {
                            uuid
                            is_primary
                        }
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
            response = graphapi_post(query)

    assert response.errors is None

    for e in response.data["engagements"]["objects"]:
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 3),
        # Employee filters
        ({"employee": {"uuids": "236e0a78-11a0-4ed9-8545-6286bb8611c7"}}, 2),
        ({"employee": {"uuids": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"}}, 1),
        ({"employee": {"uuids": "6ee24785-ee9a-4502-81c2-7697009c9053"}}, 0),
        (
            {
                "employee": {
                    "uuids": [
                        "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "6ee24785-ee9a-4502-81c2-7697009c9053",
                    ]
                }
            },
            1,
        ),
        # Organisation Unit filter
        ({"org_unit": {"uuids": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"}}, 3),
        ({"org_unit": {"uuids": "2874e1dc-85e6-4269-823a-e1125484dfd3"}}, 0),
        (
            {
                "org_unit": {
                    "uuids": [
                        "2874e1dc-85e6-4269-823a-e1125484dfd3",
                        "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    ]
                }
            },
            3,
        ),
        # Job function filter
        ({"job_function": {"uuids": "ca76a441-6226-404f-88a9-31e02e420e52"}}, 1),
        ({"job_function": {"uuids": "2874e1dc-85e6-4269-823a-e1125484dfd3"}}, 0),
        (
            {
                "job_function": {
                    "uuids": [
                        "ca76a441-6226-404f-88a9-31e02e420e52",
                        "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                    ]
                }
            },
            3,
        ),
        # Mixed filters
        (
            {
                "employee": {"uuids": "236e0a78-11a0-4ed9-8545-6286bb8611c7"},
                "org_unit": {"uuids": "2874e1dc-85e6-4269-823a-e1125484dfd3"},
                "job_function": {"uuids": "2874e1dc-85e6-4269-823a-e1125484dfd3"},
            },
            0,
        ),
        (
            {
                "employee": {"uuids": "236e0a78-11a0-4ed9-8545-6286bb8611c7"},
                "org_unit": {"uuids": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuids": None},
            },
            2,
        ),
        (
            {
                "employee": {"uuids": "236e0a78-11a0-4ed9-8545-6286bb8611c7"},
                "org_unit": {"uuids": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {"uuids": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"},
            },
            1,
        ),
    ],
)
async def test_engagement_filters(
    graphapi_post: GraphAPIPost, filter, expected
) -> None:
    """Test filters on engagements."""
    engagement_query = """
        query Engagements($filter: EngagementFilter!) {
            engagements(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(engagement_query, variables=dict(filter=filter))
    assert response.errors is None
    assert len(response.data["engagements"]["objects"]) == expected


@given(test_data=st.builds(EngagementCreate, employee=st.none(), person=st.uuids()))
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
    create_engagement.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"engagement_create": {"uuid": str(test_data.uuid)}}

    create_engagement.assert_called_with(test_data)


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_engagement_integration_test(
    data, graphapi_post: GraphAPIPost, org_uuids, employee_uuids
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
    primary_uuids = fetch_class_uuids(graphapi_post, "primary_type")

    test_data = data.draw(
        st.builds(
            EngagementCreate,
            org_unit=st.just(org_uuid),
            employee=st.sampled_from(employee_uuids),
            engagement_type=st.sampled_from(engagement_type_uuids),
            job_function=st.sampled_from(job_function_uuids),
            primary=st.sampled_from(primary_uuids),
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
    response = graphapi_post(mutate_query, {"input": jsonable_encoder(test_data)})
    assert response.errors is None
    uuid = UUID(response.data["engagement_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            engagements(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        org_unit: org_unit_uuid
                        employee: employee_uuid
                        engagement_type: engagement_type_uuid
                        job_function: job_function_uuid
                        primary: primary_uuid
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
    obj = one(one(response.data["engagements"]["objects"])["objects"])
    assert obj["user_key"] == test_data.user_key or str(uuid)
    assert UUID(obj["org_unit"]) == test_data.org_unit
    assert UUID(obj["employee"]) == test_data.employee
    assert UUID(obj["engagement_type"]) == test_data.engagement_type
    assert UUID(obj["job_function"]) == test_data.job_function
    assert UUID(obj["primary"]) == test_data.primary
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
    update_engagement.return_value = engagement_uuid_to_update

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
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "d000591f-8705-4324-897a-075e3623f37b",
            "user_key": "-",
            "job_function": "62ec821f-4179-4758-bfdf-134529d186e9",
            "org_unit": None,
            "primary": "2f16d140-d743-4c9f-9e0e-361da91a06f6",
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "d000591f-8705-4324-897a-075e3623f37b",
            "user_key": None,
            "job_function": "07cea156-1aaf-4c89-bf1b-8e721f704e22",
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "d000591f-8705-4324-897a-075e3623f37b",
            "user_key": "-",
            "job_function": None,
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
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
            "primary": None,
            "employee": None,
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
    ],
)
async def test_update_engagement_integration_test(
    graphapi_post: GraphAPIPost, test_data
) -> None:
    uuid = test_data["uuid"]

    query = """
        query MyQuery($uuid: UUID!) {
            engagements(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        user_key
                        job_function: job_function_uuid
                        primary: primary_uuid
                        org_unit: org_unit_uuid
                        employee: employee_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None

    pre_update_engagement = one(one(response.data["engagements"]["objects"])["objects"])

    mutate_query = """
        mutation UpdateEngagement($input: EngagementUpdateInput!) {
            engagement_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(
        mutate_query, {"input": jsonable_encoder(test_data)}
    )
    assert mutation_response.errors is None

    """Query data to check that it actually gets written to database"""
    verify_query = """
        query VerifyQuery($uuid: [UUID!]!) {
            engagements(filter: {uuids: $uuid}){
                objects {
                    objects {
                        uuid
                        user_key
                        job_function: job_function_uuid
                        primary: primary_uuid
                        org_unit: org_unit_uuid
                        employee: employee_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    verify_response = graphapi_post(query=verify_query, variables={"uuid": uuid})

    assert verify_response.errors is None

    post_update_engagement = one(
        one(verify_response.data["engagements"]["objects"])["objects"]
    )

    # If value is None, we use data from our original query
    # to ensure that the field has not been updated
    expected_updated_engagement = {
        k: v or pre_update_engagement[k] for k, v in test_data.items()
    }

    assert post_update_engagement == expected_updated_engagement


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "update_input, expected_extension_field",
    [
        (
            {
                "uuid": "301a906b-ef51-4d5c-9c77-386fb8410459",
                "validity": {"from": datetime.today().date().isoformat()},
                "extension_1": "Testing the extensions field",
            },
            {
                "extension_1": "Testing the extensions field",
                "extension_2": None,
                "extension_3": None,
            },
        ),
        (
            {
                "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                "validity": {"from": datetime.today().date().isoformat()},
                "extension_2": "NOT TEST 2 LUL",
                "extension_3": "Third extension",
            },
            {
                "extension_1": "test1",
                "extension_2": "NOT TEST 2 LUL",
                "extension_3": "Third extension",
            },
        ),
        (
            {
                "uuid": "d3028e2e-1d7a-48c1-ae01-d4c64e64bbab",
                "validity": {"from": datetime.today().date().isoformat()},
                "extension_1": "OS",
                "extension_2": "2",
                "extension_3": "MO",
            },
            {"extension_1": "OS", "extension_2": "2", "extension_3": "MO"},
        ),
    ],
)
async def test_update_extensions_field_integrations_test(
    graphapi_post: GraphAPIPost, update_input, expected_extension_field
) -> None:
    """Tests that extension fields in engagements is editable via GraphQL."""
    # ARRANGE
    uuid = update_input["uuid"]

    query = """
        query MyQuery($uuid: [UUID!]) {
          engagements(filter: {uuids: $uuid}) {
            objects {
              objects {
                extension_1
                extension_2
                extension_3
              }
            }
          }
        }
    """
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.status_code == 200

    # ACT
    mutation_query = """
        mutation UpdateEngagement($input: EngagementUpdateInput!) {
          engagement_update(input: $input) {
            uuid
          }
        }
    """

    mutation_response = graphapi_post(
        query=mutation_query, variables={"input": jsonable_encoder(update_input)}
    )

    assert mutation_response.errors is None
    assert mutation_response.status_code == 200

    verify_query = """
        query MyVerifyQuery($uuid: [UUID!]!) {
          engagements(filter: {uuids: $uuid}) {
            objects {
              objects {
                extension_1
                extension_2
                extension_3
              }
            }
          }
        }
    """
    verify_response = graphapi_post(query=verify_query, variables={"uuid": uuid})
    assert verify_response.errors is None
    assert verify_response.status_code == 200

    post_update_engagement_with_new_extensions = one(
        one(verify_response.data["engagements"]["objects"])["objects"]
    )

    # ASSERT
    assert post_update_engagement_with_new_extensions == expected_extension_field


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_engagement_with_extensions_fields_integrations_test(
    data, graphapi_post: GraphAPIPost, org_uuids, employee_uuids
) -> None:
    """Test that extension fields in engagements can be created in LoRa via GraphQL."""
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

    # 'Cc' - Control, 'Cs' - Surrogate.
    extension_field_texts = st.text(
        alphabet=characters(blacklist_categories=("Cc", "Cs")),
        min_size=1,
    )

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
            extension_1=extension_field_texts,
            extension_2=extension_field_texts,
            extension_3=extension_field_texts,
            extension_4=extension_field_texts,
            extension_5=extension_field_texts,
            extension_6=extension_field_texts,
            extension_7=extension_field_texts,
            extension_8=extension_field_texts,
            extension_9=extension_field_texts,
            extension_10=extension_field_texts,
        )
    )

    mutate_query = """
        mutation CreateEngagement($input: EngagementCreateInput!) {
            engagement_create(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(
        query=mutate_query, variables={"input": jsonable_encoder(test_data)}
    )

    assert mutation_response.errors is None
    uuid = UUID(mutation_response.data["engagement_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: [UUID!]!) {
            engagements(filter: {uuids: $uuid, from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        org_unit: org_unit_uuid
                        employee: employee_uuid
                        engagement_type: engagement_type_uuid
                        validity {
                            from
                            to
                        }
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
        }
        """
    response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None

    obj = one(one(response.data["engagements"]["objects"])["objects"])

    assert obj["extension_1"] == test_data.extension_1
    assert obj["extension_2"] == test_data.extension_2
    assert obj["extension_3"] == test_data.extension_3
    assert obj["extension_4"] == test_data.extension_4
    assert obj["extension_5"] == test_data.extension_5
    assert obj["extension_6"] == test_data.extension_6
    assert obj["extension_7"] == test_data.extension_7
    assert obj["extension_8"] == test_data.extension_8
    assert obj["extension_9"] == test_data.extension_9
    assert obj["extension_10"] == test_data.extension_10


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_clear_extension_field(graphapi_post: GraphAPIPost) -> None:
    """Test that extension fields can be cleared via GraphQL."""

    def read_extension_field3(uuid: UUID) -> str | None:
        verify_query = """
        query ReadExtensionField(
            $uuid: UUID!
        ) {
          engagements(filter: {uuids: [$uuid]}) {
            objects {
              current {
                extension_3
              }
            }
          }
        }
        """
        response = graphapi_post(verify_query, {"uuid": str(uuid)})
        assert response.errors is None
        extension_3 = one(response.data["engagements"]["objects"])["current"][
            "extension_3"
        ]
        return extension_3

    def set_extension_field3(uuid: UUID, extension_3: str) -> None:
        mutate_query = """
        mutation UpdateExtensionField(
          $uuid: UUID!, $extension_3: String
        ) {
          engagement_update(
            input: {
              uuid: $uuid,
              validity: {from: "2020-01-01"},
              extension_3: $extension_3
            }
          ) {
            uuid
          }
        }
        """
        response = graphapi_post(
            mutate_query, {"uuid": str(uuid), "extension_3": extension_3}
        )
        assert response.errors is None
        response_uuid = UUID(response.data["engagement_update"]["uuid"])
        assert response_uuid == uuid

    uuid = UUID("d000591f-8705-4324-897a-075e3623f37b")

    extension_3 = read_extension_field3(uuid)
    assert extension_3 is None

    new_value = "Testing"
    set_extension_field3(uuid, new_value)
    extension_3 = read_extension_field3(uuid)
    assert extension_3 == new_value

    set_extension_field3(uuid, "")
    extension_3 = read_extension_field3(uuid)
    assert extension_3 is None
