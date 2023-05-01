# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid
from datetime import datetime
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import patch

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


@patch("mora.service.autocomplete.get_results")
@patch("mora.service.orgunit.config.get_settings")
def test_v2_legacy_logic(mock_get_settings, mock_get_results, service_client):
    class_uuids = [
        uuid.UUID("e8ea1a09-d3d4-4203-bfe9-d9a213371337"),
    ]

    mock_get_settings.return_value = MagicMock(
        confdb_autocomplete_v2_use_legacy=True,
        confdb_autocomplete_attrs_orgunit=class_uuids,
    )
    mock_get_results.return_value = {"items": []}

    at = datetime.now().date()
    query = "f494ad89-039d-478e-91f2-a63566554666"
    response = service_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    mock_get_results.assert_called()
    mock_get_results.assert_called_with(ANY, class_uuids, query)
