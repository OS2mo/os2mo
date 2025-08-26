# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import cast
from unittest import TestCase
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from ldap3 import Connection
from more_itertools import one
from structlog.testing import capture_logs

from mo_ldap_import_export.ldapapi import LDAPAPI
from mo_ldap_import_export.types import LDAPUUID


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "False",
    }
)
async def test_convert_ldap_uuids_to_dns(
    ldap_api: LDAPAPI,
    ldap_person_uuid: LDAPUUID,
    ldap_connection: Connection,
) -> None:
    missing_uuid = cast(LDAPUUID, uuid4())

    # Convert empty list
    with capture_logs() as cap_logs:
        result = await ldap_api.convert_ldap_uuids_to_dns(set())
        assert result == {}

    assert cap_logs == []

    # Convert missing LDAP UUID
    with capture_logs() as cap_logs:
        result = await ldap_api.convert_ldap_uuids_to_dns({missing_uuid})
        assert result == {missing_uuid: None}

    assert cap_logs == [
        {
            "event": "Looking for LDAP object",
            "log_level": "info",
            "unique_ldap_uuid": missing_uuid,
        },
        {
            "event": "Unable to convert LDAP UUID to DN",
            "log_level": "warning",
            "uuid": missing_uuid,
        },
    ]

    # Convert existing LDAP UUID
    with capture_logs() as cap_logs:
        result = await ldap_api.convert_ldap_uuids_to_dns({ldap_person_uuid})
        assert result == {
            ldap_person_uuid: "uid=abk,ou=os2mo,o=magenta,dc=magenta,dc=dk"
        }

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
        assert result == {
            missing_uuid: None,
            ldap_person_uuid: "uid=abk,ou=os2mo,o=magenta,dc=magenta,dc=dk",
        }

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
                "event": "Unable to convert LDAP UUID to DN",
                "log_level": "warning",
                "uuid": missing_uuid,
            },
        ],
    )

    # Convert existing UUID, but LDAP is down
    exception = ValueError("BOOM")
    ldap_api.ldap_connection.connection = MagicMock()
    ldap_api.ldap_connection.connection.search.side_effect = exception

    with pytest.raises(ValueError) as exc_info:
        await ldap_api.convert_ldap_uuids_to_dns({ldap_person_uuid})

    assert "Exceptions during UUID2DN translation" in str(exc_info.value)
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, ExceptionGroup)
    assert one(exc_info.value.__cause__.exceptions) == exception
