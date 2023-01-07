# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "url",
    [
        "/service/details/create",
        "/service/details/edit",
    ],
)
def test_create_invalid_type(service_client: TestClient, url: str) -> None:
    response = service_client.post(url, json=[{"type": "kaflaflibob"}])
    assert response.status_code == 400
    assert response.json() == {
        "description": "Unknown role type.",
        "error": True,
        "error_key": "E_UNKNOWN_ROLE_TYPE",
        "status": 400,
        "types": ["kaflaflibob"],
    }


def test_invalid_json(service_client: TestClient) -> None:
    response = service_client.post("/service/details/edit", json="kaflaflibob")
    assert response.status_code == 400
    assert response.json() == {
        "description": "Invalid input.",
        "error": True,
        "error_key": "E_INVALID_INPUT",
        "errors": [
            {
                "loc": ["body"],
                "msg": "value is not a valid list",
                "type": "type_error.list",
            },
            {
                "loc": ["body"],
                "msg": "value is not a valid dict",
                "type": "type_error.dict",
            },
        ],
        "request": "kaflaflibob",
        "status": 400,
    }


def test_request_invalid_type(service_client: TestClient) -> None:
    response = service_client.get(
        "/service/e/00000000-0000-0000-0000-000000000000/details/blyf"
    )
    assert response.status_code == 400
    assert response.json() == {
        "description": "Unknown role type.",
        "error": True,
        "error_key": "E_UNKNOWN_ROLE_TYPE",
        "status": 400,
        "type": "blyf",
    }
