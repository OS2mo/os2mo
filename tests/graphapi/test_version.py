# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_unauthorized_version_endpoint(
    raw_client: TestClient, latest_graphql_url: str
) -> None:
    mo_version_query = """
        query {
            version {
                mo_hash
                mo_version
            }
        }
    """
    response = raw_client.post(latest_graphql_url, json={"query": mo_version_query})
    status_code = response.status_code
    assert status_code == 200
    assert response.json() == {
        "data": {
            "version": {
                "mo_hash": ANY,
                "mo_version": "HEAD",
            }
        }
    }
