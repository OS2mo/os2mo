# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from operator import itemgetter

import pytest
from fastapi.testclient import TestClient
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_unauthorized_healths_endpoint(
    raw_client: TestClient, latest_graphql_url: str
) -> None:
    """Healths endpoint requires authentication."""
    mo_healths_query = """
        query {
            healths {
                objects {
                    identifier
                    status
                }
            }
        }
    """
    response = raw_client.post(latest_graphql_url, json={"query": mo_healths_query})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"] is None
    assert one(payload["errors"])["message"] == "User is not authenticated"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_authorized_healths_endpoint(graphapi_post: GraphAPIPost) -> None:
    """Healths endpoint works for authenticated users."""
    mo_healths_query = """
        query {
            healths {
                objects {
                    identifier
                    status
                }
            }
        }
    """
    response = graphapi_post(mo_healths_query)
    assert response.errors is None
    assert response.data is not None
    objects = response.data["healths"]["objects"]
    assert sorted(objects, key=itemgetter("identifier")) == [
        {
            "identifier": "amqp",
            "status": True,
        },
        {
            "identifier": "dar",
            "status": True,
        },
        {
            "identifier": "dataset",
            "status": False,
        },
    ]
