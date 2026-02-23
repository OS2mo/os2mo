# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from uuid import UUID
from uuid import uuid4

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from pytest import MonkeyPatch

from tests.conftest import GQLResponse

from ..conftest import GraphAPIPost
from .utils import fetch_employee_validity
from .utils import fetch_org_unit_validity


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the ituser data model."""
    query = """
        query {
            itusers {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        employee_uuid
                        org_unit_uuid
                        engagement_uuid
                        itsystem_uuid
                        primary_uuid
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
async def test_create_ituser_employee_integration_test(
    monkeypatch: MonkeyPatch,
    graphapi_post: GraphAPIPost,
    itsystem_uuids,
    employee_uuids,
) -> None:
    """Test that multiple itusers can be created using the list mutator."""

    monkeypatch.setattr(
        "mora.service.validation.models.GroupValidation.validate_unique_constraint",
        AsyncMock(return_value=None),
    )
    employee_uuid = employee_uuids[0]
    employee_from, employee_to = fetch_employee_validity(graphapi_post, employee_uuid)

    start_date = employee_from

    test_data = {
        "uuid": str(uuid4()),
        "user_key": "ituser_key",
        "itsystem": str(itsystem_uuids[0]),
        "person": str(employee_uuid),
        "org_unit": None,
        "engagement": str(uuid4()),
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutate_query = """
        mutation CreateITUser($input: ITUserCreateInput!){
            ituser_create(input: $input){
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": jsonable_encoder(test_data)})
    assert response.errors is None
    uuid = UUID(response.data["ituser_create"]["uuid"])
    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            itusers(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        user_key
                        itsystem_uuid
                        employee_uuid
                        org_unit_uuid
                        engagement_uuid
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
    obj = one(one(response.data["itusers"]["objects"])["objects"])
    assert obj["user_key"] == test_data["user_key"]
    assert obj["itsystem_uuid"] == test_data["itsystem"]
    assert obj["employee_uuid"] == test_data["person"]
    assert obj["org_unit_uuid"] is None
    assert obj["engagement_uuid"] == test_data["engagement"]
    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_ituser_org_unit_integration_test(
    graphapi_post: GraphAPIPost,
    itsystem_uuids,
    org_uuids,
) -> None:
    org_unit_uuid = org_uuids[0]
    org_unit_from, org_unit_to = fetch_org_unit_validity(graphapi_post, org_unit_uuid)

    start_date = org_unit_from

    test_data = {
        "uuid": str(uuid4()),
        "user_key": "org_ituser_key",
        "itsystem": str(itsystem_uuids[0]),
        "person": None,
        "org_unit": str(org_unit_uuid),
        "engagement": None,
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutate_query = """
        mutation CreateITUser($input: ITUserCreateInput!){
            ituser_create(input: $input){
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": test_data})
    assert response.errors is None
    uuid = UUID(response.data["ituser_create"]["uuid"])
    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            itusers(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        user_key
                        itsystem_uuid
                        employee_uuid
                        org_unit_uuid
                        engagement_uuid
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

    obj = one(one(response.data["itusers"]["objects"])["objects"])
    assert obj["user_key"] == test_data["user_key"]
    assert obj["itsystem_uuid"] == test_data["itsystem"]
    assert obj["org_unit_uuid"] == test_data["org_unit"]
    assert obj["employee_uuid"] is None
    assert obj["engagement_uuid"] is None
    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "user_key": "UserKey",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "itsystem": "0872fb72-926d-4c5c-a063-ff800b8ee697",
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
        {
            "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "user_key": None,
            "primary": None,
            "itsystem": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "user_key": "UserKey",
            "primary": None,
            "itsystem": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "user_key": None,
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "itsystem": "0872fb72-926d-4c5c-a063-ff800b8ee697",
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
    ],
)
async def test_update_ituser_integration_test(
    graphapi_post: GraphAPIPost, test_data
) -> None:
    uuid = test_data["uuid"]

    query = """
        query MyQuery($uuid: UUID!) {
            itusers (filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        user_key
                        primary: primary_uuid
                        itsystem: itsystem_uuid
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

    pre_update_ituser = one(one(response.data["itusers"]["objects"])["objects"])

    mutate_query = """
        mutation UpdateITUser($input: ITUserUpdateInput!) {
            ituser_update(input: $input) {
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
            itusers(filter: {uuids: $uuid}){
                objects {
                    objects {
                        uuid
                        user_key
                        primary: primary_uuid
                        itsystem: itsystem_uuid
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

    post_update_ituser = one(one(verify_response.data["itusers"]["objects"])["objects"])

    # If value is None, we use data from our original query
    # to ensure that the field has not been updated
    expected_updated_ituser = {
        k: v or pre_update_ituser[k] for k, v in test_data.items()
    }

    assert post_update_ituser == expected_updated_ituser


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_it_user_systems_uuid_filter(graphapi_post):
    ACTIVE_DIRECTORY = "59c135c9-2b15-41cc-97c8-b5dff7180beb"

    query = """
      query TestITSystemUUIDFilter($itsystem_uuids: [UUID!]!) {
        itusers(filter: {itsystem_uuids: $itsystem_uuids}) {
          objects {
            objects {
              itsystem {
                uuid
              }
            }
          }
        }
      }
    """

    r: GQLResponse = graphapi_post(
        query=query, variables={"itsystem_uuids": ACTIVE_DIRECTORY}
    )

    assert r.errors is None
    assert r.data is not None

    for itusers in r.data["itusers"]["objects"]:
        for objects in itusers["objects"]:
            assert objects["itsystem"]["uuid"] == ACTIVE_DIRECTORY


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_it_user_external_id(graphapi_post: GraphAPIPost) -> None:
    # Create
    r = graphapi_post(
        """
        mutation Create($input: ITUserCreateInput!) {
          ituser_create(input: $input) {
            uuid
          }
        }
        """,
        variables={
            "input": {
                "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "itsystem": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
                "user_key": "foo",
                "external_id": "foo",
                "validity": {"from": "2021-01-01"},
            }
        },
    )
    assert r.errors is None
    assert r.data is not None
    uuid = r.data["ituser_create"]["uuid"]

    # Check
    read_query = """
      query Read($external_id: String!) {
        itusers(filter: { external_ids: [$external_id], from_date: null, to_date: null }) {
          objects {
            validities(start: null, end: null) {
              user_key
              external_id
              validity {
                from
                to
              }
            }
          }
        }
      }
    """
    r = graphapi_post(read_query, variables={"external_id": "foo"})
    assert r.errors is None
    assert r.data is not None
    obj = one(r.data["itusers"]["objects"])
    assert obj["validities"] == [
        {
            "user_key": "foo",
            "external_id": "foo",
            "validity": {"from": "2021-01-01T00:00:00+01:00", "to": None},
        }
    ]

    # Update
    r = graphapi_post(
        """
        mutation Update($input: ITUserUpdateInput!) {
          ituser_update(input: $input) {
            uuid
          }
        }
        """,
        variables={
            "input": {
                "uuid": uuid,
                "external_id": "bar",
                "validity": {"from": "2022-02-02"},
            }
        },
    )
    assert r.errors is None

    # Check
    r = graphapi_post(read_query, variables={"external_id": "bar"})
    assert r.errors is None
    assert r.data is not None
    obj = one(r.data["itusers"]["objects"])
    assert obj["validities"] == [
        {
            "user_key": "foo",
            "external_id": "foo",
            "validity": {
                "from": "2021-01-01T00:00:00+01:00",
                "to": "2022-02-01T00:00:00+01:00",
            },
        },
        {
            "user_key": "foo",
            "external_id": "bar",
            "validity": {"from": "2022-02-02T00:00:00+01:00", "to": None},
        },
    ]
