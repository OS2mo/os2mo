# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
from aiohttp import ClientError
from fastapi.testclient import TestClient
from httpx import Request
from httpx import Response
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from mora.graphapi.versions.latest import health


HTTPX_MOCK_RESPONSE_404 = Response(
    status_code=404, request=Request("GET", "http://some-url.xyz")
)
HTTPX_MOCK_RESPONSE_200 = Response(
    status_code=200, request=Request("GET", "http://some-url.xyz")
)


async def test_dataset_returns_false_if_no_data_found(respx_mock) -> None:
    respx_mock.get("http://localhost/lora/organisation/organisation").mock(
        return_value=Response(200, json={"results": [[]]})
    )
    actual = await health.dataset()
    assert actual is False


@pytest.mark.usefixtures("mock_organisation")
async def test_dataset_returns_true_if_data_found() -> None:
    actual = await health.dataset()
    assert actual is True


async def test_dar_returns_false_if_unreachable(darmocked) -> None:
    darmocked.get("https://api.dataforsyningen.dk/autocomplete", status=404)

    actual = await health.dar()

    assert actual is False


async def test_dar_returns_false_if_request_error(darmocked) -> None:
    darmocked.get(
        "https://api.dataforsyningen.dk/autocomplete", exception=ClientError()
    )

    actual = await health.dar()

    assert actual is False


async def test_dar_returns_true_if_reachable(darmocked) -> None:
    darmocked.get("https://api.dataforsyningen.dk/autocomplete", status=200)

    actual = await health.dar()

    assert actual is True


def test_liveness(service_client: TestClient) -> None:
    response = service_client.request("GET", "/health/live")
    assert response.status_code == HTTP_204_NO_CONTENT


@patch("mora.health.oio_rest", new_callable=AsyncMock)
def test_readiness_everything_ready(mock_oio_rest, service_client: TestClient) -> None:
    mock_oio_rest.return_value = True
    response = service_client.request("GET", "/health/ready")
    assert response.status_code == HTTP_204_NO_CONTENT


@patch("mora.health.oio_rest", new_callable=AsyncMock)
def test_readiness_not_ready(mock_oio_rest, service_client: TestClient) -> None:
    mock_oio_rest.return_value = False
    response = service_client.request("GET", "/health/ready")
    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.integration_test
async def test_healths(service_client: TestClient) -> None:
    response = service_client.request("GET", "/health/")
    assert response.status_code == 200
    assert response.json() == {
        "amqp": True,
        "dar": True,
        "dataset": True,
        "keycloak": True,
        "oio_rest": True,
    }


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "identifier", ["amqp", "dar", "dataset", "keycloak", "oio_rest"]
)
async def test_healthidentifier(service_client: TestClient, identifier: str) -> None:
    response = service_client.request("GET", f"/health/{identifier}")
    assert response.status_code == 200
    assert response.json() is True
