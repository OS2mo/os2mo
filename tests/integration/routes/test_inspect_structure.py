# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
from httpx import AsyncClient


@pytest.mark.usefixtures("ldap_person")
@pytest.mark.integration_test
async def test_inspect_structure(test_client: AsyncClient) -> None:
    response = await test_client.get("/Inspect/structure")
    assert response.status_code == 202

    result = response.json()
    assert result == {
        "ou=os2mo": {"dn": "ou=os2mo,o=magenta,dc=magenta,dc=dk", "empty": False}
    }


@pytest.mark.usefixtures("ldap_org")
@pytest.mark.integration_test
async def test_inspect_structure_empty(test_client: AsyncClient) -> None:
    response = await test_client.get("/Inspect/structure")
    assert response.status_code == 202

    result = response.json()
    assert result == {
        "ou=os2mo": {"dn": "ou=os2mo,o=magenta,dc=magenta,dc=dk", "empty": True}
    }
