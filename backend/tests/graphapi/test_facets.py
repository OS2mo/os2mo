# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from typing import Any
from uuid import UUID

import pytest
from more_itertools import first

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost) -> None:
    """Test that we can query all attributes of the facets data model."""
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
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data


def read_facets_helper(
    graphapi_post: GraphAPIPost, query: str, extract: str
) -> dict[UUID, Any]:
    response = graphapi_post(query)
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


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_facet(graphapi_post):
    """Test that we can create new facets."""
    # Verify existing state
    facet_map = read_facets(graphapi_post)
    assert len(facet_map.keys()) == 18

    # Create new facet
    mutation = """
        mutation CreateFacet($input: FacetCreateInput!) {
            facet_create(input: $input) {
                uuid
            }
        }
    """
    facet_uuid = UUID("4445ab30-42c3-4b69-b65b-09136cd77e18")
    response = graphapi_post(
        mutation,
        {
            "input": {
                "uuid": str(facet_uuid),
                "user_key": "my_user_key",
                "validity": {"from": "1930-01-01"},
            }
        },
    )
    assert response.errors is None
    assert response.data
    new_uuid = UUID(response.data["facet_create"]["uuid"])
    assert new_uuid == facet_uuid

    # Verify modified state
    new_facet_map = read_history(graphapi_post)
    assert new_facet_map.keys() == set(facet_map.keys()) | {new_uuid}

    # Verify new object
    facet_history = new_facet_map[new_uuid]
    assert facet_history == [
        {
            "uuid": str(new_uuid),
            "user_key": "my_user_key",
            "validity": {"from": "1930-01-01T00:00:00+01:00", "to": None},
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_facet(graphapi_post) -> None:
    """Test that we can update facets."""
    # Verify existing state
    facet_map = read_facets(graphapi_post)
    assert len(facet_map.keys()) == 18

    facet_to_update = UUID("1a6045a2-7a8e-4916-ab27-b2402e64f2be")
    assert facet_to_update in facet_map.keys()

    # Update a facet
    mutation = """
        mutation UpdateFacet($input: FacetUpdateInput!) {
            facet_update(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        mutation,
        {
            "input": {
                "uuid": str(facet_to_update),
                "user_key": "my_user_key",
                "validity": {"from": "1990-01-01"},
            }
        },
    )
    assert response.errors is None
    assert response.data
    updated_uuid = UUID(response.data["facet_update"]["uuid"])
    assert updated_uuid == facet_to_update

    # Verify modified state
    new_facet_map = read_history(graphapi_post)
    assert new_facet_map.keys() == set(facet_map.keys())

    # Verify facet history
    facet_history = new_facet_map[facet_to_update]
    assert facet_history == [
        {
            "uuid": str(facet_to_update),
            "user_key": "engagement_job_function",
            "validity": {
                "from": "1900-01-01T00:00:00+01:00",
                "to": "1989-12-31T00:00:00+01:00",
            },
        },
        {
            "uuid": str(facet_to_update),
            "user_key": "my_user_key",
            "validity": {"from": "1990-01-01T00:00:00+01:00", "to": None},
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_delete_facet(graphapi_post) -> None:
    """Test that we can delete facets."""
    # Verify existing state
    facet_map = read_facets(graphapi_post)
    assert len(facet_map.keys()) == 18

    facet_to_delete = first(facet_map)

    # Delete a facet
    mutation = """
        mutation DeleteFacet($uuid: UUID!) {
            facet_delete(uuid: $uuid) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"uuid": str(facet_to_delete)})
    assert response.errors is None
    assert response.data
    deleted_uuid = UUID(response.data["facet_delete"]["uuid"])
    assert deleted_uuid == facet_to_delete

    # Verify modified state
    new_facet_map = read_history(graphapi_post)
    assert new_facet_map.keys() == set(facet_map.keys()) - {facet_to_delete}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
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
    response = graphapi_post(
        mutation,
        {"input": {"uuid": str(facet_to_terminate), "to": "1990-01-01"}},
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
