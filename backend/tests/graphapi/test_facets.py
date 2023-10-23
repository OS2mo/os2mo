# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from typing import Any
from uuid import UUID

import pytest
from hypothesis import given
from more_itertools import first
from pytest import MonkeyPatch

from ..conftest import GraphAPIPost
from .strategies import graph_data_strat
from .strategies import graph_data_uuids_strat
from mora.graphapi.shim import flatten_data
from mora.graphapi.versions.latest import dataloaders
from mora.graphapi.versions.latest.models import FacetRead


@given(test_data=graph_data_strat(FacetRead))
async def test_query_all(test_data, graphapi_post: GraphAPIPost, patch_loader):
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
        response = graphapi_post(query)

    assert response.errors is None
    assert response.data
    assert flatten_data(response.data["facets"]["objects"]) == test_data


@given(test_input=graph_data_uuids_strat(FacetRead))
async def test_query_by_uuid(test_input, graphapi_post: GraphAPIPost, patch_loader):
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
        response = graphapi_post(query, {"uuids": test_uuids})

    assert response.errors is None
    assert response.data

    # Check UUID equivalence
    result_uuids = [facet.get("uuid") for facet in response.data["facets"]["objects"]]
    assert set(result_uuids) == set(test_uuids)
    assert len(result_uuids) == len(set(test_uuids))


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
@pytest.mark.usefixtures("load_fixture_data_with_reset")
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
    response = graphapi_post(
        mutation,
        {
            "input": {
                "user_key": "my_user_key",
                "validity": {"from": "1930-01-01"},
            }
        },
    )
    assert response.errors is None
    assert response.data
    new_uuid = UUID(response.data["facet_create"]["uuid"])

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
@pytest.mark.usefixtures("load_fixture_data_with_reset")
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
@pytest.mark.usefixtures("load_fixture_data_with_reset")
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
