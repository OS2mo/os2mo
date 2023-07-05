# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from contextlib import suppress
from uuid import UUID

from mora import config


def validate_session(session_id: str) -> bool:
    """Validate the existence of a session in our legacy sessions."""
    settings = config.get_settings()
    with suppress(ValueError):
        return UUID(session_id) in settings.os2mo_legacy_sessions
    return False
