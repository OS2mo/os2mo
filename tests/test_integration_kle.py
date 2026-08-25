# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from more_itertools import one

from tests.conftest import GraphAPIPost

KLE_READ_QUERY = """
    query ReadKLEs($filter: KLEFilter!) {
        kles(filter: $filter) {
            objects {
                objects {
                    uuid
                    user_key
                    org_unit_uuid
                    kle_number_uuid
                    kle_aspect_uuids
                    validity {from to}
                }
            }
        }
    }
"""


def read_kles(graphapi_post: GraphAPIPost, filter: dict) -> list[dict]:
    response = graphapi_post(KLE_READ_QUERY, variables={"filter": filter})
    assert response.errors is None
    return [
        obj for outer in response.data["kles"]["objects"] for obj in outer["objects"]
    ]


@pytest.mark.integration_test
@pytest.mark.freeze_time("2018-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
def test_create_kle(service_client: TestClient, graphapi_post: GraphAPIPost) -> None:
    org_unit_uuid = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

    payload = [
        {
            "type": "kle",
            "org_unit": {"uuid": org_unit_uuid},
            "kle_aspect": [
                {"uuid": "9016d80a-c6d2-4fb4-83f1-87ecc23ab062"},
                {"uuid": "fdbdb18f-5a28-4414-bc43-d5c2b70c0510"},
            ],
            "kle_number": {"uuid": "d7c12965-6207-4c82-88b8-68dbf6667492"},
            "user_key": "1234",
            "validity": {
                "from": "2017-12-01",
                "to": None,
            },
        }
    ]

    with patch("uuid.uuid4", new=lambda: UUID("11111111-1111-1111-1111-111111111111")):
        response = service_client.request(
            "POST", "/service/details/create", json=payload
        )
        # amqp_topics={"org_unit.kle.create": 1},
        assert response.status_code == 201

    kle = one(
        read_kles(
            graphapi_post,
            {"uuids": ["11111111-1111-1111-1111-111111111111"]},
        )
    )
    assert kle["uuid"] == "11111111-1111-1111-1111-111111111111"
    assert kle["user_key"] == "1234"
    assert kle["org_unit_uuid"] == org_unit_uuid
    assert kle["kle_number_uuid"] == "d7c12965-6207-4c82-88b8-68dbf6667492"
    assert kle["kle_aspect_uuids"] == [
        "9016d80a-c6d2-4fb4-83f1-87ecc23ab062",
        "fdbdb18f-5a28-4414-bc43-d5c2b70c0510",
    ]
    assert kle["validity"]["from"] == "2017-12-01T00:00:00+01:00"
    assert kle["validity"]["to"] is None


@pytest.mark.integration_test
@pytest.mark.freeze_time("2018-01-01", tz_offset=1)
@pytest.mark.usefixtures("fixture_db")
def test_edit_kle_no_overwrite(
    service_client: TestClient, graphapi_post: GraphAPIPost
) -> None:
    org_unit_uuid = "dad7d0ad-c7a9-4a94-969d-464337e31fec"
    kle_uuid = "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5"

    req = [
        {
            "type": "kle",
            "uuid": kle_uuid,
            "data": {
                "org_unit": {"uuid": org_unit_uuid},
                "kle_aspect": [
                    {"uuid": "fdbdb18f-5a28-4414-bc43-d5c2b70c0510"},
                    {"uuid": "f9748c65-3354-4682-a035-042c534c6b4e"},
                ],
                "kle_number": {"uuid": "73360db1-bad3-4167-ac73-8d827c0c8751"},
                "user_key": "5678",
                "validity": {
                    "from": "2017-12-06",
                    "to": None,
                },
            },
        }
    ]

    response = service_client.request("POST", "/service/details/edit", json=req)
    # amqp_topics={"org_unit.kle.update": 1},
    assert response.status_code == 200
    assert response.json() == [kle_uuid]

    kle = one(read_kles(graphapi_post, {"uuids": [kle_uuid]}))
    assert kle["uuid"] == kle_uuid
    assert kle["user_key"] == "5678"
    assert kle["org_unit_uuid"] == org_unit_uuid
    assert kle["kle_number_uuid"] == "73360db1-bad3-4167-ac73-8d827c0c8751"
    assert kle["kle_aspect_uuids"] == [
        "fdbdb18f-5a28-4414-bc43-d5c2b70c0510",
        "f9748c65-3354-4682-a035-042c534c6b4e",
    ]
    assert kle["validity"]["from"] == "2017-12-06T00:00:00+01:00"
    assert kle["validity"]["to"] is None
