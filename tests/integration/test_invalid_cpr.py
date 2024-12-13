# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from fastramqpi.context import Context

from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.exceptions import InvalidCPR
from mo_ldap_import_export.moapi import MOAPI
from mo_ldap_import_export.types import CPRNumber


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
@pytest.mark.usefixtures("test_client")
async def test_cpr2uuids(
    context: Context,
    mo_person: UUID,
) -> None:
    dataloader: DataLoader = context["user_context"]["dataloader"]
    moapi: MOAPI = dataloader.moapi

    result = await moapi.cpr2uuids(CPRNumber("0101700000"))
    assert result == set()

    result = await moapi.cpr2uuids(CPRNumber("2108613133"))
    assert result == {mo_person}

    with pytest.raises(InvalidCPR) as exc_info:
        await moapi.cpr2uuids(CPRNumber("9999999999"))
    assert "Unable to lookup invalid CPR number" in str(exc_info.value)
