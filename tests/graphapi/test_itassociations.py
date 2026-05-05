# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID
from uuid import uuid4

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from mora.graphapi.gmodels.mo.details import AssociationRead
from more_itertools import one
from pydantic import Field

from ..conftest import GraphAPIPost
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity


class ITAssociationRead(AssociationRead):
    # This is needed since these 2 will be `None` otherwise, which would result in
    # 0 ITAssociations created in the MonkeyPatch..
    it_user_uuid: UUID = Field(
        description="UUID of an 'ITAssociation' model, only defined for 'IT associations'."
    )
    job_function_uuid: UUID = Field(description="UUID of the 'job_function'")


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all our ITAssociations."""
    query = """
        query {
            associations(filter: {it_association: true}) {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        org_unit_uuid
                        employee_uuid
                        association_type_uuid
                        primary_uuid
                        substitute_uuid
                        job_function_uuid
                        primary_uuid
                        it_user_uuid
                        trade_union_uuid
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
def test_query_flag(graphapi_post: GraphAPIPost):
    """Test that the flag works."""
    query = """
        query ITAssociation($it_association: Boolean) {
          associations(filter: {it_association: $it_association}) {
            objects {
              uuid
            }
          }
        }
    """
    associations = {}
    for is_it_association in (True, False, None):
        response = graphapi_post(query, variables={"it_association": is_it_association})
        assert response.errors is None
        associations[is_it_association] = {
            o["uuid"] for o in response.data["associations"]["objects"]
        }
    assert associations[None] == associations[True].union(associations[False])
    assert associations[True].isdisjoint(associations[False])


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_itassociation_integration_test(
    graphapi_post: GraphAPIPost, org_uuids, employee_uuids, ituser_uuids
) -> None:
    """Test that ITAssociation annotations can be created in LoRa via GraphQL."""

    org_uuid = org_uuids[0]
    parent_from, parent_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    start_date = parent_from

    job_function_uuids = fetch_class_uuids(graphapi_post, "engagement_job_function")

    test_data = {
        "uuid": str(uuid4()),
        "user_key": "asd123",
        "org_unit": str(org_uuid),
        "it_user": str(ituser_uuids[0]),
        "person": str(employee_uuids[0]),
        "job_function": str(job_function_uuids[0]),
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutation = """
        mutation CreateITAssociation($input: ITAssociationCreateInput!) {
            itassociation_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"input": test_data})

    assert response.errors is None
    uuid = UUID(response.data["itassociation_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            associations(filter: {uuids: [$uuid], from_date: null, to_date: null, it_association: true}) {
                objects {
                    objects {
                        user_key
                        org_unit: org_unit_uuid
                        employee: employee_uuid
                        it_user: it_user_uuid
                        job_function: job_function_uuid
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
    obj = one(one(response.data["associations"]["objects"])["objects"])

    assert obj["employee"] == test_data["person"]
    assert obj["it_user"] == test_data["it_user"]
    assert obj["org_unit"] == test_data["org_unit"]
    assert obj["user_key"] == test_data["user_key"]
    assert obj["job_function"] == test_data["job_function"]

    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
            "it_user": "4de484d9-f577-4fe0-965f-2d4be11b348c",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "job_function": "07cea156-1aaf-4c89-bf1b-8e721f704e22",
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
        {
            "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
            "it_user": "4de484d9-f577-4fe0-965f-2d4be11b348c",
            "primary": None,
            "job_function": "07cea156-1aaf-4c89-bf1b-8e721f704e22",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
            "it_user": None,
            "primary": None,
            "job_function": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
            "it_user": "4de484d9-f577-4fe0-965f-2d4be11b348c",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "job_function": "07cea156-1aaf-4c89-bf1b-8e721f704e22",
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
    ],
)
async def test_update_itassociation_integration_test(
    graphapi_post: GraphAPIPost, test_data
) -> None:
    uuid = test_data["uuid"]

    query = """
        query MyQuery {
            associations(filter: {it_association: true}) {
                objects {
                    objects {
                        uuid
                        it_user: it_user_uuid
                        primary: primary_uuid
                        job_function: job_function_uuid
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

    pre_update_it_association = one(
        one(response.data["associations"]["objects"])["objects"]
    )

    mutate_query = """
        mutation UpdateITAssociation($input: ITAssociationUpdateInput!) {
            itassociation_update(input: $input) {
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
            associations(filter: {uuids: $uuid, it_association: true}){
                objects {
                    objects {
                        uuid
                        it_user: it_user_uuid
                        primary: primary_uuid
                        job_function: job_function_uuid
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

    post_update_it_association = one(
        one(verify_response.data["associations"]["objects"])["objects"]
    )

    # If value is None, we use data from our original query
    # to ensure that the field has not been updated
    expected_updated_it_association = {
        k: v or pre_update_it_association[k] for k, v in test_data.items()
    }

    assert post_update_it_association == expected_updated_it_association


@pytest.mark.integration_test
@freezegun.freeze_time("2023-07-13", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
            "to": "2023-07-25T00:00:00+02:00",
        },
        {
            "uuid": "c89853b8-3da5-4b10-8d87-6ca5b4c9416b",
            "to": "2040-01-01T00:00:00+01:00",
        },
    ],
)
async def test_itassociation_terminate_integration(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    uuid = test_data["uuid"]
    mutation = """
        mutation TerminateITAssociation($input: ITAssociationTerminateInput!) {
            itassociation_terminate(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            associations(filter: {uuids: [$uuid], it_association: true}){
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
    it_association_objects_post_terminate = one(
        one(verify_response.data["associations"]["objects"])["objects"]
    )
    assert test_data["uuid"] == it_association_objects_post_terminate["uuid"]
    assert test_data["to"] == it_association_objects_post_terminate["validity"]["to"]
