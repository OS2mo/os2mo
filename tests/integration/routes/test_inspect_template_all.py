# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import json
from uuid import UUID

import pytest
from httpx import AsyncClient


@pytest.mark.integration_test
async def test_ldap_template_all(test_client: AsyncClient, mo_person: UUID) -> None:
    response = await test_client.get("/Inspect/mo2ldap/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    with open("/tmp/mo2ldap.json") as fin:
        file_data = json.load(fin)
    assert file_data == {
        str(mo_person): {
            "employeeNumber": [
                "2108613133",
            ],
            "givenName": [
                "Aage",
            ],
            "sn": [
                "Bach Klarskov",
            ],
            "title": [str(mo_person)],
        },
    }
