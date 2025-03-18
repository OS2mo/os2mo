# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock

import pytest

from mo_ldap_import_export.depends import Settings
from mo_ldap_import_export.ldap import filter_dns
from mo_ldap_import_export.types import DN


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.parametrize("input_dns", [set(), {"CN=foo"}, {"CN=foo", "CN=bar"}])
async def test_filter_dns_no_filter(input_dns: set[DN]) -> None:
    ldap_connection = AsyncMock()

    settings = Settings()
    assert settings.discriminator_filter is None

    output_dns = await filter_dns(settings, ldap_connection, input_dns)
    assert input_dns == output_dns


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_filter_dns_no_fields() -> None:
    ldap_connection = AsyncMock()

    settings = Settings()
    assert settings.discriminator_filter is None
    settings = settings.copy(update={"discriminator_filter": "True"})
    assert settings.discriminator_filter == "True"

    with pytest.raises(AssertionError) as exc_info:
        await filter_dns(settings, ldap_connection, {"CN=foo"})
    assert "discriminator_fields must be set" in str(exc_info.value)
