# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from mora.graphapi.versions.latest.models import AssociationCreate
from more_itertools import one
from pydantic import parse_obj_as

from tests.conftest import GQLResponse

from ..conftest import GraphAPIPost
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all our associations."""
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_association_integration_test(
    graphapi_post: GraphAPIPost,
    org_uuids,
    employee_uuids,
    trade_union_uuids: list[UUID],
    set_settings: Callable[..., None],
) -> None:
    """Test that associations can be created in LoRa via GraphQL."""
    # Set a substitute role, to test substitute
    set_settings(CONFDB_SUBSTITUTE_ROLES='["45751985-321f-4d4f-ae16-847f0a633360"]')

    org_uuid = org_uuids[0]
    org_from, org_to = fetch_org_unit_validity(graphapi_post, org_uuid)

    start_date = org_from

    association_type_uuids = fetch_class_uuids(graphapi_post, "association_type")
    primary_type_uuids = fetch_class_uuids(graphapi_post, "primary_type")

    association_type_uuid = association_type_uuids[0]
    employee_uuid = employee_uuids[0]

    test_data = {
        "uuid": str(uuid4()),
        "org_unit": str(org_uuid),
        "person": None,
        "employee": str(employee_uuid),
        "association_type": str(association_type_uuid),
        "primary": str(primary_type_uuids[0]),
        "substitute": (str(employee_uuids[1])),
        "trade_union": str(trade_union_uuids[0]),
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutate_query = """
        mutation CreateAssociation($input: AssociationCreateInput!) {
            association_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": test_data})
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
                        substitute: substitute_uuid
                        trade_union: trade_union_uuid
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
    assert obj["user_key"] == test_data.get("user_key") or str(uuid)
    assert obj["org_unit"] == test_data["org_unit"]
    assert obj["employee"] == test_data["employee"]
    assert obj["association_type"] == test_data["association_type"]
    assert obj["primary"] == test_data["primary"]
    assert obj["substitute"] == test_data["substitute"]
    assert obj["trade_union"] == test_data["trade_union"]
    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "user_key": "-",
            "org_unit": None,
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "association_type": "45751985-321f-4d4f-ae16-847f0a633360",
            "primary": None,
            "substitute": "6ee24785-ee9a-4502-81c2-7697009c9053",
            # "trade_union": Added from fixture in the test,
            "validity": {"to": None, "from": "2017-01-01T00:00:00+01:00"},
        },
        {
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "user_key": "George",
            "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "association_type": "ef71fe9c-7901-48e2-86d8-84116e210202",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "substitute": None,
            # "trade_union": Added from fixture in the test,
            "validity": {"to": None, "from": "2017-01-01T00:00:00+01:00"},
        },
        {
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "user_key": "65922",
            "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "employee": None,
            "association_type": "d9387db2-4271-4497-a2ef-50edd6b068b1",
            "primary": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "substitute": None,
            # "trade_union": Added from fixture in the test,
            "validity": {"to": None, "from": "2017-01-12T00:00:00+01:00"},
        },
        {
            "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
            "user_key": "-",
            "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "employee": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "association_type": "45751985-321f-4d4f-ae16-847f0a633360",
            "primary": "2f16d140-d743-4c9f-9e0e-361da91a06f6",
            "substitute": "7626ad64-327d-481f-8b32-36c78eb12f8c",
            # "trade_union": Added from fixture in the test,
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "3025-10-02T00:00:00+02:00",
            },
        },
    ],
)
async def test_update_association_integration_test(
    graphapi_post: GraphAPIPost,
    test_data: dict[str, Any],
    trade_union_uuids: list[UUID],
    set_settings: Callable[..., None],
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
                            substitute: substitute_uuid
                            trade_union: trade_union_uuid
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

    # Set a substitute role, to test substitute
    set_settings(CONFDB_SUBSTITUTE_ROLES='["45751985-321f-4d4f-ae16-847f0a633360"]')

    # Add trade_union UUID from fixture `trade_union_uuids`
    test_data["trade_union"] = str(one(trade_union_uuids))

    prior_data = await query_data(test_data["uuid"])
    assert prior_data.errors is None
    assert prior_data.data is not None

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

    # Query data to check that it actually gets written to database
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
                        substitute: substitute_uuid
                        trade_union: trade_union_uuid
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
    assert query_response.errors is None
    assert query_response.data is not None

    response_data = one(
        one(query_response.data.get("associations", {})["objects"]).get("objects")
    )

    # Assert returned UUID from mutator is correct
    assert response.errors is None
    assert response.data is not None
    assert (
        response.data.get("association_update", {}).get("uuid", {}) == test_data["uuid"]
    )

    updated_test_data = {k: v or prior_data[k] for k, v in test_data.items()}

    # Assert data written to db is correct when queried
    assert query_response.errors is None
    assert updated_test_data == response_data


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


@pytest.fixture
def create_association(
    graphapi_post: GraphAPIPost,
) -> Callable:
    def inner(association_type: UUID, org_unit: UUID, person: UUID) -> UUID:
        mutate_query = """
            mutation CreateAssociation($input: AssociationCreateInput!) {
                association_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "association_type": str(association_type),
                    "org_unit": str(org_unit),
                    "person": str(person),
                    "substitute": str(uuid4()),
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["association_create"]["uuid"])

    return inner


@pytest.fixture
def update_substitute_vacant(
    graphapi_post: GraphAPIPost,
) -> Callable:
    def inner(uuid: UUID) -> UUID:
        mutate_query = """
            mutation UpdateAssociation($input: AssociationUpdateInput!) {
                association_update(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "uuid": str(uuid),
                    "substitute": None,
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["association_update"]["uuid"])

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_update_substitute_vacant(
    graphapi_post: GraphAPIPost,
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_association: Callable[..., UUID],
    update_substitute_vacant: Callable[..., UUID],
    set_settings: Callable[..., None],
) -> None:
    root = create_org_unit("root")
    person = create_person()
    substitute_role = uuid4()

    # Set a substitute role, to test substitute
    set_settings(CONFDB_SUBSTITUTE_ROLES=f'["{substitute_role}"]')
    association = create_association(substitute_role, root, person)
    update_substitute_vacant(association)

    # Test our filter
    query = """
        query Association(
          $filter: AssociationFilter!,
        ) {
          associations(filter: $filter) {
            objects {
              current {
                uuid
                substitute_uuid
              }
            }
          }
        }
    """
    response = graphapi_post(
        query,
        variables={
            "filter": {"uuids": [str(association)]},
        },
    )
    assert response.errors is None
    assert response.data

    assert (
        one(response.data["associations"]["objects"])["current"]["substitute_uuid"]
        is None
    )
