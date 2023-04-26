# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import freezegun
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@patch("mora.config.get_settings")
async def test_autocomplete_v2_search_by_addr_afdelingskode(
    mock_get_settings, service_client: TestClient
):
    # Mock settings
    mock_get_settings.return_value = MagicMock(
        confdb_autocomplete_v2_use_legacy=False,
        confdb_autocomplete_attrs_orgunit=[
            uuid.UUID("e8ea1a09-d3d4-4203-bfe9-d9a213371337"),
        ],
    )

    # Parameters
    at = datetime.now().date()
    query = "Fake afdelingskode"
    response = service_client.get(
        f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "f494ad89-039d-478e-91f2-a63566554666",
                "name": "Fake Corp With Addrs",
                "path": ["Fake Corp With Addrs"],
                "attrs": [
                    {
                        "title": "Afdelingskode",
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0441",
                        "value": "Fake afdelingskode",
                    }
                ],
            }
        ]
    }
