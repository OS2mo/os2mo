# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime as dt
from datetime import datetime
from unittest import mock
from unittest.mock import AsyncMock
from unittest.mock import patch
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from more_itertools import one
from pydantic import parse_obj_as
from pytest import MonkeyPatch

from ..conftest import GraphAPIPost
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity
from mora import lora
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.association import terminate_association
from mora.graphapi.versions.latest.models import AssociationCreate
from mora.graphapi.versions.latest.models import AssociationTerminate
from mora.graphapi.versions.latest.models import AssociationUpdate
from mora.util import POSITIVE_INFINITY
from ramodels.mo import Validity as RAValidity
from ramodels.mo.details import AssociationRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(AssociationRead))
def test_query_all(test_data, graphapi_post: GraphAPIPost, patch_loader):
    """Test that we can query all our associations."""
    # JSON encode test data
    test_data = jsonable_encoder(test_data)

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                associations {
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
                            dynamic_class_uuid
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
    assert flatten_data(response.data["associations"]["objects"]) == test_data


@given(test_input=graph_data_uuids_strat(AssociationRead))
def test_query_by_uuid(test_input, graphapi_post: GraphAPIPost, patch_loader):
    """Test that we can query associations by UUID."""
    # Sample UUIDs
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    associations(filter: {uuids: $uuids}) {
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
        assoc.get("uuid") for assoc in response.data["associations"]["objects"]
    ]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 2),
        # Employee filters
        ({"employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"}, 2),
        ({"employees": "6ee24785-ee9a-4502-81c2-7697009c9053"}, 0),
        (
            {
                "employees": [
                    "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    "6ee24785-ee9a-4502-81c2-7697009c9053",
                ]
            },
            2,
        ),
        # Organisation Unit filter
        ({"org_units": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"}, 2),
        ({"org_units": "2874e1dc-85e6-4269-823a-e1125484dfd3"}, 0),
        (
            {
                "org_units": [
                    "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                ]
            },
            2,
        ),
        # Association type filter
        ({"association_types": "62ec821f-4179-4758-bfdf-134529d186e9"}, 2),
        ({"association_type_user_keys": "medl"}, 2),
        ({"association_types": "8eea787c-c2c7-46ca-bd84-2dd50f47801e"}, 0),
        ({"association_type_user_keys": "projektleder"}, 0),
        ({"association_types": "45751985-321f-4d4f-ae16-847f0a633360"}, 0),
        ({"association_type_user_keys": "teammedarbejder"}, 0),
        (
            {
                "association_types": [
                    "62ec821f-4179-4758-bfdf-134529d186e9",
                    "8eea787c-c2c7-46ca-bd84-2dd50f47801e",
                ]
            },
            2,
        ),
        (
            {
                "association_type_user_keys": "medl",
                "association_types": "8eea787c-c2c7-46ca-bd84-2dd50f47801e",
            },
            2,
        ),
        # Mixed filters
        (
            {
                "employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_units": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            },
            0,
        ),
        (
            {
                "employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_units": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            },
            2,
        ),
        (
            {
                "employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_units": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "association_type_user_keys": "medl",
            },
            2,
        ),
        (
            {
                "employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_units": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                "association_types": "8eea787c-c2c7-46ca-bd84-2dd50f47801e",
            },
            0,
        ),
    ],
)
async def test_association_filters(
    graphapi_post: GraphAPIPost, filter, expected
) -> None:
    """Test filters on associations."""
    association_query = """
        query Associations($filter: AssociationFilter!) {
            associations(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(association_query, variables=dict(filter=filter))
    assert response.errors is None
    assert len(response.data["associations"]["objects"]) == expected


@given(test_data=st.builds(AssociationCreate, person=st.uuids(), employee=st.none()))
@patch(
    "mora.graphapi.versions.latest.mutators.create_association", new_callable=AsyncMock
)
async def test_create_association(
    create_association: AsyncMock, test_data: AssociationCreate
) -> None:
    """Test that pydantic jsons are passed through to association_create."""

    mutate_query = """
        mutation CreateAssociation($input: AssociationCreateInput!) {
            association_create(input: $input) {
                uuid
            }
        }
    """
    created_uuid = uuid4()
    create_association.return_value = created_uuid

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {"association_create": {"uuid": str(created_uuid)}}

    create_association.assert_called_with(test_data)


@given(data=st.data())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_association_integration_test(
    data, graphapi_post: GraphAPIPost, org_uuids, employee_uuids
) -> None:
    """Test that associations can be created in LoRa via GraphQL."""

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

    association_type_uuids = fetch_class_uuids(graphapi_post, "association_type")
    primary_type_uuids = fetch_class_uuids(graphapi_post, "primary_type")

    test_data = data.draw(
        st.builds(
            AssociationCreate,
            org_unit=st.just(org_uuid),
            person=st.none(),
            employee=st.sampled_from(employee_uuids),
            association_type=st.sampled_from(association_type_uuids),
            primary=st.sampled_from(primary_type_uuids),
            validity=st.builds(
                RAValidity,
                from_date=st.just(test_data_validity_start),
                to_date=test_data_validity_end_strat,
            ),
        )
    )

    mutate_query = """
        mutation CreateAssociation($input: AssociationCreateInput!) {
            association_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": jsonable_encoder(test_data)})
    assert response.errors is None
    uuid = UUID(response.data["association_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            associations(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        org_unit: org_unit_uuid
                        employee: employee_uuid
                        association_type: association_type_uuid
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
    obj = one(one(response.data["associations"]["objects"])["objects"])
    assert obj["user_key"] == test_data.user_key or str(uuid)
    assert UUID(obj["org_unit"]) == test_data.org_unit
    assert UUID(obj["employee"]) == test_data.employee
    assert UUID(obj["association_type"]) == test_data.association_type
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "user_key": "-",
            "org_unit": None,
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "association_type": "62ec821f-4179-4758-bfdf-134529d186e9",
            "primary": None,
            "validity": {"to": None, "from": "2017-01-01T00:00:00+01:00"},
        },
        {
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "user_key": "George",
            "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "association_type": "ef71fe9c-7901-48e2-86d8-84116e210202",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "validity": {"to": None, "from": "2017-01-01T00:00:00+01:00"},
        },
        {
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "user_key": "65922",
            "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "employee": None,
            "association_type": "d9387db2-4271-4497-a2ef-50edd6b068b1",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "validity": {"to": None, "from": "2017-01-12T00:00:00+01:00"},
        },
        {
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "user_key": "-",
            "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "association_type": "8eea787c-c2c7-46ca-bd84-2dd50f47801e",
            "primary": "2f16d140-d743-4c9f-9e0e-361da91a06f6",
            "validity": {
                "to": "2025-10-02T00:00:00+02:00",
                "from": "2017-01-01T00:00:00+01:00",
            },
        },
    ],
)
async def test_update_association_integration_test(
    graphapi_post: GraphAPIPost, test_data
) -> None:
    async def query_data(uuid: str) -> GQLResponse:
        query = """
            query ($uuid: [UUID!]!) {
                __typename
                associations(filter: {uuids: $uuid}){
                    objects {
                        objects {
                            uuid
                            user_key
                            org_unit: org_unit_uuid
                            employee: employee_uuid
                            association_type: association_type_uuid
                            primary: primary_uuid
                            validity {
                                to
                                from
                            }
                        }
                    }
                }
            }

        """
        response = graphapi_post(query=query, variables={"uuid": uuid})

        return response

    prior_data = await query_data(test_data["uuid"])

    prior_data = one(
        one(prior_data.data.get("associations", {})["objects"]).get("objects")
    )

    mutate_query = """
        mutation UpdateAssociation($input: AssociationUpdateInput!) {
            association_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": jsonable_encoder(test_data)})

    """Query data to check that it actually gets written to database"""
    query_query = """
        query ($uuid: [UUID!]!){
            __typename
            associations(filter: {uuids: $uuid}){
                objects {
                    objects {
                        uuid
                        user_key
                        org_unit: org_unit_uuid
                        employee: employee_uuid
                        association_type: association_type_uuid
                        primary: primary_uuid
                        validity {
                            to
                            from
                        }
                    }
                }
            }
        }

    """

    query_response = graphapi_post(
        query=query_query, variables={"uuid": test_data["uuid"]}
    )

    response_data = one(
        one(query_response.data.get("associations", {})["objects"]).get("objects")
    )

    """Assert returned UUID from mutator is correct"""
    assert response.errors is None
    assert (
        response.data.get("association_update", {}).get("uuid", {}) == test_data["uuid"]
    )

    updated_test_data = {k: v or prior_data[k] for k, v in test_data.items()}

    """Asssert data written to db is correct when queried"""
    assert query_response.errors is None
    assert updated_test_data == response_data


@given(test_data=...)
@patch(
    "mora.graphapi.versions.latest.mutators.update_association", new_callable=AsyncMock
)
async def test_update_association_unit_test(
    update_association: AsyncMock, test_data: AssociationUpdate
) -> None:
    """Test that pydantic jsons are passed through to association_update."""

    mutate_query = """
        mutation UpdateAssociation($input: AssociationUpdateInput!) {
            association_update(input: $input) {
                uuid
            }
        }
    """

    association_uuid_to_update = uuid4()
    update_association.return_value = association_uuid_to_update

    payload = jsonable_encoder(test_data)
    response = await execute_graphql(
        query=mutate_query, variable_values={"input": payload}
    )
    assert response.errors is None
    assert response.data == {
        "association_update": {"uuid": str(association_uuid_to_update)}
    }

    update_association.assert_called_with(test_data)


@given(
    given_uuid=st.uuids(),
    given_validity_dts=st.tuples(st.datetimes() | st.none(), st.datetimes()).filter(
        lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
    ),
)
async def test_association_terminate(given_uuid, given_validity_dts):
    from_date, to_date = given_validity_dts

    # The terminate logic have a check that verifies we don't use times other than:
    # 00:00:00, to the endpoint.. so if we get one of these from hypothesis, we will
    # expect an exception.
    expect_exception = False
    if to_date.time() != dt.time.min:
        expect_exception = True

    test_data = AssociationTerminate(
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
            terminate_result_uuid = await terminate_association(input=test_data)
        except Exception as e:
            caught_exception = e

    # Assert
    if not expect_exception:
        assert terminate_result_uuid == test_data.uuid
    else:
        assert caught_exception is not None


@pytest.mark.parametrize(
    "person,employee,exception",
    [
        (False, False, "Must set one of 'person' and 'employee'"),
        (True, False, None),
        (False, True, None),
        (True, True, "Can only set one of 'person' and 'employee'"),
    ],
)
def test_employee_person_exclusivity(
    person: bool, employee: bool, exception: str | None
) -> None:
    """Test that employee and person are mutually exclusive."""

    input_dict = {
        "validity": {"from": "2020-01-01"},
        "org_unit": uuid4(),
        "association_type": uuid4(),
    }
    if person:
        input_dict["person"] = uuid4()
    if employee:
        input_dict["employee"] = uuid4()

    if exception:
        with pytest.raises(HTTPException) as excinfo:
            parse_obj_as(AssociationCreate, input_dict)
        assert exception in str(excinfo.value)
    else:
        parse_obj_as(AssociationCreate, input_dict)
