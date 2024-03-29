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

from mora.graphapi.versions.latest.mutators import purge_old_idempotency_tokens
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


create_facet = """
    mutation CreateFacet($input: FacetCreateInput!, $idempotency_token: UUID!) {
      facet_create(input: $input, idempotency_token: $idempotency_token) {
        uuid
      }
    }
"""

# We cannot read out current.user_key, because the transaction is closed at this point
# create_facet = """
#    mutation CreateFacet($input: FacetCreateInput!, $idempotency_token: UUID!) {
#      facet_create(input: $input, idempotency_token: $idempotency_token) {
#        uuid
#        current {
#          user_key
#        }
#      }
#    }
# """


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_idempotency_on_duplicate_creates(graphapi_post: GraphAPIPost) -> None:
    """Test that duplicate creates are idempotent."""
    idempotency_token = "30636129-f44b-46b0-9c19-5e80d47ecfb4"

    payload = {
        "input": {"user_key": "1", "validity": {}},
        "idempotency_token": idempotency_token,
    }

    # Create a facet with an idempotency_token
    response = graphapi_post(create_facet, payload)
    assert response.errors is None
    assert response.data
    facet1 = response.data["facet_create"]
    # assert facet1["current"]["user_key"] == "1"

    # Send a duplicate create request
    response = graphapi_post(create_facet, payload)
    assert response.errors is None
    assert response.data
    facet2 = response.data["facet_create"]
    # assert facet2["current"]["user_key"] == "1"

    # We expect to have gotten the same result from both
    assert facet1["uuid"] == facet2["uuid"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_idempotency_on_different_creates(graphapi_post: GraphAPIPost) -> None:
    """Test that different creates are idempotent."""
    idempotency_token = "30636129-f44b-46b0-9c19-5e80d47ecfb4"

    payload_1 = {
        "input": {"user_key": "1", "validity": {}},
        "idempotency_token": idempotency_token,
    }
    payload_2 = {
        "input": {"user_key": "2", "validity": {}},
        "idempotency_token": idempotency_token,
    }

    # Create a facet with an idempotency_token
    response = graphapi_post(create_facet, payload_1)
    assert response.errors is None
    assert response.data
    facet1 = response.data["facet_create"]
    # assert facet1["current"]["user_key"] == "1"

    # Send a duplicate create request
    response = graphapi_post(create_facet, payload_2)
    assert response.errors is None
    assert response.data
    facet2 = response.data["facet_create"]
    # Notice that this returns 1, because of idempotency
    # assert facet2["current"]["user_key"] == "1"

    # We expect to have gotten the same result from both
    assert facet1["uuid"] == facet2["uuid"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_idempotency_on_race_condition(
    graphapi_post: GraphAPIPost, async_graphapi_post: AsyncGraphAPIPost
) -> None:
    """Test that the last of two duplicate writes is rejected."""
    idempotency_token = "30636129-f44b-46b0-9c19-5e80d47ecfb4"

    concurrent_writes = 5

    payloads = [
        {
            "input": {"user_key": str(i), "validity": {}},
            "idempotency_token": idempotency_token,
        }
        for i in range(concurrent_writes)
    ]

    barrier = asyncio.Barrier(concurrent_writes)

    async def barriered_purge_old_idempotency_tokens() -> None:
        # Synchronize to make sure all callers got to here before continuing
        await barrier.wait()

        # Purge idempotency_tokens
        await purge_old_idempotency_tokens()

    # Mock purge_old_idempotency_tokens, to make sure all writes are inside, before continuing
    with patch(
        "mora.graphapi.versions.latest.mutators.purge_old_idempotency_tokens",
        new=barriered_purge_old_idempotency_tokens,
    ):
        calls = [
            async_graphapi_post(create_facet, payloads[i])
            for i in range(concurrent_writes)
        ]
        results = await asyncio.gather(*calls, return_exceptions=True)
        errors = [result.errors for result in results]
        assert errors == [None] * concurrent_writes

        datas = [result.data for result in results]
        assert all_equal(datas)
