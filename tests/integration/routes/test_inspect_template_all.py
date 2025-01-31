# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import csv
from uuid import UUID

import pytest
from httpx import AsyncClient


@pytest.mark.integration_test
async def test_ldap_template_all(test_client: AsyncClient, mo_person: UUID) -> None:
    response = await test_client.get("/Inspect/mo2ldap/all")
    assert response.status_code == 200
    result = response.json()
    assert result == "OK"

    with open("/tmp/mo2ldap.csv") as fin:
        reader = csv.reader(fin)
        file_data = [row for row in reader]
    assert file_data == [
        [
            "2108613133",
            "Aage",
            "Bach Klarskov",
            str(mo_person),
            str(mo_person),
        ]
    ]
