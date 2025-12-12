# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from httpx import AsyncClient

from mo_ldap_import_export.types import LDAPUUID


@pytest.mark.envvar({"LISTEN_TO_CHANGES_IN_MO": "False"})
@pytest.mark.integration_test
async def test_reconcile_when_not_listening(
    test_client: AsyncClient, ldap_person_uuid: LDAPUUID
) -> None:
    """Test that reconcile does not crash when LISTEN_TO_CHANGES_IN_MO is False."""
    result = await test_client.post(
        "/ldap2mo/reconcile",
        json={
            "subject": str(ldap_person_uuid),
            "priority": 1,
        },
    )
    assert result.status_code == 200
