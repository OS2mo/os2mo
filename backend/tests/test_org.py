# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from oio_rest.organisation import Organisation


def test_no_orgs_in_mo(service_client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        Organisation, "get_objects_direct", AsyncMock(return_value={"results": []})
    )

    response = service_client.request("GET", "/service/o/")
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "error_key": "E_ORG_UNCONFIGURED",
        "status": 400,
        "description": "Organisation has not been configured",
    }


def test_more_than_one_org_in_mo(service_client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        Organisation,
        "get_objects_direct",
        AsyncMock(
            return_value={
                "results": [
                    [
                        {
                            "id": "6bd057e7-0727-43e7-96d6-f01f741f8554",
                            "registreringer": [{}],
                        },
                        {
                            "id": "b9a30070-ef15-4e54-840f-2b77753580df",
                            "registreringer": [{}],
                        },
                    ]
                ]
            },
        ),
    )

    response = service_client.request("GET", "/service/o/")
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "count": 2,
        "error_key": "E_ORG_TOO_MANY",
        "status": 400,
        "description": "Too many organisations in lora, max one allowed",
    }
