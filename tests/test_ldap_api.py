# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock

import pytest

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.types import CPRNumber


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_cpr2dns_not_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LDAP_CPR_ATTRIBUTE")
    monkeypatch.setenv("LDAP_IT_SYSTEM", "ADUUID")

    settings = Settings()
    connection = AsyncMock()
    ldapapi = LDAPAPI(settings, connection)

    with pytest.raises(NoObjectsReturnedException) as exc_info:
        await ldapapi.cpr2dns(CPRNumber("0101700000"))
    assert "cpr_field is not configured" in str(exc_info.value)
