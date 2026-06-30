# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest
from fastapi import Request
from more_itertools import one
from structlog.testing import capture_logs

from mora.auth.keycloak.legacy import validate_session
from mora.auth.keycloak.oidc import LEGACY_AUTH_UUID
from mora.auth.keycloak.oidc import legacy_auth_adapter


@pytest.mark.parametrize(
    "session_id,environmental_variable,expected",
    [
        ("alfa", "[]", False),
        ("beta", "[]", False),
        ("00000000-0000-0000-0000-000000000000", "[]", False),
        (
            "00000000-0000-0000-0000-000000000000",
            '["00000000-0000-0000-0000-000000000000"]',
            True,
        ),
        (
            "00000000-0000-0000-0000-000000000000",
            '["11111111-1111-1111-1111-111111111111"]',
            False,
        ),
        (
            "00000000-0000-0000-0000-000000000000",
            '["00000000-0000-0000-0000-000000000000", "11111111-1111-1111-1111-111111111111"]',
            True,
        ),
    ],
)
def test_validate_session(
    set_settings: Callable[..., None],
    session_id: str,
    environmental_variable: list[UUID],
    expected: bool,
) -> None:
    set_settings(
        **{
            "OS2MO_LEGACY_SESSIONS": environmental_variable,
        }
    )
    result = validate_session(session_id)
    assert result == expected


async def test_legacy_session_logs_session_id(
    set_settings: Callable[..., None],
) -> None:
    """The session id is included in the log when a legacy session is used."""
    session_id = "00000000-0000-0000-0000-000000000000"
    set_settings(OS2MO_LEGACY_SESSIONS=f'["{session_id}"]')

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
        token = await legacy_auth_adapter(request)

    # The valid session authenticates as the legacy actor.
    assert token.uuid == LEGACY_AUTH_UUID

    log = one(entry for entry in logs if entry["event"] == "Legacy session token used")
    assert log["session_id"] == session_id
