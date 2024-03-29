# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from typing import Any
from typing import Protocol
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from more_itertools import all_equal
from more_itertools import first
from more_itertools import one
from strawberry.types import Info

from mora.graphapi.versions.latest.mutators import check_etags
from mora.graphapi.versions.latest.types import ETag
from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost
from tests.conftest import YieldFixture


class AsyncGraphAPIPost(Protocol):
    async def __call__(
        self, query: str, variables: dict[str, Any] | None = None, url: str = ""
    ) -> GQLResponse:
        ...


@pytest.fixture
async def async_admin_client(
    fastapi_admin_test_app: FastAPI,
) -> YieldFixture[AsyncClient]:
    async with AsyncClient(
        app=fastapi_admin_test_app, base_url="http://testserver/"
    ) as ac:
        yield ac


@pytest.fixture
def async_graphapi_post(
    async_admin_client: AsyncClient, latest_graphql_url: str
) -> YieldFixture[AsyncGraphAPIPost]:
    async def _post(
        query: str,
        variables: dict[str, Any] | None = None,
        url: str = latest_graphql_url,
    ) -> GQLResponse:
        response = await async_admin_client.post(
            url, json={"query": query, "variables": variables}
        )
        data = response.json().get("data")
        errors = response.json().get("errors")
        extensions = response.json().get("extensions")
        status_code = response.status_code
        return GQLResponse(
            data=data, errors=errors, extensions=extensions, status_code=status_code
        )

    yield _post


