# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY

import pytest
from httpx import AsyncClient


@pytest.mark.usefixtures("ldap_person")
@pytest.mark.integration_test
async def test_ldap_employee_search(test_client: AsyncClient) -> None:
    response = await test_client.get("/LDAP/Employee", params={"entries_to_return": 1})
    assert response.status_code == 202

    result = response.json()
    assert result == [
        {
            "dn": "uid=abk,ou=os2mo,o=magenta,dc=magenta,dc=dk",
            "employeeNumber": "2108613133",
            "entryUUID": ANY,
            "givenName": ["Aage"],
            "sn": ["Bach Klarskov"],
            "title": ["Skole underviser"],
        },
    ]


@pytest.mark.usefixtures("ldap_person")
@pytest.mark.integration_test
async def test_ldap_employee_converted(test_client: AsyncClient) -> None:
    response = await test_client.get("/LDAP/Employee/converted")
    assert response.status_code == 202

    result = response.json()
    assert result == [
        {
            "cpr_number": "2108613133",
            "given_name": "Aage",
            "nickname_given_name": "",
            "nickname_surname": "",
            "seniority": None,
            "surname": "Bach Klarskov",
            "user_key": "Skole underviser",
            "uuid": ANY,
        }
    ]


@pytest.mark.usefixtures("ldap_person")
@pytest.mark.integration_test
async def test_ldap_employee_search_by_cpr(test_client: AsyncClient) -> None:
    response = await test_client.get("/LDAP/Employee/2108613133")
    assert response.status_code == 202

    result = response.json()
    assert result == [
        {
            "dn": "uid=abk,ou=os2mo,o=magenta,dc=magenta,dc=dk",
            "employeeNumber": "2108613133",
            "entryUUID": ANY,
            "givenName": ["Aage"],
            "sn": ["Bach Klarskov"],
            "title": ["Skole underviser"],
        },
    ]


@pytest.mark.usefixtures("ldap_person")
@pytest.mark.integration_test
async def test_ldap_employee_search_by_cpr_converted(test_client: AsyncClient) -> None:
    response = await test_client.get("/LDAP/Employee/2108613133/converted")
    assert response.status_code == 202

    result = response.json()
    assert result == [
        [
            {
                "cpr_number": "2108613133",
                "given_name": "Aage",
                "nickname_given_name": "",
                "nickname_surname": "",
                "seniority": None,
                "surname": "Bach Klarskov",
                "user_key": "Skole underviser",
                "uuid": ANY,
            }
        ]
    ]


@pytest.mark.usefixtures("ldap_person")
@pytest.mark.integration_test
async def test_ldap_employee_search_by_invalid_cpr(test_client: AsyncClient) -> None:
    response = await test_client.get("/LDAP/Employee/invalid_cpr")
    assert response.status_code == 422

    result = response.json()
    assert result == {"detail": "invalid_cpr is not a valid cpr-number"}


@pytest.mark.usefixtures("ldap_person")
@pytest.mark.integration_test
async def test_ldap_employee_search_by_invalid_cpr_converted(
    test_client: AsyncClient,
) -> None:
    response = await test_client.get("/LDAP/Employee/invalid_cpr/converted")
    assert response.status_code == 422

    result = response.json()
    assert result == {"detail": "invalid_cpr is not a valid cpr-number"}
