# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from parameterized import parameterized

from .cases import AsyncLoRATestCase
from mora.lora import AutocompleteScope
from mora.lora import Connector


class TestAutocompleteScope(AsyncLoRATestCase):
    @parameterized.expand(
        [
            ("bruger", []),
            ("organisationsenhed", []),
        ]
    )
    async def test_autocomplete(self, path: str, expected_result: list):
        connector = Connector()
        scope = AutocompleteScope(connector, path)
        response = await scope.fetch("phrase")
        assert "items" in response
        result = response["items"]
        assert result == expected_result
