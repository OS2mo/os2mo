# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import json
from collections.abc import Awaitable
from collections.abc import Callable
from datetime import datetime

import pytest
from ldap3 import Connection
from more_itertools import one
from structlog.testing import capture_logs

from mo_ldap_import_export.depends import Settings
from mo_ldap_import_export.ldap import ldap_search
from mo_ldap_import_export.types import LDAPUUID
from mo_ldap_import_export.utils import combine_dn_strings


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
        "CONVERSION_MAPPING": json.dumps(
            {
                "mo2ldap": """
                    {% set mo_employee = load_mo_employee(uuid, current_objects_only=False) %}
                    {{
                        {
                            "employeeNumber": mo_employee.cpr_number,
                            "carLicense": mo_employee.uuid|string,
                            "cn": mo_employee.given_name + " " + mo_employee.surname,
                            "sn": mo_employee.surname,
                            "givenName": mo_employee.given_name,
                            "displayName": mo_employee.nickname_given_name + " " + mo_employee.nickname_surname
                        }|tojson
                    }}
                """,
                "username_generator": {
                    "combinations_to_try": ["FFFX", "LLLX"],
                },
            }
        ),
    }
)
async def test_no_log_spam(
    trigger_mo_person: Callable[[], Awaitable[None]],
    ldap_person_uuid: LDAPUUID,
    ldap_org_unit: list[str],
    ldap_connection: Connection,
) -> None:
    """Ensure that we only write to LDAP when there are changes.

    While LDAP is not a bitemporal system like MO, it does have change management, i.e.
    a changelog and modifyTimestamps which change whenever an entity is updated.

    This test ensures that we only write to LDAP when there are actual changes, i.e.
    that we do not write noop changes to LDAP, as we may otherwise spam the change
    management with empty events, triggering our own reconciliation and filling the
    customers changelogs.
    """

    async def get_ldap_modify_time() -> datetime:
        settings = Settings()
        response, _ = await ldap_search(
            ldap_connection,
            search_base=combine_dn_strings(ldap_org_unit),
            search_filter=f"({settings.ldap_unique_id_field}={ldap_person_uuid})",
            attributes=["modifyTimestamp"],
        )
        employee = one(response)
        modify_timestamp = employee["attributes"]["modifyTimestamp"]
        assert isinstance(modify_timestamp, datetime)
        return modify_timestamp

    # Fetch the modifyTimestamp on our LDAP account
    modify_time_start = await get_ldap_modify_time()
    await asyncio.sleep(1)

    # Forcefully synchronizing changes data the first time
    with capture_logs() as cap_logs:
        await trigger_mo_person()
    events = [m["event"] for m in cap_logs]
    assert "Not writing to LDAP as changeset is empty" not in events
    assert "Uploading object" in events

    # Fetch the modifyTimestamp after our write, and check that it is now later
    modify_time_write = await get_ldap_modify_time()
    assert modify_time_start < modify_time_write
    await asyncio.sleep(1)

    # Forcefully synchronizing again does not change data
    with capture_logs() as cap_logs:
        await trigger_mo_person()
    events = [m["event"] for m in cap_logs]
    assert "Not writing to LDAP as changeset is empty" in events
    assert "Uploading object" not in events

    # Fetch the modifyTimestamp after our non-write, and check that it is the same
    modify_time_noop = await get_ldap_modify_time()
    assert modify_time_write == modify_time_noop
