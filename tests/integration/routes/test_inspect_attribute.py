# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from httpx import AsyncClient


@pytest.mark.integration_test
async def test_inspect_attribute(test_client: AsyncClient) -> None:
    response = await test_client.get("/Inspect/attribute/carLicense")
    assert response.status_code == 202

    result = response.json()
    assert result == {
        "_oid_info": None,
        "collective": False,
        "description": "RFC2798: vehicle license or registration plate",
        "equality": [
            "caseIgnoreMatch",
        ],
        "experimental": None,
        "extensions": None,
        "mandatory_in": [],
        "min_length": None,
        "name": [
            "carLicense",
        ],
        "no_user_modification": False,
        "obsolete": False,
        "oid": "2.16.840.1.113730.3.1.1",
        "optional_in": [
            "inetOrgPerson",
        ],
        "ordering": None,
        "raw_definition": "( 2.16.840.1.113730.3.1.1 NAME 'carLicense' DESC 'RFC2798: vehicle "
        "license or registration plate' EQUALITY caseIgnoreMatch SUBSTR "
        "caseIgnoreSubstringsMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 )",
        "single_value": False,
        "substr": [
            "caseIgnoreSubstringsMatch",
        ],
        "substring": None,
        "superior": None,
        "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
        "usage": None,
    }


@pytest.mark.integration_test
async def test_inspect_values_empty(test_client: AsyncClient) -> None:
    response = await test_client.get("/Inspect/attribute/values/carLicense")
    assert response.status_code == 202

    result = response.json()
    assert result == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("ldap_person")
async def test_inspect_values(test_client: AsyncClient) -> None:
    response = await test_client.get("/Inspect/attribute/values/mail")
    assert response.status_code == 202

    result = response.json()
    assert result == ["['abk@ad.kolding.dk']", "[]"]
