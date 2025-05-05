# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora.auth.middleware import get_authenticated_user
from mora.config import get_settings
from mora.db import AccessLogOperation
from mora.db import AccessLogRead
from mora.db import AsyncSession


def access_log(
    session: AsyncSession,
    operation: str,
    class_name: str,
    arguments: dict[str, Any],
    uuids: list[UUID],
) -> None:
    """Insert an entry into the access log.

    Args:
        session: SQLAlchemy sync or async session within an active transaction.
        operation: Name of the current operation.
        class_name: Name of the data entry being accessed.
        arguments: Arguments provided to operation.
        uuids: UUIDs read by the operation.
    """
    settings = get_settings()
    if not settings.access_log_enable:
        return
    if get_authenticated_user() in settings.access_log_no_log_uuids:
        return

    operation = AccessLogOperation(
        actor=get_authenticated_user(),
        model=class_name,
        operation=operation,
        arguments=jsonable_encoder(arguments),
    )
    uuids = [AccessLogRead(operation=operation, uuid=uuid) for uuid in uuids]
    session.add(operation)
    session.add_all(uuids)
