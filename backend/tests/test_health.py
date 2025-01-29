# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from aiohttp import ClientError
from fastapi.testclient import TestClient
from mora.graphapi.versions.latest import health
from starlette.status import HTTP_204_NO_CONTENT


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_dataset_returns_false_if_no_data_found() -> None:
    actual = await health.dataset()
    assert actual is False


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
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


def test_readiness(service_client: TestClient) -> None:
    response = service_client.request("GET", "/health/ready")
    assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_healths(darmocked, service_client: TestClient) -> None:
    darmocked.get("https://api.dataforsyningen.dk/autocomplete", status=200)
    response = service_client.request("GET", "/health/")
    assert response.status_code == 200
    assert response.json() == {
        "amqp": True,
        "dar": True,
        "dataset": True,
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize("identifier", ["amqp", "dar", "dataset"])
async def test_healthidentifier(
    darmocked, service_client: TestClient, identifier: str
) -> None:
    darmocked.get("https://api.dataforsyningen.dk/autocomplete", status=200)
    response = service_client.request("GET", f"/health/{identifier}")
    assert response.status_code == 200
    assert response.json() is True
