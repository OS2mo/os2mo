# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import uuid4

import pytest
from fastramqpi.context import Context
from structlog.testing import capture_logs

from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.environments import get_person_dn
from mo_ldap_import_export.exceptions import NoObjectsReturnedException
from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import EmployeeUUID


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
@pytest.mark.usefixtures("test_client")
async def test_get_person_dn_invalid_uuid(context: Context) -> None:
    assert "user_context" in context
    dataloader: DataLoader = context["user_context"]["dataloader"]

    with pytest.raises(NoObjectsReturnedException) as exc_info:
        await get_person_dn(dataloader, EmployeeUUID(uuid4()))

    assert "Unable to lookup employee" in str(exc_info.value)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
@pytest.mark.usefixtures("test_client")
async def test_get_person_dn_no_ldap_account(
    context: Context, mo_person: EmployeeUUID
) -> None:
    assert "user_context" in context
    dataloader: DataLoader = context["user_context"]["dataloader"]
    with capture_logs() as cap_logs:
        result = await get_person_dn(dataloader, mo_person)
    assert result is None

    events = [m["event"] for m in cap_logs]
    assert "_find_best_dn returned create=True in get_person_dn" in events


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
@pytest.mark.usefixtures("test_client")
async def test_get_person_dn_with_ldap_account(
    context: Context,
    mo_person: EmployeeUUID,
    ldap_person_dn: DN,
) -> None:
    assert "user_context" in context
    dataloader: DataLoader = context["user_context"]["dataloader"]

    result = await get_person_dn(dataloader, mo_person)
    assert result == ldap_person_dn
