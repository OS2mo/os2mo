# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from datetime import datetime
from unittest.mock import ANY
from uuid import UUID

import pytest
from fastramqpi.context import Context
from structlog.testing import capture_logs

from mo_ldap_import_export.dataloaders import DataLoader
from mo_ldap_import_export.dataloaders import extract_unique_ldap_uuids
from mo_ldap_import_export.import_export import SyncTool
from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.moapi import MOAPI
from mo_ldap_import_export.types import DN
from mo_ldap_import_export.types import LDAPUUID
from mo_ldap_import_export.types import EmployeeUUID
from mo_ldap_import_export.utils import combine_dn_strings
from mo_ldap_import_export.utils import mo_today
from tests.integration.conftest import DN2UUID
from tests.integration.conftest import AddLdapPerson


@pytest.fixture
def ldap_delete_by_dn(ldap_api: LDAPAPI) -> Callable[[DN], Awaitable[None]]:
    async def inner(dn: DN) -> None:
        await ldap_api.ldap_connection.ldap_delete(dn)

    return inner


@pytest.fixture
def read_mo_mapping_uuids(
    context: Context,
) -> Callable[[EmployeeUUID], Awaitable[dict[LDAPUUID, datetime | None]]]:
    dataloader = context["user_context"]["dataloader"]
    assert isinstance(dataloader, DataLoader)
    moapi = dataloader.moapi
    assert isinstance(moapi, MOAPI)

    async def inner(person: EmployeeUUID) -> dict[LDAPUUID, datetime | None]:
        # Fetch the mapping ITSystem, it must exists for our tests
        raw_it_system_uuid = await moapi.get_ldap_it_system_uuid()
        assert raw_it_system_uuid is not None
        it_system_uuid = UUID(raw_it_system_uuid)
        # Fetch all ITUsers for our user under the mapping ITSystem
        it_users = await moapi.load_mo_employee_it_users(person, it_system_uuid)
        # Ensure all values are UUIDs and construct an UUID mapping
        ldap_uuid_ituser_map = extract_unique_ldap_uuids(it_users)
        return {
            ldap_uuid: ituser.validity.end
            for ldap_uuid, ituser in ldap_uuid_ituser_map.items()
        }

    return inner


@pytest.fixture
def sync_tool(context: Context) -> SyncTool:
    sync_tool = context["user_context"]["sync_tool"]
    assert isinstance(sync_tool, SyncTool)
    return sync_tool


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "LDAP_IT_SYSTEM": "ADUUID",
    }
)
async def test_find_mo_employee_dn_by_itsystem_ituser_termination(
    read_mo_mapping_uuids: Callable[
        [EmployeeUUID], Awaitable[dict[LDAPUUID, datetime | None]]
    ],
    ldap_delete_by_dn: Callable[[DN], Awaitable[None]],
    add_ldap_person: AddLdapPerson,
    sync_tool: SyncTool,
    dn2uuid: DN2UUID,
    mo_person: EmployeeUUID,
) -> None:
    # Create an LDAP account and fetch its DN + LDAP UUID
    dn = combine_dn_strings(await add_ldap_person("account1", "0101700000"))
    ldap_uuid = await dn2uuid(dn)

    # Cannot find any DNs as the LDAP account is not attached to the mo person
    with capture_logs() as cap_logs:
        dns = await sync_tool.dataloader.find_mo_employee_dn_by_itsystem(mo_person)
        assert dns == set()
    assert cap_logs == []

    # Ensure that no link exists between the mo person and LDAP account
    ituser_map = await read_mo_mapping_uuids(mo_person)
    assert ituser_map == {}

    # Create the link between the mo person and the LDAP account
    with capture_logs() as cap_logs:
        await sync_tool.ensure_ituser_link(mo_person, dn)
    events = {log["event"] for log in cap_logs}
    assert "Creating link as it is missing" in events

    # Ensure we can read the link between the mo person and LDAP account
    ituser_map = await read_mo_mapping_uuids(mo_person)
    assert ituser_map == {ldap_uuid: None}

    # Ensure that we can find the DN now using the mo person
    with capture_logs() as cap_logs:
        dns = await sync_tool.dataloader.find_mo_employee_dn_by_itsystem(mo_person)
        assert dns == {dn}
    assert cap_logs == [
        {
            "event": "Looking for LDAP object",
            "log_level": "info",
            "unique_ldap_uuid": ldap_uuid,
        },
        {
            "dns": {dn},
            "employee_uuid": mo_person,
            "event": "Found DN(s) using ITUser lookup",
            "log_level": "info",
        },
    ]

    # Ensure that the link was not deleted by the previous call
    ituser_map = await read_mo_mapping_uuids(mo_person)
    assert ituser_map == {ldap_uuid: None}

    # Delete the LDAP account
    await ldap_delete_by_dn(dn)

    # Ensure that the link between the mo person and the LDAP account still exists in MO
    ituser_map = await read_mo_mapping_uuids(mo_person)
    assert ituser_map == {ldap_uuid: None}

    # Rerun the mapping code, this should delete the link and return no match
    with capture_logs() as cap_logs:
        dns = await sync_tool.dataloader.find_mo_employee_dn_by_itsystem(mo_person)
        assert dns == set()
    assert cap_logs == [
        {
            "event": "Looking for LDAP object",
            "log_level": "info",
            "unique_ldap_uuid": ldap_uuid,
        },
        {
            "event": "Unable to convert LDAP UUID to DN",
            "log_level": "warning",
            "uuid": ldap_uuid,
        },
        {
            "event": "Terminating correlation link it-user",
            "log_level": "info",
            "uuid": ANY,
        },
    ]

    # Ensure that the link beteen the mo person and the LDAP account was terminated
    ituser_map = await read_mo_mapping_uuids(mo_person)
    assert ituser_map == {ldap_uuid: mo_today()}
