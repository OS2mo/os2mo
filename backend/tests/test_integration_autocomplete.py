# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
import freezegun

from datetime import datetime
from fastapi.testclient import TestClient


@pytest.mark.integration_test
@freezegun.freeze_time("2017-01-01", tz_offset=1)
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_autocomplete_v2_get_by_uuid(service_client: TestClient):
    # Parameters
    url = "/service/ou/autocomplete/"
    at = datetime.now().date()
    query = "f494ad89-039d-478e-91f2-a63566554666"

    # query = "Skole"
    # query = "d3018bd8"
    # query = "d3018bd8-fc29-5ee2-b2ce-8e38e488ada9"
    # query = "dad7d0ad-c7a9-4a94-969d-464337e31fec"

    response = service_client.get(f"{url}?query={query}&at={at.isoformat()}")
    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "uuid": "d3018bd8-fc29-5ee2-b2ce-8e38e488ada9",
                "path": [
                    "Lønorganisation",
                    "Skole og Børn",
                    "Skoler og børnehaver",
                    "Egtved skole",
                ],
            }
        ]
    }

    tap = "test"
