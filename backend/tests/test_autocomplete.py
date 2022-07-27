# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
import respx
from httpx import Response
from parameterized import parameterized

from .cases import AsyncLoRATestCase
from mora.lora import AutocompleteScope
from mora.lora import Connector


@pytest.mark.usefixtures("mock_asgi_transport")
class TestAutocompleteScope(AsyncLoRATestCase):
    @parameterized.expand(
        [
            ("bruger", []),
            ("organisationsenhed", []),
        ]
    )
    @respx.mock
    async def test_autocomplete(self, path: str, expected_result: list):
        respx.get(f"http://localhost/lora/autocomplete/{path}?phrase=phrase").mock(
            return_value=Response(200, json={"results": []})
        )
        connector = Connector()
        scope = AutocompleteScope(connector, path)
        response = await scope.fetch("phrase")
        assert "items" in response
        result = response["items"]
        assert result == expected_result
