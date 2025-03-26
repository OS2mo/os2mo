# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json

import pytest
from httpx import AsyncClient
from structlog.testing import capture_logs

TEST_UUID = "00692245-3a5b-4ae3-a55a-cd05aa6af239"


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "url,ignores_mo,ignores_ldap",
    (
        ("/mo2ldap/person", True, False),
        ("/mo2ldap/reconcile", True, False),
        ("/ldap2mo/uuid", False, True),
        ("/ldap2mo/reconcile", False, True),
    ),
)
@pytest.mark.envvar(
    {
        "MO_UUIDS_TO_IGNORE": json.dumps([TEST_UUID]),
        "LDAP_UUIDS_TO_IGNORE": json.dumps([TEST_UUID]),
    }
)
async def test_uuids_to_ignore(
    test_client: AsyncClient, url: str, ignores_mo: bool, ignores_ldap: bool
) -> None:
    with capture_logs() as cap_logs:
        await test_client.post(
            url, content=TEST_UUID, headers={"Content-Type": "text/plain"}
        )

    log_events = [x["event"] for x in cap_logs]
    if ignores_mo:
        assert "MO event ignored due to ignore-list" in log_events
    else:
        assert "MO event ignored due to ignore-list" not in log_events

    if ignores_ldap:
        assert "LDAP event ignored due to ignore-list" in log_events
    else:
        assert "LDAP event ignored due to ignore-list" not in log_events
