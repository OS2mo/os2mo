# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from datetime import timedelta
from typing import Any
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
from mora.service.autocomplete.employees import search_employees
from mora.service.autocomplete.orgunits import search_orgunits
from mora.util import DEFAULT_TIMEZONE
from oio_rest.config import get_settings as lora_get_settings
from oio_rest.db import _get_dbname
from tests.conftest import admin_auth_uuid


def create_sessionmaker():
    lora_settings = lora_get_settings()
    return get_sessionmaker(
        user=lora_settings.db_user,
        password=lora_settings.db_password,
        host=lora_settings.db_host,
        name=_get_dbname(),
    )


async def ensure_empty_audit_tables(sessionmaker) -> None:
    session = sessionmaker()
    async with session.begin():
        query = select(AuditLogOperation)
        result = list(await session.scalars(query))
        assert result == []

        query = select(AuditLogRead)
        result = list(await session.scalars(query))
        assert result == []


async def assert_one_audit_entry(
    sessionmaker,
    model: str,
    operation: str,
    uuids: list[UUID] | None = None,
    actor: UUID | None = None,
    arguments: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> None:
    actor = actor or UUID("42c432e8-9c4a-11e6-9f62-873cf34a735f")
    arguments = arguments or {}
    now = now or (datetime.now(tz=DEFAULT_TIMEZONE) - timedelta(minutes=1))
    uuids = uuids or []

    session = sessionmaker()
    async with session.begin():
        query = select(AuditLogOperation)
        audit_operation = one(await session.scalars(query))

        assert audit_operation.time > now
        assert audit_operation.actor == actor
        assert audit_operation.model == model

        assert audit_operation.operation == operation
        assert audit_operation.arguments == arguments

        query = select(AuditLogRead)
        reads = list(await session.scalars(query))
        read_uuids = []
        for read in reads:
            assert read.operation_id == audit_operation.id
            read_uuids.append(read.uuid)

        assert read_uuids == uuids


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_auditlog_database(set_settings: MonkeyPatch) -> None:
    """Integrationtest for reading and writing the auditlog."""

    set_settings(AUDIT_READLOG_ENABLE="True")

    sessionmaker = create_sessionmaker()
    await ensure_empty_audit_tables(sessionmaker)

    uuid = uuid4()

    session = sessionmaker()
    async with session.begin():
        audit_log(session, "test_auditlog", "AuditLog", {}, [uuid])

    await assert_one_audit_entry(sessionmaker, "AuditLog", "test_auditlog", [uuid])


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


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_search_employees(set_settings: MonkeyPatch) -> None:
    set_settings(AUDIT_READLOG_ENABLE="True")

    sessionmaker = create_sessionmaker()
    await ensure_empty_audit_tables(sessionmaker)

    results = await search_employees(sessionmaker, "")
    assert results == []

    await assert_one_audit_entry(
        sessionmaker, "Bruger", "search_employees", arguments={"at": None, "query": ""}
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_search_orgunits(set_settings: MonkeyPatch) -> None:
    set_settings(AUDIT_READLOG_ENABLE="True")

    sessionmaker = create_sessionmaker()
    await ensure_empty_audit_tables(sessionmaker)

    results = await search_orgunits(sessionmaker, "")
    assert results == []

    await assert_one_audit_entry(
        sessionmaker,
        "OrganisationEnhed",
        "search_orgunits",
        arguments={"at": None, "query": ""},
    )
