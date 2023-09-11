# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID
from uuid import uuid4

import pytest
from _pytest.monkeypatch import MonkeyPatch
from more_itertools import one
from sqlalchemy import select

from mora.audit import audit_log
from mora.db import AuditLogOperation as AuditLogOperation
from mora.db import AuditLogRead
from mora.db import get_sessionmaker
from mora.util import DEFAULT_TIMEZONE
from oio_rest.config import get_settings as lora_get_settings
from oio_rest.db import _get_dbname
from tests.conftest import admin_auth_uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_auditlog_database(set_settings: MonkeyPatch) -> None:
    """Integrationtest for reading and writing the auditlog."""

    set_settings(AUDIT_READLOG_ENABLE="True")

    lora_settings = lora_get_settings()
    sessionmaker = get_sessionmaker(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name=_get_dbname(),
    )
    session = sessionmaker()
    async with session.begin():
        query = select(AuditLogOperation)
        result = list(await session.scalars(query))
        assert result == []

        query = select(AuditLogRead)
        result = list(await session.scalars(query))
        assert result == []

    uuid = uuid4()
    now = datetime.now(tz=DEFAULT_TIMEZONE)
    async with session.begin():
        audit_log(session, "test_auditlog", "AuditLog", {}, [uuid])

    async with session.begin():
        query = select(AuditLogOperation)
        operation = one(await session.scalars(query))

        assert operation.time > now
        assert operation.actor == UUID("42c432e8-9c4a-11e6-9f62-873cf34a735f")
        assert operation.model == "AuditLog"

        assert operation.operation == "test_auditlog"
        assert operation.arguments == {}

        query = select(AuditLogRead)
        read = one(await session.scalars(query))
        assert read.operation_id == operation.id
        assert read.uuid == uuid


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_auditlog_graphql_self(set_settings: MonkeyPatch, graphapi_post) -> None:
    """Integrationtest for reading and writing the auditlog."""

    set_settings(AUDIT_READLOG_ENABLE="True")
    now = datetime.now(tz=DEFAULT_TIMEZONE)

    query = """
        query ReadAuditLog {
          auditlog {
            objects {
              id
              time
              actor
              model
              uuids
            }
          }
        }
    """
    # First call returns nothing, but produces an audit event
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"auditlog": {"objects": []}}

    # Next call reads the first calls audit event and makes another
    response = graphapi_post(query)
    assert response.errors is None
    result = one(response.data["auditlog"]["objects"])

    assert datetime.fromisoformat(result["time"]) > now
    assert result["actor"] == str(await admin_auth_uuid())
    assert result["model"] == "AuditLog"
    assert result["uuids"] == []

    # This call reads both audit events (and makes yet another)
    response = graphapi_post(query)
    assert response.errors is None
    results = list(response.data["auditlog"]["objects"])
    ordered_results = sorted(
        results, key=lambda result: datetime.fromisoformat(result["time"])
    )
    old_result, new_result = ordered_results

    assert old_result == result

    assert datetime.fromisoformat(new_result["time"]) > now
    assert new_result["actor"] == str(await admin_auth_uuid())
    assert new_result["model"] == "AuditLog"
    assert new_result["uuids"] == [old_result["id"]]
