# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import pytest
from httpx import AsyncClient

from mo_ldap_import_export.utils import combine_dn_strings
from tests.integration.conftest import AddLdapPerson


@pytest.mark.integration_test
async def test_import_invalid_cpr_number(
    test_client: AsyncClient,
    ldap_org_unit: list[str],
    add_ldap_person: AddLdapPerson,
) -> None:
    # Valid
    await add_ldap_person("abk", "0101700000")
    # Invalid
    bad_cpr = "5001012002"
    bad_dn = "bad"
    await add_ldap_person(bad_dn, bad_cpr)

    response = await test_client.get("/Inspect/invalid_cpr_numbers")
    assert response.status_code == 202
    result = response.json()
    assert result == {
        combine_dn_strings([f"uid={bad_dn}"] + ldap_org_unit): bad_cpr,
    }


@pytest.mark.integration_test
async def test_import_invalid_cpr_number_empty(
    test_client: AsyncClient,
) -> None:
    response = await test_client.get("/Inspect/invalid_cpr_numbers")
    assert response.status_code == 202
    result = response.json()
    assert result == {}


@pytest.mark.integration_test
@pytest.mark.envvar({"LDAP_CPR_ATTRIBUTE": "", "LDAP_IT_SYSTEM": "ADUUID"})
async def test_import_invalid_cpr_number_no_cpr_field(
    test_client: AsyncClient,
) -> None:
    response = await test_client.get("/Inspect/invalid_cpr_numbers")
    assert response.status_code == 404
    result = response.json()
    assert result == {"detail": "cpr_field is not configured"}
