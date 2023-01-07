# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
import respx
from httpx import Response

from mora.lora import AutocompleteScope
from mora.lora import Connector


@pytest.mark.usefixtures("mock_asgi_transport")
@pytest.mark.parametrize(
    "path,expected_result",
    [
        ("bruger", []),
        ("organisationsenhed", []),
    ],
)
@respx.mock
async def test_autocomplete(path: str, expected_result: list) -> None:
    respx.get(f"http://localhost/lora/autocomplete/{path}?phrase=phrase").mock(
        return_value=Response(200, json={"results": []})
    )
    connector = Connector()
    scope = AutocompleteScope(connector, path)
    response = await scope.fetch("phrase")
    assert "items" in response
    result = response["items"]
    assert result == expected_result