query_facet = """
    query ReadFacet($uuid: UUID!) {
      facets(filter: {uuids: [$uuid]}) {
        objects {
          uuid
          etag
          current {
            user_key
          }
        }
      }
    }
"""
query_class = """
    query ReadClass($uuid: UUID!) {
      classes(filter: {uuids: [$uuid]}) {
        objects {
          uuid
          etag
          current {
            user_key
          }
        }
      }
    }
"""
update_facet = """
    mutation UpdateFacet($input: FacetUpdateInput!, $etags: [Etag!]!) {
      facet_update(input: $input, etags: $etags) {
        uuid
      }
    }
"""
update_class = """
    mutation UpdateClass($input: ClassUpdateInput!, $etags: [Etag!]!) {
      class_update(input: $input, etags: $etags) {
        uuid
      }
    }
"""


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_duplicate_update_rejected(graphapi_post: GraphAPIPost) -> None:
    """Test that the last of two duplicate writes is rejected."""
    facet_uuid = "1a6045a2-7a8e-4916-ab27-b2402e64f2be"

    # Read and assert current state
    response = graphapi_post(query_facet, {"uuid": facet_uuid})
    assert response.errors is None
    assert response.data
    facet = one(response.data["facets"]["objects"])
    assert facet["uuid"] == facet_uuid
    assert facet["current"]["user_key"] == "engagement_job_function"

    new_facet_name = "new_facet_name"
    payload = {
        "input": {
            "uuid": facet_uuid,
            "validity": {"from": "2000-01-01"},
            "user_key": new_facet_name,
        },
        "etags": [facet["etag"]],
    }

    # Write a new state, having backend checking the etag as we do
    response = graphapi_post(update_facet, payload)
    assert response.errors is None
    assert response.data
    facet_update = response.data["facet_update"]
    assert facet_update["uuid"] == facet_uuid

    # Read and assert the new state
    response = graphapi_post(query_facet, {"uuid": facet_uuid})
    assert response.errors is None
    assert response.data
    new_facet = one(response.data["facets"]["objects"])
    assert new_facet["uuid"] == facet_uuid
    assert new_facet["current"]["user_key"] == new_facet_name
    # New state should mean new etag
    assert new_facet["etag"] != facet["etag"]

    # Try to do the duplicate write, should fail because etag changed
    response = graphapi_post(update_facet, payload)
    assert response.errors is not None
    error = one(response.errors)
    assert error["message"] == "ETag mismatch, please try again"

    # Do the duplicate write with the new etag, should succeed
    payload["etags"] = [new_facet["etag"]]
    response = graphapi_post(update_facet, payload)
    assert response.errors is None
    assert response.data
    facet_update = response.data["facet_update"]
    assert facet_update["uuid"] == facet_uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_unrelated_etag_rejects(graphapi_post: GraphAPIPost) -> None:
    """Test that a facet write can fail on a class etag."""
    facet_uuid = "1a6045a2-7a8e-4916-ab27-b2402e64f2be"
    class_uuid = "4e337d8e-1fd2-4449-8110-e0c8a22958ed"

    # Read and assert current facet state
    response = graphapi_post(query_facet, {"uuid": facet_uuid})
    assert response.errors is None
    assert response.data
    facet = one(response.data["facets"]["objects"])
    assert facet["uuid"] == facet_uuid
    assert facet["current"]["user_key"] == "engagement_job_function"

    # Read and assert current class state
    response = graphapi_post(query_class, {"uuid": class_uuid})
    assert response.errors is None
    assert response.data
    clazz = one(response.data["classes"]["objects"])
    assert clazz["uuid"] == class_uuid
    assert clazz["current"]["user_key"] == "BrugerPostadresse"

    # Write a new class state, ignoring etag
    new_class_name = "new_class_name"
    payload = {
        "input": {
            "uuid": class_uuid,
            "facet_uuid": facet_uuid,
            "validity": {"from": "2000-01-01"},
            "user_key": new_class_name,
            "name": new_class_name,
        },
        # This forcefully overrides no matter if updates have been made since our read
        "etags": [],
    }
    response = graphapi_post(update_class, payload)
    assert response.errors is None
    assert response.data
    facet_update = response.data["class_update"]
    assert facet_update["uuid"] == class_uuid

    # Attempt to write a new facet state, should fail because class etag changed
    new_facet_name = "new_facet_name"
    payload = {
        "input": {
            "uuid": facet_uuid,
            "validity": {"from": "2000-01-01"},
            "user_key": new_facet_name,
        },
        "etags": [
            facet["etag"],
            clazz["etag"],
        ],
    }
    response = graphapi_post(update_facet, payload)
    assert response.errors is not None
    error = one(response.errors)
    assert error["message"] == "ETag mismatch, please try again"

    # If we only depend on the facet etag it should pass
    payload["etags"] = [facet["etag"]]
    response = graphapi_post(update_facet, payload)
    assert response.errors is None
    assert response.data
    facet_update = response.data["facet_update"]
    assert facet_update["uuid"] == facet_uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_race_conditioned_writes_get_rejected(
    graphapi_post: GraphAPIPost, async_graphapi_post: AsyncGraphAPIPost
) -> None:
    """Test that one of two race conditioned writes fail."""
    facet_uuid = "1a6045a2-7a8e-4916-ab27-b2402e64f2be"

    # Read and assert current state
    response = graphapi_post(query_facet, {"uuid": facet_uuid})
    assert response.errors is None
    assert response.data
    facet = one(response.data["facets"]["objects"])
    assert facet["uuid"] == facet_uuid
    assert facet["current"]["user_key"] == "engagement_job_function"

    concurrent_writes = 5
    payloads = [
        {
            "input": {
                "uuid": facet_uuid,
                "validity": {"from": "2000-01-01"},
                "user_key": str(i),
            },
            "etags": [facet["etag"]],
        }
        for i in range(concurrent_writes)
    ]

    barrier = asyncio.Barrier(concurrent_writes)

    async def barriered_check_etags(info: Info, etags: list[ETag]) -> None:
        # Synchronize to make sure all callers got to here before continuing
        await barrier.wait()

        # Pass the etags check
        await check_etags(info, etags)

    # Mock check_etags, to make sure all writes are inside, before continuing
    with patch(
        "mora.graphapi.versions.latest.mutators.check_etags", new=barriered_check_etags
    ):
        calls = [
            async_graphapi_post(update_facet, payloads[i])
            for i in range(concurrent_writes)
        ]
        results = await asyncio.gather(*calls, return_exceptions=True)
        error_messages = [
            one(result.errors)["message"]
            for result in results
            if result.errors is not None
        ]
        datas = [result.data for result in results if result.data is not None]
        # All but one should have been rejected
        assert len(error_messages) == concurrent_writes - 1
        assert all_equal(error_messages)
        assert first(error_messages) == "ErrorCodes.E_SERIALIZATION_FAILURE"
        # Exactly one should have passed
        facet_update = one(datas)["facet_update"]
        assert facet_update["uuid"] == facet_uuid
