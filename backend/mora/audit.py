# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from mora.auth.middleware import get_authenticated_user
from mora.config import get_settings
from mora.db import AuditLogOperation
from mora.db import AuditLogRead


def audit_log(
    session: Session | AsyncSession,
    operation: str,
    class_name: str,
    arguments: dict[str, Any],
    uuids: list[UUID],
) -> None:
    """Insert an entry into the audit log.

    Args:
        session: SQLAlchemy sync or async session within an active transaction.
        operation: Name of the current operation.
        class_name: Name of the data entry being accessed.
        arguments: Arguments provided to operation.
        uuids: UUIDs read by the operation.
    """
    settings = get_settings()
    if not settings.audit_readlog_enable:
        return
    if get_authenticated_user() in settings.audit_readlog_no_log_uuids:
        return

    operation = AuditLogOperation(
        actor=get_authenticated_user(),
        model=class_name,
        operation=operation,
        arguments=jsonable_encoder(arguments),
    )
    uuids = [AuditLogRead(operation=operation, uuid=uuid) for uuid in uuids]
    session.add(operation)
    session.add_all(uuids)
