# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from functools import wraps
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from more_itertools import one
from psycopg2.extensions import cursor
from psycopg2.extras import execute_values
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from mora.auth.middleware import get_authenticated_user
from mora.config import get_settings
from mora.db import AuditLogOperation
from mora.db import AuditLogRead


def if_audit(function: Callable) -> Callable:
    """Disable function if auditing is disabled.

    Args:
        function: The function to call if auditing is enabled.

    Returns:
        Callable that only calls `function` if auditing is enabled.
    """

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        settings = get_settings()
        if not settings.audit_readlog_enable:
            return

        if get_authenticated_user() in settings.audit_readlog_no_log_uuids:
            return

        return function(*args, **kwargs)

    return wrapper


@if_audit
def audit_log_lora(
    cursor: cursor,
    operation: str,
    class_name: str,
    arguments: dict[str, Any],
    uuids: list[UUID],
) -> None:
    """Insert an entry into the audit log.

    Args:
        cursor: psycopg2 database cursor within an active transaction.
        operation: Name of the current operation.
        class_name: Name of the data entry being accessed.
        arguments: Arguments provided to operation.
        uuids: UUIDs read by the operation.
    """
    operation_query = """
    INSERT INTO
        audit_log_operation (time, actor, model, operation, arguments)
    VALUES
        (now(), %(actor)s, %(model)s, %(operation)s, %(arguments)s)
    RETURNING id
    """
    cursor.execute(
        operation_query,
        {
            "actor": str(get_authenticated_user()),
            "model": class_name,
            "operation": operation,
            "arguments": jsonable_encoder(arguments),
        },
    )
    operation_uuid = one(cursor.fetchone())

    insert_query = """
    INSERT INTO
        audit_log_read (operation_id, uuid)
    VALUES %s
    """
    execute_values(
        cursor, insert_query, [(operation_uuid, uuid) for uuid in uuids], page_size=100
    )


@if_audit
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
    operation = AuditLogOperation(
        actor=get_authenticated_user(),
        model=class_name,
        operation=operation,
        arguments=jsonable_encoder(arguments),
    )
    uuids = [AuditLogRead(operation=operation, uuid=uuid) for uuid in uuids]
    session.add(operation)
    session.add_all(uuids)
