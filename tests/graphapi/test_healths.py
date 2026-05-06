# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from operator import itemgetter
from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_unauthorized_healths_endpoint(
    raw_client: TestClient, latest_graphql_url: str
) -> None:
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
    status_code = response.status_code
    assert status_code == 200
    payload = response.json()
    assert payload == {"data": {"healths": {"objects": ANY}}}
    objects = payload["data"]["healths"]["objects"]
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
