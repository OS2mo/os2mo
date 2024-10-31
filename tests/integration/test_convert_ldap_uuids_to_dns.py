# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest import TestCase
from unittest.mock import ANY
from unittest.mock import MagicMock
from uuid import UUID
from uuid import uuid4

import pytest
from ldap3 import Connection
from ldap3.core.exceptions import LDAPResponseTimeoutError
from more_itertools import one
from structlog.testing import capture_logs

from mo_ldap_import_export.ldapapi import LDAPAPI


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
async def test_convert_ldap_uuids_to_dns(
    ldap_api: LDAPAPI,
    ldap_person_uuid: UUID,
    ldap_connection: Connection,
) -> None:
    missing_uuid = uuid4()

    # Convert empty list
    with capture_logs() as cap_logs:
        result = await ldap_api.convert_ldap_uuids_to_dns(set())
        assert result == set()

    assert cap_logs == []

    # Convert missing LDAP UUID
    with capture_logs() as cap_logs:
        result = await ldap_api.convert_ldap_uuids_to_dns({missing_uuid})
        assert result == set()

    assert cap_logs == [
        {
            "event": "Looking for LDAP object",
            "log_level": "info",
            "unique_ldap_uuid": missing_uuid,
        },
        {
            "event": "Unable to convert LDAP UUIDs to DNs",
            "log_level": "warning",
            "not_found": ANY,
        },
    ]

    # Convert existing LDAP UUID
    with capture_logs() as cap_logs:
        result = await ldap_api.convert_ldap_uuids_to_dns({ldap_person_uuid})
        assert result == {"uid=abk,ou=os2mo,o=magenta,dc=magenta,dc=dk"}

    assert cap_logs == [
        {
            "event": "Looking for LDAP object",
            "log_level": "info",
            "unique_ldap_uuid": ldap_person_uuid,
        },
    ]

    # Convert existing and non-existing LDAP UUIDs
    with capture_logs() as cap_logs:
        result = await ldap_api.convert_ldap_uuids_to_dns(
            {ldap_person_uuid, missing_uuid}
        )
        assert result == {"uid=abk,ou=os2mo,o=magenta,dc=magenta,dc=dk"}

    TestCase().assertCountEqual(
        cap_logs,
        [
            {
                "event": "Looking for LDAP object",
                "log_level": "info",
                "unique_ldap_uuid": ldap_person_uuid,
            },
            {
                "event": "Looking for LDAP object",
                "log_level": "info",
                "unique_ldap_uuid": missing_uuid,
            },
            {
                "event": "Unable to convert LDAP UUIDs to DNs",
                "log_level": "warning",
                "not_found": ANY,
            },
        ],
    )

    # Convert existing UUID, but LDAP is down
    # Save original socket to restore it later
    sock = ldap_connection.socket
    # Replace socket with broken connection mock
    socket_mock = MagicMock()
    socket_mock.side_effect = ValueError("BOOM")
    ldap_connection.socket = socket_mock

    with pytest.raises(ExceptionGroup) as exc_info:
        await ldap_api.convert_ldap_uuids_to_dns({ldap_person_uuid})

    assert "Exceptions during UUID2DN translation" in str(exc_info.value)
    exception = one(exc_info.value.exceptions)
    assert isinstance(exception, LDAPResponseTimeoutError)

    # Restore socket so cleanup works
    ldap_connection.socket = sock
