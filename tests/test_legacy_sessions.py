# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from uuid import UUID

import pytest
from fastapi import Request
from more_itertools import one
from structlog.testing import capture_logs

from mora.auth.keycloak.legacy import validate_session
from mora.auth.keycloak.oidc import LEGACY_AUTH_UUID
from mora.auth.keycloak.oidc import legacy_auth_adapter
from mora.config import Settings

ZERO_UUID = UUID("00000000-0000-0000-0000-000000000000")
ONE_UUID = UUID("11111111-1111-1111-1111-111111111111")


@pytest.mark.parametrize(
    "session_id,legacy_sessions,expected",
    [
        ("alfa", [], False),
        ("beta", [], False),
        (str(ZERO_UUID), [], False),
        (str(ZERO_UUID), [ZERO_UUID], True),
        (str(ZERO_UUID), [ONE_UUID], False),
        (str(ZERO_UUID), [ZERO_UUID, ONE_UUID], True),
    ],
)
def test_validate_session(
    session_id: str, legacy_sessions: list[UUID], expected: bool
) -> None:
    assert validate_session(session_id, legacy_sessions) == expected


@pytest.mark.envvar(
    {"OS2MO_LEGACY_SESSIONS": json.dumps(["00000000-0000-0000-0000-000000000000"])}
)
async def test_legacy_session_logs_session_id() -> None:
    """The session id is included in the log when a legacy session is used."""
    session_id = "00000000-0000-0000-0000-000000000000"

    request = Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "query_string": b"",
            "headers": [(b"session", session_id.encode())],
            "client": ("127.0.0.1", 1),
            "server": ("127.0.0.1", 2),
        }
    )

    with capture_logs() as logs:
        token = await legacy_auth_adapter(request, Settings())

    # The valid session authenticates as the legacy actor.
    assert token.uuid == LEGACY_AUTH_UUID

    log = one(entry for entry in logs if entry["event"] == "Legacy session token used")
    assert log["session_id"] == session_id
