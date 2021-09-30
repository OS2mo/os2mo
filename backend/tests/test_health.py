# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

from aioresponses import aioresponses
from httpx import Response, Request

import pytest

import tests.cases
from mora import health, config


HTTPX_MOCK_RESPONSE = Response(
    status_code=404,
    request=Request('GET', 'http://some-url.xyz')
)


class TestOIORestHealth:
    @pytest.mark.asyncio
    async def test_oio_rest_returns_true_if_reachable(self):
        assert await health.oio_rest()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_oio_rest_returns_false_if_unreachable(self, mock_get):
        mock_get.return_value = HTTPX_MOCK_RESPONSE
        assert not await health.oio_rest()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
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
    @aioresponses()
    async def test_dataset_returns_false_if_no_data_found(self, mock):
        mock.get(config.get_settings().lora_url +
                 "organisation/organisation?"
                 "virkningfra=-infinity&virkningtil=infinity&bvn=%&konsolider=True",
                 payload={"results": [[]]},
                 )
        actual = await health.dataset()

        self.assertEqual(False, actual)

    @aioresponses()
    async def test_dataset_returns_true_if_data_found(self, mock):
        mock.get((config.get_settings().lora_url +
                  "organisation/organisation"
                  "?virkningfra=-infinity&virkningtil=infinity&bvn=%&konsolider=True"
                  ),
                 payload={"results": [["f668b69a-66c4-4ba8-a783-5513178e8df1"]]},
                 )

        actual = await health.dataset()

        self.assertEqual(True, actual)


class TestKeycloakHealth:
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_keycloak_returns_true_if_reachable(self, mock_get):
        mock_get.return_value = Response(
            status_code=200,
            request=Request('GET', 'http://keycloak:8080/auth/')
        )
        assert await health.keycloak()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_keycloak_returns_false_if_unreachable(self, mock_get):
        mock_get.return_value = HTTPX_MOCK_RESPONSE
        assert not await health.keycloak()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_keycloak_returns_false_for_httpx_client_error(self, mock_get):
        # This is one of the possible erros raised by the httpx client
        mock_get.side_effect = RuntimeError(
            "Cannot send a request, as the client has been closed."
        )
        assert not await health.keycloak()


class TestDARHealth:
    @pytest.mark.asyncio
    async def test_dar_returns_true_if_reachable(self):
        assert await health.dar()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_dar_returns_false_if_unreachable(self, mock_get):
        mock_get.return_value = HTTPX_MOCK_RESPONSE
        assert not await health.dar()

    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_dar_returns_false_for_httpx_client_error(self, mock_get):
        # This is one of the possible erros raised by the httpx client
        mock_get.side_effect = RuntimeError(
            "Cannot send a request, as the client has been closed."
        )
        assert not await health.dar()
