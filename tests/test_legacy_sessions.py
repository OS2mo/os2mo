# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from uuid import UUID

import pytest
from mora.auth.keycloak.legacy import validate_session


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
