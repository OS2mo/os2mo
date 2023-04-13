# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_autcomplete_v2(service_client: TestClient):
    timemachine_date = datetime.utcnow().date()

    # search_phrase = "Skole"
    # search_phrase = "d3018bd8"
    # search_phrase = "d3018bd8-fc29-5ee2-b2ce-8e38e488ada9"
    search_phrase = "dad7d0ad-c7a9-4a94-969d-464337e31fec"

    response = service_client.get(
        # f"/service/ou/autocomplete/?query={search_phrase}&at={timemachine_date.isoformat()}"
        f"/service/ou/autocomplete/?query={search_phrase}"
    )

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
