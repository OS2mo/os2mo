# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest
import respx
from aiohttp import ClientError
from httpx import Request
from httpx import Response
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

import tests.cases
from mora.graphapi.versions.latest import health
from mora.service.org import ConfiguredOrganisation
from tests import util

HTTPX_MOCK_RESPONSE_404 = Response(
    status_code=404, request=Request("GET", "http://some-url.xyz")
)

HTTPX_MOCK_RESPONSE_200 = Response(
    status_code=200, request=Request("GET", "http://some-url.xyz")
)


@pytest.mark.usefixtures("mock_asgi_transport")
class DatasetHealthTests(tests.cases.AsyncTestCase):
    @respx.mock
    async def test_dataset_returns_false_if_no_data_found(self):
        ConfiguredOrganisation.clear()
        respx.get("http://localhost/lora/organisation/organisation").mock(
            return_value=Response(200, json={"results": [[]]})
        )
        actual = await health.dataset()
        assert actual is False

    @respx.mock
    @pytest.mark.usefixtures("mock_organisation")
    async def test_dataset_returns_true_if_data_found(self):
        ConfiguredOrganisation.clear()
        actual = await health.dataset()
        assert actual is True


class DARHealthTests(tests.cases.AsyncTestCase):
    @util.darmock()
    async def test_dar_returns_false_if_unreachable(self, mock):
        mock.get("https://api.dataforsyningen.dk/autocomplete", status=404)

        actual = await health.dar()

        assert actual is False

    @util.darmock()
    async def test_dar_returns_false_if_request_error(self, mock):
        mock.get("https://api.dataforsyningen.dk/autocomplete", exception=ClientError())

        actual = await health.dar()

        assert actual is False

    @util.darmock()
    async def test_dar_returns_true_if_reachable(self, mock):
        mock.get("https://api.dataforsyningen.dk/autocomplete", status=200)

        actual = await health.dar()

        assert actual is True


def test_liveness(service_client):
    response = service_client.get("/health/live")
    assert response.status_code == HTTP_204_NO_CONTENT


@patch("mora.health.oio_rest", new_callable=AsyncMock)
def test_readiness_everything_ready(mock_oio_rest, service_client):
    mock_oio_rest.return_value = True
    response = service_client.get("/health/ready")
    assert response.status_code == HTTP_204_NO_CONTENT


@patch("mora.health.oio_rest", new_callable=AsyncMock)
def test_readiness_not_ready(mock_oio_rest, service_client):
    mock_oio_rest.return_value = False
    response = service_client.get("/health/ready")
    assert response.status_code == HTTP_503_SERVICE_UNAVAILABLE
