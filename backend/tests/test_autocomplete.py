# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid
from datetime import datetime
from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from httpx import Response

from mora.graphapi.versions.v14.version import GraphQLVersion as GraphQLVersionV14
from mora.lora import AutocompleteScope
from mora.lora import Connector
from mora.service.autocomplete.orgunits import decorate_orgunit_search_result


@pytest.mark.parametrize(
    "path,expected_result",
    [
        ("bruger", []),
        ("organisationsenhed", []),
    ],
)
async def test_autocomplete(respx_mock, path: str, expected_result: list) -> None:
    respx_mock.get(f"http://localhost/lora/autocomplete/{path}?phrase=phrase").mock(
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
    response = service_client.request(
        "GET", f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    mock_get_results.assert_called()
    mock_get_results.assert_called_with(ANY, class_uuids, query)


@patch("mora.service.autocomplete.orgunits.execute_graphql", new_callable=AsyncMock)
async def test_v2_decorate_orgunits(mock_execute_graphql):
    test_data = {
        "uuid": "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
        "name": "Viuf skole",
        "user_key": "Viuf skole",
        "validity": {"from": "1960-01-01T00:00:00+01:00", "to": None},
        "ancestors_validity": [
            {"name": "Skoler og børnehaver"},
            {"name": "Skole og Børn"},
            {"name": "Kolding Kommune"},
        ],
    }

    expected_result = [
        {
            "uuid": uuid.UUID(test_data["uuid"]),
            "name": test_data["name"],
            "path": [
                # [::-1] reverses the list
                ancestor["name"]
                for ancestor in test_data["ancestors_validity"][::-1]
            ]
            + [test_data["name"]],
            "attrs": [],
            "validity": test_data["validity"],
        }
    ]

    mock_execute_graphql.return_value = MagicMock(
        data={
            "org_units": {
                "objects": [
                    {
                        "uuid": test_data["uuid"],
                        "current": test_data,
                        "objects": [test_data],
                    }
                ]
            }
        },
        errors=None,
    )

    # Invoke
    now = datetime.now()
    result = await decorate_orgunit_search_result(
        settings=MagicMock(confdb_autocomplete_attrs_orgunit=None),
        search_results=[uuid.UUID(test_data["uuid"])],
        at=now.date(),
    )

    # Asserts
    mock_execute_graphql.assert_called_with(
        ANY,
        graphql_version=GraphQLVersionV14,
        variable_values={
            "uuids": [test_data["uuid"]],
            "from_date": now.date().isoformat(),
        },
    )

    assert result == expected_result
