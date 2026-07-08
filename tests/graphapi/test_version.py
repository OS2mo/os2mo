# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_unauthorized_version_endpoint(
    raw_client: TestClient, latest_graphql_url: str
) -> None:
    """Version endpoint requires authentication."""
    mo_version_query = """
        query {
            version {
                mo_hash
                mo_version
            }
        }
    """
    response = raw_client.post(latest_graphql_url, json={"query": mo_version_query})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"] is None
    assert one(payload["errors"])["message"] == "User is not authenticated"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_authorized_version_endpoint(graphapi_post: GraphAPIPost) -> None:
    """Version endpoint works for authenticated users."""
    mo_version_query = """
        query {
            version {
                mo_hash
                mo_version
            }
        }
    """
    response = graphapi_post(mo_version_query)
    assert response.errors is None
    assert response.data == {
        "version": {
            "mo_hash": ANY,
            "mo_version": "HEAD",
        }
    }
