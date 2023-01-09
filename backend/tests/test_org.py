# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

from fastapi.testclient import TestClient


async def async_helper1():
    return []


async def async_helper2():
    return [{}, {}]


@patch("mora.service.org.get_valid_organisations", new=async_helper1)
def test_no_orgs_in_mo(service_client: TestClient) -> None:
    response = service_client.get("/service/o/")
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "error_key": "E_ORG_UNCONFIGURED",
        "status": 400,
        "description": "Organisation has not been configured",
    }


@patch("mora.service.org.get_valid_organisations", new=async_helper2)
def test_more_than_one_org_in_mo(service_client: TestClient) -> None:
    response = service_client.get("/service/o/")
    assert response.status_code == 400
    assert response.json() == {
        "error": True,
        "count": 2,
        "error_key": "E_ORG_TOO_MANY",
        "status": 400,
        "description": "Too many organisations in lora, max one allowed",
    }
