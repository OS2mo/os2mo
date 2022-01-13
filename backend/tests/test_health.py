# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
from aioresponses import aioresponses
from aiohttp import ClientError
from httpx import Response, Request
from mock import patch
from starlette.status import HTTP_204_NO_CONTENT
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

import tests.cases
from mora import health, config
from tests import util

pytestmark = pytest.mark.asyncio

HTTPX_MOCK_RESPONSE = Response(
    status_code=404, request=Request("GET", "http://some-url.xyz")
)


class TestOIORestHealth:
    async def test_oio_rest_returns_true_if_reachable(self):
        assert await health.oio_rest()

    @patch("httpx.AsyncClient.get")
    async def test_oio_rest_returns_false_if_unreachable(self, mock_get):
        mock_get.return_value = HTTPX_MOCK_RESPONSE
        assert not await health.oio_rest()

    @patch("httpx.AsyncClient.get")
    async def test_oio_rest_returns_false_for_httpx_client_error(self, mock_get):
        # This is one of the possible erros raised by the httpx client
        mock_get.side_effect = RuntimeError(
            "Cannot send a request, as the client has been closed."
        )
        assert not await health.oio_rest()


class ConfigurationDatabaseHealthTests(tests.cases.TestCase):
    @patch("mora.health.conf_db.health_check", new=lambda: (False, ""))
    def test_configuration_database_returns_false_if_health_check_fails(self):
        actual = health.configuration_database()

        self.assertEqual(False, actual)

    @patch("mora.health.conf_db.health_check", new=lambda: (True, ""))
    def test_configuration_database_returns_false_if_health_check_succeeds(self):
        actual = health.configuration_database()

        self.assertEqual(True, actual)


class DatasetHealthTests(tests.cases.TestCase):
    @pytest.mark.skip(reason="LoRa is using HTTPX now, these tests did not run")
    @aioresponses()
    async def test_dataset_returns_false_if_no_data_found(self, mock):
        mock.get(
            config.get_settings().lora_url + "organisation/organisation?"
            "virkningfra=-infinity&virkningtil=infinity&bvn=%&konsolider=True",
            payload={"results": [[]]},
        )
        actual = await health.dataset()

        self.assertEqual(False, actual)

    @pytest.mark.skip(reason="LoRa is using HTTPX now, these tests did not run")
    @aioresponses()
    async def test_dataset_returns_true_if_data_found(self, mock):
        mock.get(
            (
                config.get_settings().lora_url + "organisation/organisation"
                "?virkningfra=-infinity&virkningtil=infinity&bvn=%&konsolider=True"
            ),
            payload={"results": [["f668b69a-66c4-4ba8-a783-5513178e8df1"]]},
        )

        actual = await health.dataset()

        self.assertEqual(True, actual)


class TestKeycloakHealth:
    @patch("httpx.AsyncClient.get")
    async def test_keycloak_returns_true_if_reachable(self, mock_get):
        mock_get.return_value = Response(
            status_code=200, request=Request("GET", "http://keycloak:8080/auth/")
        )
        assert await health.keycloak()

    @patch("httpx.AsyncClient.get")
    async def test_keycloak_returns_false_if_unreachable(self, mock_get):
        mock_get.return_value = HTTPX_MOCK_RESPONSE
        assert not await health.keycloak()

    @patch("httpx.AsyncClient.get")
    async def test_keycloak_returns_false_for_httpx_client_error(self, mock_get):
        # This is one of the possible erros raised by the httpx client
        mock_get.side_effect = RuntimeError(
            "Cannot send a request, as the client has been closed."
        )
        assert not await health.keycloak()


class DARHealthTests(tests.cases.TestCase):
    @util.darmock()
    async def test_dar_returns_false_if_unreachable(self, mock):
        mock.get("https://api.dataforsyningen.dk/autocomplete", status=404)

        actual = await health.dar()

        self.assertEqual(False, actual)

    @util.darmock()
    async def test_dar_returns_false_if_request_error(self, mock):
        mock.get("https://api.dataforsyningen.dk/autocomplete", exception=ClientError())

        actual = await health.dar()

        self.assertEqual(False, actual)

    @util.darmock()
    async def test_dar_returns_true_if_reachable(self, mock):
        mock.get("https://api.dataforsyningen.dk/autocomplete", status=200)

        actual = await health.dar()

        self.assertEqual(True, actual)


class TestKubernetesProbes(tests.cases.TestCase):
    """
    Test the Kubernetes liveness and readiness endpoints
    """

    def test_liveness(self):
        self.assertRequest("/health/live", HTTP_204_NO_CONTENT)

    @patch("mora.health._is_endpoint_reachable")
    def test_readiness_everything_ready(self, mock_is_endpoint_reachable):
        mock_is_endpoint_reachable.side_effect = [True, True]
        self.assertRequest("/health/ready", HTTP_204_NO_CONTENT)

    @patch("mora.health._is_endpoint_reachable")
    @patch("mora.health.configuration_database")
    def test_readiness_conf_db_not_ready(
        self, mock_conf_db, mock_is_endpoint_reachable
    ):
        mock_conf_db.return_value = False
        mock_is_endpoint_reachable.side_effect = [True, True]
        self.assertRequest("/health/ready", HTTP_503_SERVICE_UNAVAILABLE)

    @patch("mora.health._is_endpoint_reachable")
    def test_readiness_lora_not_ready(self, mock_is_endpoint_reachable):
        mock_is_endpoint_reachable.side_effect = [False, True]
        self.assertRequest("/health/ready", HTTP_503_SERVICE_UNAVAILABLE)

    @patch("mora.health._is_endpoint_reachable")
    def test_readiness_keycloak_not_ready(self, mock_is_endpoint_reachable):
        mock_is_endpoint_reachable.side_effect = [True, False]
        self.assertRequest("/health/ready", HTTP_503_SERVICE_UNAVAILABLE)
