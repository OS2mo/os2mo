# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import freezegun
import pytest
from fastapi.encoders import jsonable_encoder
from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.strategies import DataObject
from mora.graphapi.gmodels.mo import Validity as RAValidity
from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.models import ITUserCreate
from mora.graphapi.versions.latest.models import ITUserUpdate
from mora.util import POSITIVE_INFINITY
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


@patch("mora.graphapi.versions.latest.mutators.create_ituser", new_callable=AsyncMock)
@given(data=st.data())
async def test_create_ituser(create_ituser: AsyncMock, data: DataObject) -> None:
    """Test that pydantic jsons are passed through to create_ituser."""

    mutate_query = """
        mutation CreateITUser($input: ITUserCreateInput!){
            ituser_create(input: $input){
                uuid
            }
        }
    """

    # TODO: Why isn't this two different tests?
    should_test_employee = data.draw(st.booleans())

    if should_test_employee:
        employee_uuid = uuid4()
        org_unit_uuid = None
    else:
        employee_uuid = None
        org_unit_uuid = uuid4()

    test_data = data.draw(
        st.builds(
            ITUserCreate,
            person=st.just(employee_uuid),
            org_unit=st.just(org_unit_uuid),
        )
    )

    create_ituser.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)

    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )

    assert response.errors is None
    assert response.data == {"ituser_create": {"uuid": str(test_data.uuid)}}


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_ituser_employee_integration_test(
    data: DataObject,
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
    employee_uuid = data.draw(st.sampled_from(employee_uuids))
    employee_from, employee_to = fetch_employee_validity(graphapi_post, employee_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=employee_from, max_value=employee_to or datetime.max)
    )

    if employee_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=employee_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    test_data = data.draw(
        st.builds(
            ITUserCreate,
            uuid=st.none() | st.uuids(),
            user_key=st.text(
                alphabet=st.characters(whitelist_categories=("L",)), min_size=1
            ),
            itsystem=st.sampled_from(itsystem_uuids),
            person=st.just(employee_uuid),
            org_unit=st.none(),
            engagement=st.uuids() | st.none(),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

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

    # IMPORTANT: This is needed and shouldn't (I think), cause problems.
    # Since we can't avoid the "duplicate error", we set it to None at the top
    # `validate_unique_constraint.return_value = None`, this results in the mutator
    # query failing WITHOUT returning that exact error. Therefore we need to check that
    # response.data["itusers"] is not empty.
    # The test should fail, if any other error is thrown
    if len(response.data["itusers"]["objects"]):
        obj = one(one(response.data["itusers"]["objects"])["objects"])
        assert obj["user_key"] == test_data.user_key
        assert UUID(obj["itsystem_uuid"]) == test_data.itsystem
        assert UUID(obj["employee_uuid"]) == test_data.person
        assert obj["org_unit_uuid"] is None
        if test_data.engagement:
            assert UUID(obj["engagement_uuid"]) == test_data.engagement
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
async def test_create_ituser_org_unit_integration_test(
    data: DataObject,
    monkeypatch: MonkeyPatch,
    graphapi_post: GraphAPIPost,
    itsystem_uuids,
    org_uuids,
) -> None:
    monkeypatch.setattr(
        "mora.service.validation.models.GroupValidation.validate_unique_constraint",
        AsyncMock(return_value=None),
    )

    org_unit_uuid = data.draw(st.sampled_from(org_uuids))
    org_unit_from, org_unit_to = fetch_org_unit_validity(graphapi_post, org_unit_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=org_unit_from, max_value=org_unit_to or datetime.max)
    )

    if org_unit_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=org_unit_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    test_data = data.draw(
        st.builds(
            ITUserCreate,
            uuid=st.none() | st.uuids(),
            user_key=st.text(
                alphabet=st.characters(whitelist_categories=("L",)), min_size=1
            ),
            itsystem=st.sampled_from(itsystem_uuids),
            person=st.none(),
            org_unit=st.just(org_unit_uuid),
            engagement=st.none(),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

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

    # IMPORTANT: This is needed and shouldn't (I think), cause problems.
    # Since we can't avoid the "duplicate error", we set it to None at the top
    # `validate_unique_constraint.return_value = None`, this results in the mutator
    # query failing WITHOUT returning that exact error. Therefore we need to check that
    # response.data["itusers"] is not empty.
    # The test should fail, if any other error is thrown
    if len(response.data["itusers"]["objects"]):
        obj = one(one(response.data["itusers"]["objects"])["objects"])
        assert obj["user_key"] == test_data.user_key
        assert UUID(obj["itsystem_uuid"]) == test_data.itsystem
        assert UUID(obj["org_unit_uuid"]) == test_data.org_unit
        assert obj["employee_uuid"] is None
        assert obj["engagement_uuid"] is None
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
async def test_create_multiple_itusers_employee_integration_test(
    data: DataObject,
    monkeypatch: MonkeyPatch,
    graphapi_post: GraphAPIPost,
    itsystem_uuids,
    employee_uuids,
) -> None:
    monkeypatch.setattr(
        "mora.service.validation.models.GroupValidation.validate_unique_constraint",
        AsyncMock(return_value=None),
    )
    employee_uuid = data.draw(st.sampled_from(employee_uuids))
    employee_from, employee_to = fetch_employee_validity(graphapi_post, employee_uuid)

    test_data_validity_start = data.draw(
        st.datetimes(min_value=employee_from, max_value=employee_to or datetime.max)
    )

    if employee_to:
        test_data_validity_end_strat = st.datetimes(
            min_value=test_data_validity_start, max_value=employee_to
        )
    else:
        test_data_validity_end_strat = st.none() | st.datetimes(
            min_value=test_data_validity_start,
        )

    test_data = data.draw(
        st.lists(
            st.builds(
                ITUserCreate,
                uuid=st.none() | st.uuids(),
                user_key=st.text(
                    alphabet=st.characters(whitelist_categories=("L",)), min_size=1
                ),
                itsystem=st.sampled_from(itsystem_uuids),
                person=st.just(employee_uuid),
                org_unit=st.none(),
                engagement=st.uuids() | st.none(),
                validity=st.builds(
                    RAValidity,
                    from_date=st.just(test_data_validity_start),
                    to_date=test_data_validity_end_strat,
                ),
            )
        )
    )

    CREATE_ITUSERS_QUERY = """
        mutation CreateITUsers($input: [ITUserCreateInput!]!) {
            itusers_create(input: $input) {
                uuid
            }
        }
    """

    response = graphapi_post(
        CREATE_ITUSERS_QUERY, {"input": jsonable_encoder(test_data)}
    )
    assert response.errors is None
    uuids = [ituser["uuid"] for ituser in response.data["itusers_create"]]
    assert len(uuids) == len(test_data)


@given(test_data=...)
@patch("mora.graphapi.versions.latest.mutators.update_ituser", new_callable=AsyncMock)
async def test_update_ituser(update_ituser: AsyncMock, test_data: ITUserUpdate) -> None:
    """Test that pydantic jsons are passed through to update_ituser."""

    mutate_query = """
        mutation UpdateITUser($input: ITUserUpdateInput!){
            ituser_update(input: $input){
                uuid
            }
        }
    """
    updated_uuid = uuid4()
    update_ituser.return_value = updated_uuid

    payload = jsonable_encoder(test_data)

    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )

    assert response.errors is None
    assert response.data == {"ituser_update": {"uuid": str(updated_uuid)}}

    update_ituser.assert_called_with(test_data)


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
