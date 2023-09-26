# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from typing import Any
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
from mora.auth.keycloak.oidc import noauth
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.graphql_utils import PrintableStr
from mora.graphapi.versions.latest.models import FacetRead
from tests.conftest import GQLResponse


@given(test_data=graph_data_strat(FacetRead))
async def test_query_all(test_data, graphapi_post, patch_loader):
    """Test that we can query all attributes of the facets data model."""
    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
        query = """
            query {
                facets {
                    objects {
                        objects {
                            uuid
                            user_key
                            description
                            parent_uuid
                            org_uuid
                            published
                            type
                            validity {
                                from
                                to
                            }
                        }
                    }
                }
            }
        """
        response: GQLResponse = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["facets"]["objects"]) == test_data


@given(test_input=graph_data_uuids_strat(FacetRead))
async def test_query_by_uuid(test_input, graphapi_post, patch_loader):
    """Test that we can query facets by UUID."""
    test_data, test_uuids = test_input

    # Patch dataloader
    with MonkeyPatch.context() as patch:
        patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
        query = """
                query TestQuery($uuids: [UUID!]) {
                    facets(filter: {uuids: $uuids}) {
                        objects {
                            uuid
                        }
                    }
                }
            """
        response: GQLResponse = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [facet.get("uuid") for facet in response.data["facets"]["objects"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


def read_facets_helper(graphapi_post, query: str, extract: str) -> dict[UUID, Any]:
    response: GQLResponse = graphapi_post(query)
    assert response.errors is None
    assert response.data
    return {UUID(x["uuid"]): x[extract] for x in response.data["facets"]["objects"]}


read_facets = partial(
    read_facets_helper,
    query="""
        query ReadITFacet {
            facets {
                objects {
                    uuid
                    current {
                        uuid
                        user_key
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """,
    extract="current",
)

read_history = partial(
    read_facets_helper,
    query="""
        query ReadITFacet {
            facets(filter: {from_date: null, to_date: null}) {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """,
    extract="objects",
)


OPTIONAL = {
    "published": st.sampled_from(["Publiceret", "IkkePubliceret"]),
}


@st.composite
def write_strat(draw):
    required = {
        "user_key": st.from_regex(PrintableStr.regex),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=OPTIONAL))
    return st_dict


def prepare_mutator_data(test_data):
    if "type_" in test_data:
        test_data["type"] = test_data.pop("type_")

    """Change UUID types to string."""
    for k, v in test_data.items():
        if type(v) == UUID:
            test_data[k] = str(v)

    return test_data


def prepare_query_data(test_data, query_response):
    entries_to_remove = OPTIONAL.keys()
    for k in entries_to_remove:
        test_data.pop(k, None)

    td = {k: v for k, v in test_data.items() if v is not None}

    query_dict = (
        one(query_response.data.get("facets").get("objects"))["current"]
        if isinstance(query_response.data, dict)
        else {}
    )
    query = {k: v for k, v in query_dict.items() if k in td.keys()}

    return test_data, query


"""
Facets mutator tests.

Tests are generated by Hypothesis based on FacetCreate.
"""


@given(test_data=write_strat())
@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_create_facet(test_data, graphapi_post):
    """Integrationtest for create facet mutator."""

    mutate_query = """
        mutation CreateFacet($input: FacetCreateInput!) {
            facet_create(input: $input) {
                uuid
            }
        }
    """

    test_data = prepare_mutator_data(test_data)

    mut_response: GQLResponse = graphapi_post(
        query=mutate_query, variables={"input": test_data}
    )

    assert mut_response.data
    response_uuid = (
        mut_response.data.get("facet_create", {}).get("uuid", {})
        if isinstance(mut_response.data, dict)
        else {}
    )

    """Query data to check that it actually gets written to database"""
    query_query = """
        query ($uuid: [UUID!]!) {
            facets(filter: {uuids: $uuid}) {
                objects {
                    current {
                        uuid
                        type
                        org_uuid
                        user_key
                        published
                        parent_uuid
                    }
                }
            }
        }
    """
    query_response = await execute_graphql(
        query=query_query,
        variable_values={"uuid": str(response_uuid)},
    )

    test_data, query = prepare_query_data(test_data, query_response)

    """Assert response returned by mutation."""
    assert mut_response.errors is None
    assert mut_response.data
    if test_data.get("uuid"):
        assert response_uuid == test_data["uuid"]

    """Assert response returned by quering data written."""
    assert query_response.errors is None
    assert query == test_data


@given(test_data=write_strat())
@patch("mora.graphapi.versions.latest.mutators.create_facet", new_callable=AsyncMock)
async def test_unit_create_class(create_facet: AsyncMock, test_data: Any):
    """Unit test for create facet mutator."""

    query = """
        mutation CreateFacet($input: FacetCreateInput!){
            facet_create(input: $input){
                uuid
            }
        }
    """

    if test_data.get("uuid"):
        created_uuid = test_data["uuid"]
    else:
        created_uuid = uuid4()
    create_facet.return_value = created_uuid

    payload = jsonable_encoder(test_data)

    response = await execute_graphql(
        query=query,
        variable_values={"input": payload},
        context_value={"org_loader": AsyncMock(), "get_token": noauth},
    )

    assert response.errors is None
    assert response.data == {"facet_create": {"uuid": str(created_uuid)}}


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_integration_delete_facet() -> None:
    read_query = """
        query ($uuid: [UUID!]!) {
          facets(filter: {uuids: $uuid}) {
            objects {
              current {
                uuid
                user_key
              }
            }
          }
        }
    """
    facet_uuid = "1a6045a2-7a8e-4916-ab27-b2402e64f2be"

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": facet_uuid},
    )
    assert response.errors is None
    assert response.data == {
        "facets": {
            "objects": [
                {"current": {"user_key": "engagement_job_function", "uuid": facet_uuid}}
            ]
        }
    }

    delete_query = """
        mutation ($uuid: UUID!) {
          facet_delete(uuid: $uuid) {
            uuid
          }
        }
    """
    response = await execute_graphql(
        query=delete_query,
        variable_values={"uuid": facet_uuid},
    )
    assert response.errors is None
    assert response.data == {"facet_delete": {"uuid": facet_uuid}}

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": facet_uuid},
    )
    assert response.errors is None
    assert response.data == {"facets": {"objects": []}}


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_update_facet() -> None:
    """Unit test for create facet mutator."""
    read_query = """
        query ($uuid: [UUID!]!) {
          facets(filter: {uuids: $uuid}) {
            objects {
              current {
                uuid
                user_key
              }
            }
          }
        }
    """
    facet_uuid = "baddc4eb-406e-4c6b-8229-17e4a21d3550"

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": facet_uuid},
    )
    assert response.errors is None
    assert one(response.data.keys()) == "facets"
    klass = one(response.data["facets"]["objects"])["current"]
    assert klass == {
        "uuid": facet_uuid,
        "user_key": "employee_address_type",
    }

    update_query = """
        mutation UpdateFacet($input: FacetUpdateInput!) {
            facet_update(input: $input) {
                uuid
            }
        }
    """
    response = await execute_graphql(
        query=update_query,
        variable_values={
            "input": {"user_key": "New Value 1", "uuid": facet_uuid},
        },
    )
    assert response.errors is None
    assert response.data == {"facet_update": {"uuid": facet_uuid}}

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": facet_uuid},
    )
    assert response.errors is None
    assert one(response.data.keys()) == "facets"
    klass = one(response.data["facets"]["objects"])["current"]
    assert klass == {
        "uuid": facet_uuid,
        "user_key": "New Value 1",
    }

    delete_query = """
        mutation ($uuid: UUID!) {
          facet_delete(uuid: $uuid) {
            uuid
          }
        }
    """
    response = await execute_graphql(
        query=delete_query,
        variable_values={"uuid": facet_uuid},
    )
    assert response.errors is None
    assert response.data == {"facet_delete": {"uuid": facet_uuid}}

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": facet_uuid},
    )
    assert response.errors is None
    assert response.data == {"facets": {"objects": []}}

    update_query = """
        mutation UpdateFacet($input: FacetUpdateInput!) {
            facet_update(input: $input) {
                uuid
            }
        }
    """
    response = await execute_graphql(
        query=update_query,
        variable_values={
            "input": {
                "user_key": "New Value 2",
                "uuid": facet_uuid,
            },
        },
    )
    assert response.errors is None
    assert response.data == {"facet_update": {"uuid": facet_uuid}}

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": facet_uuid},
    )
    assert response.errors is None
    assert one(response.data.keys()) == "facets"
    klass = one(response.data["facets"]["objects"])["current"]
    assert klass == {
        "uuid": facet_uuid,
        "user_key": "New Value 2",
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_terminate_facet(graphapi_post) -> None:
    """Test that we can terminate facets."""
    # Verify existing state
    facet_map = read_facets(graphapi_post)
    assert len(facet_map.keys()) == 18

    facet_to_terminate = UUID("1a6045a2-7a8e-4916-ab27-b2402e64f2be")
    assert facet_to_terminate in facet_map.keys()

    # Terminate a facet
    mutation = """
        mutation TerminateFacet($input: FacetTerminateInput!) {
            facet_terminate(input: $input) {
                uuid
            }
        }
    """
    response: GQLResponse = graphapi_post(
        mutation,
        {"input": {"uuid": str(facet_to_terminate), "validity": {"to": "1990-01-01"}}},
    )
    assert response.errors is None
    assert response.data
    terminated_uuid = UUID(response.data["facet_terminate"]["uuid"])
    assert terminated_uuid == facet_to_terminate

    # Verify modified state
    new_facet_map = read_history(graphapi_post)
    assert new_facet_map.keys() == set(facet_map.keys())

    # Verify facet history
    facet_history = new_facet_map[terminated_uuid]
    assert facet_history == [
        {
            "uuid": str(facet_to_terminate),
            "user_key": "engagement_job_function",
            "validity": {
                "from": "1900-01-01T00:00:00+01:00",
                "to": "1990-01-01T00:00:00+01:00",
            },
        }
    ]
