# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json

import pytest

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.exceptions import MultipleObjectsReturnedException
from mo_ldap_import_export.ldap import apply_discriminator
from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.moapi import MOAPI
from mo_ldap_import_export.utils import combine_dn_strings
from tests.integration.conftest import AddLdapPerson


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "DISCRIMINATOR_FIELDS": json.dumps(["uid"]),
        "DISCRIMINATOR_VALUES": json.dumps(
            [
                "{{ uid|length == 3 }}",
                "{{ uid|length == 4 }}",
                "{{ uid|length >= 5 }}",
            ]
        ),
    }
)
async def test_prefers_shorter_usernames(
    ldap_api: LDAPAPI,
    mo_api: MOAPI,
    add_ldap_person: AddLdapPerson,
) -> None:
    settings = Settings()

    ava = combine_dn_strings(await add_ldap_person("ava", "0101700000"))
    cleo = combine_dn_strings(await add_ldap_person("cleo", "0101700001"))
    emily = combine_dn_strings(await add_ldap_person("emily", "0101700002"))

    result = await apply_discriminator(
        settings, ldap_api.ldap_connection.connection, mo_api, {ava, cleo, emily}
    )
    assert result == ava

    result = await apply_discriminator(
        settings, ldap_api.ldap_connection.connection, mo_api, {cleo, emily}
    )
    assert result == cleo

    result = await apply_discriminator(
        settings, ldap_api.ldap_connection.connection, mo_api, {emily}
    )
    assert result == emily


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "DISCRIMINATOR_FIELDS": json.dumps(["uid"]),
        "DISCRIMINATOR_VALUES": json.dumps(["{{ 'ass' not in dn }}"]),
    }
)
async def test_ignore_substring(
    ldap_api: LDAPAPI,
    mo_api: MOAPI,
    add_ldap_person: AddLdapPerson,
) -> None:
    settings = Settings()

    # Valid
    ava = combine_dn_strings(await add_ldap_person("ava", "0101700000"))
    cleo = combine_dn_strings(await add_ldap_person("cleo", "0101700001"))

    # Excluded by discriminator
    classic = combine_dn_strings(await add_ldap_person("classic", "0101700002"))
    grass = combine_dn_strings(await add_ldap_person("grass", "0101700003"))
    passenger = combine_dn_strings(await add_ldap_person("passenger", "0101700004"))
    assessment = combine_dn_strings(await add_ldap_person("assessment", "0101700005"))

    # No entries, returns None
    result = await apply_discriminator(
        settings, ldap_api.ldap_connection.connection, mo_api, set()
    )
    assert result is None

    # One invalid, returns None
    result = await apply_discriminator(
        settings, ldap_api.ldap_connection.connection, mo_api, {classic}
    )
    assert result is None

    # Multiple invalid, returns None
    result = await apply_discriminator(
        settings,
        ldap_api.ldap_connection.connection,
        mo_api,
        {classic, grass, passenger},
    )
    assert result is None

    # Two valid means conflict
    with pytest.raises(MultipleObjectsReturnedException) as exc_info:
        await apply_discriminator(
            settings, ldap_api.ldap_connection.connection, mo_api, {ava, cleo}
        )
    assert "Ambiguous account result from apply discriminator" in str(exc_info.value)

    # One valid, one excluded returns the valid
    result = await apply_discriminator(
        settings, ldap_api.ldap_connection.connection, mo_api, {classic, ava}
    )
    assert result == ava

    result = await apply_discriminator(
        settings, ldap_api.ldap_connection.connection, mo_api, {passenger, cleo}
    )
    assert result == cleo

    # One valid, multiple excluded returns the valid
    result = await apply_discriminator(
        settings, ldap_api.ldap_connection.connection, mo_api, {ava, grass, assessment}
    )
    assert result == ava

    result = await apply_discriminator(
        settings,
        ldap_api.ldap_connection.connection,
        mo_api,
        {cleo, classic, passenger},
    )
    assert result == cleo

    # Multiple valid, multiple invalid means conflict
    with pytest.raises(MultipleObjectsReturnedException) as exc_info:
        await apply_discriminator(
            settings,
            ldap_api.ldap_connection.connection,
            mo_api,
            {ava, cleo, classic, grass, passenger, assessment},
        )
    assert "Ambiguous account result from apply discriminator" in str(exc_info.value)
