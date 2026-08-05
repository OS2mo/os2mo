# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from contextlib import suppress
from uuid import UUID


def validate_session(session_id: str, legacy_sessions: list[UUID]) -> bool:
    """Validate the existence of a session in our legacy sessions."""
    with suppress(ValueError):
        return UUID(session_id) in legacy_sessions
    return False
