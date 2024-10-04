# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY

import pytest
from httpx import AsyncClient


@pytest.mark.integration_test
async def test_inspect_overview(test_client: AsyncClient) -> None:
    response = await test_client.get("/Inspect/overview")
    assert response.status_code == 202

    result = response.json()
    assert result == {
        "attributes": ANY,
        "superiors": ["organizationalPerson", "person", "top"],
    }

    # Check the first 5 attributes are as expected
    attributes = result["attributes"].keys()
    assert sorted(attributes)[:5] == [
        "audio",
        "businessCategory",
        "carLicense",
        "departmentNumber",
        "description",
    ]

    # Check a single attribute has the details we expect
    assert result["attributes"]["carLicense"] == {
        "field_type": "Directory String",
        "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
    }


@pytest.mark.integration_test
async def test_inspect_overview_organizational_unit(test_client: AsyncClient) -> None:
    response = await test_client.get(
        "/Inspect/overview", params={"ldap_class": "organizationalUnit"}
    )
    assert response.status_code == 202

    result = response.json()
    assert result == {
        "attributes": ANY,
        "superiors": ["top"],
    }

    # Check the first 5 attributes are as expected
    attributes = result["attributes"].keys()
    assert sorted(attributes)[:5] == [
        "businessCategory",
        "description",
        "destinationIndicator",
        "facsimileTelephoneNumber",
        "internationaliSDNNumber",
    ]

    # Check a single attribute has the details we expect
    assert result["attributes"]["businessCategory"] == {
        "field_type": "Directory String",
        "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
    }
