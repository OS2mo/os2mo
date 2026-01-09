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
from mora.graphapi.gmodels.mo import Validity as RAValidity
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.shim import execute_graphql
from mora.graphapi.versions.latest.models import ITAssociationCreate
from mora.graphapi.versions.latest.models import ITAssociationUpdate
from mora.util import POSITIVE_INFINITY
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


@given(test_data=...)
@patch(
    "mora.graphapi.versions.latest.mutators.create_itassociation",
    new_callable=AsyncMock,
)
async def test_create_itassociation_mutation_unit_test(
    create_itassociation: AsyncMock, test_data: ITAssociationCreate
) -> None:
    """Tests that the mutator function for creating a ITAssociation annotation passes through,
    with the defined pydantic model."""

    mutation = """
        mutation CreateITAssociation($input: ITAssociationCreateInput!) {
            itassociation_create(input: $input) {
                uuid
            }
        }
    """

    create_itassociation.return_value = test_data.uuid

    payload = jsonable_encoder(test_data)

    response = await execute_graphql(query=mutation, variable_values={"input": payload})
    assert response.errors is None
    assert response.data == {"itassociation_create": {"uuid": str(test_data.uuid)}}

    create_itassociation.assert_called_with(test_data)


@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay in this instance
        HealthCheck.function_scoped_fixture,
    ],
)
@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_itassociation_integration_test(
    data, graphapi_post: GraphAPIPost, org_uuids, employee_uuids, ituser_uuids
) -> None:
    """Test that ITAssociation annotations can be created in LoRa via GraphQL."""

    org_uuid = data.draw(st.sampled_from(org_uuids))
    parent_from, parent_to = fetch_org_unit_validity(graphapi_post, org_uuid)

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

    job_function_uuids = fetch_class_uuids(graphapi_post, "engagement_job_function")

    test_data = data.draw(
        st.builds(
            ITAssociationCreate,
            uuid=st.uuids() | st.none(),
            org_unit=st.just(org_uuid),
            it_user=st.sampled_from(ituser_uuids),
            person=st.sampled_from(employee_uuids),
            job_function=st.sampled_from(job_function_uuids),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutation = """
        mutation CreateITAssociation($input: ITAssociationCreateInput!) {
            itassociation_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

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
    obj = one(one(response.data["associations"]["objects"])["objects"])

    assert UUID(obj["employee"]) == test_data.person
    assert UUID(obj["it_user"]) == test_data.it_user
    assert UUID(obj["org_unit"]) == test_data.org_unit
    assert obj["user_key"] == (test_data.user_key or str(uuid))
    assert UUID(obj["job_function"]) == test_data.job_function

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
    "mora.graphapi.versions.latest.mutators.update_itassociation",
    new_callable=AsyncMock,
)
async def test_update_itassociation_unit_test(
    update_itassociation: AsyncMock, test_data: ITAssociationUpdate
) -> None:
    """Test that pydantic jsons are passed through to association_update."""

    mutate_query = """
        mutation UpdateITAssociation($input: ITAssociationUpdateInput!) {
            itassociation_update(input: $input) {
                uuid
            }
        }
    """

    itassociation_uuid_to_update = uuid4()
    update_itassociation.return_value = itassociation_uuid_to_update

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {
        "itassociation_update": {"uuid": str(itassociation_uuid_to_update)}
    }

    update_itassociation.assert_called_with(test_data)


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
