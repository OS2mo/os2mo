# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from datetime import timedelta
from typing import Any
from unittest.mock import ANY
from uuid import UUID
from uuid import uuid4

import hypothesis.strategies as st
import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi.encoders import jsonable_encoder
from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from mora.audit import audit_log
from mora.auth.middleware import LORA_USER_UUID
from mora.auth.middleware import set_authenticated_user
from mora.db import AsyncSession
from mora.db import AuditLogOperation
from mora.db import AuditLogRead
from mora.graphapi.versions.latest.audit import AuditLogModel
from mora.service.autocomplete.employees import search_employees
from mora.service.autocomplete.orgunits import search_orgunits
from mora.util import DEFAULT_TIMEZONE
from more_itertools import flatten
from more_itertools import one
from sqlalchemy import delete
from sqlalchemy import select

from tests.conftest import GraphAPIPost
from tests.conftest import admin_auth_uuid


async def assert_empty_audit_tables(session) -> None:
    query = select(AuditLogOperation)
    result = list(await session.scalars(query))
    assert result == []

    query = select(AuditLogRead)
    result = list(await session.scalars(query))
    assert result == []


async def assert_one_audit_entry(
    session,
    model: str,
    operation: str,
    uuids: list[UUID] | None = None,
    actor: UUID | None = None,
    arguments: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> None:
    actor = actor or LORA_USER_UUID
    arguments = arguments or {}
    now = now or (datetime.now(tz=DEFAULT_TIMEZONE) - timedelta(minutes=1))
    uuids = uuids or []

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
async def test_auditlog_database(
    empty_db: AsyncSession, set_settings: MonkeyPatch
) -> None:
    """Integrationtest for reading and writing the auditlog."""

    set_settings(AUDIT_READLOG_ENABLE="True")

    await assert_empty_audit_tables(empty_db)

    uuid = uuid4()
    audit_log(empty_db, "test_auditlog", "AuditLog", {}, [uuid])

    await assert_one_audit_entry(empty_db, "AuditLog", "test_auditlog", [uuid])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_auditlog_graphql_self(
    set_settings: MonkeyPatch, graphapi_post: GraphAPIPost
) -> None:
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
    assert result["model"] == "AUDIT_LOG"
    assert result["uuids"] == []

    # This call reads both audit events (and makes yet another)
    response = graphapi_post(query)
    assert response.errors is None
    old_result, new_result = list(response.data["auditlog"]["objects"])

    assert old_result == result

    assert datetime.fromisoformat(new_result["time"]) > now
    assert new_result["actor"] == str(await admin_auth_uuid())
    assert new_result["model"] == "AUDIT_LOG"
    assert new_result["uuids"] == [old_result["id"]]


@pytest.mark.integration_test
async def test_search_employees(
    empty_db: AsyncSession, set_settings: MonkeyPatch
) -> None:
    set_settings(AUDIT_READLOG_ENABLE="True")

    await assert_empty_audit_tables(empty_db)

    results = await search_employees(empty_db, "")
    assert results == []

    await assert_one_audit_entry(
        empty_db, "Bruger", "search_employees", arguments={"at": None, "query": ""}
    )


@pytest.mark.integration_test
async def test_search_orgunits(
    empty_db: AsyncSession, set_settings: MonkeyPatch
) -> None:
    set_settings(AUDIT_READLOG_ENABLE="True")

    await assert_empty_audit_tables(empty_db)

    results = await search_orgunits(empty_db, "")
    assert results == []

    await assert_one_audit_entry(
        empty_db,
        "OrganisationEnhed",
        "search_orgunits",
        arguments={"at": None, "query": ""},
    )


simple_text = st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1)


@st.composite
def audit_log_entries_and_filter(
    draw: st.DrawFn,
) -> tuple[list[dict[str, Any]], list[UUID], list[UUID], list[UUID]]:
    audit_log_entries = draw(
        st.lists(
            st.fixed_dictionaries(
                {
                    "actor": st.uuids(),
                    "operation": simple_text,
                    "class_name": st.sampled_from(AuditLogModel).map(
                        lambda alm: alm.value
                    ),
                    "uuids": st.lists(st.uuids()),
                    # "time": st.datetimes(),
                }
            )
        )
    )

    def graphql_filter(values: list[Any]):
        return st.one_of(
            st.none(), st.lists(st.sampled_from(values) if values else st.nothing())
        )

    uuid_filter = draw(
        graphql_filter(list(flatten([x["uuids"] for x in audit_log_entries])))
    )
    actor_filter = draw(graphql_filter([x["actor"] for x in audit_log_entries]))
    model_filter = draw(
        graphql_filter([AuditLogModel(x["class_name"]).name for x in audit_log_entries])
    )

    return (audit_log_entries, uuid_filter, actor_filter, model_filter)


@pytest.mark.integration_test
@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay; we clear the auditlog
        # table manually in the beginning of each test.
        HealthCheck.function_scoped_fixture,
    ],
)
@given(audit_log_entries_and_filter=audit_log_entries_and_filter())
# TODO: Add support for id filtering
async def test_auditlog_filters(
    another_transaction,
    graphapi_post: GraphAPIPost,
    set_session_settings: MonkeyPatch,
    empty_db: AsyncSession,
    audit_log_entries_and_filter: tuple[
        list[dict[str, Any]],
        list[UUID],
        list[UUID],
        list[UUID],
    ],
) -> None:
    """Integration equivalence test between python and SQLAlchemy filtering.

    This test ensures that filters on their own AND filters being combined works as expected.
    """
    (
        audit_log_entries,
        uuid_filter,
        actor_filter,
        model_filter,
    ) = audit_log_entries_and_filter

    # Remove all audit log entries present since hypothesis doesn't work with
    # function-scoped fixtures.
    async with another_transaction() as (_, session):
        await session.execute(delete(AuditLogRead))
        await session.execute(delete(AuditLogOperation))

    audit_filter_query = """
        query ReadAuditLog($filter: AuditLogFilter) {
          auditlog(filter: $filter) {
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

    # Test that the audit log is empty
    response = graphapi_post(audit_filter_query, {"filter": {}})
    assert response.errors is None
    assert response.data == {"auditlog": {"objects": []}}

    # Add auditlog entries
    set_session_settings(AUDIT_READLOG_ENABLE="True")

    async with another_transaction() as (_, session):
        for audit_event in audit_log_entries:
            async for _ in set_authenticated_user(audit_event["actor"]):
                # TODO: Set time somehow
                audit_log(
                    session,
                    audit_event["operation"],
                    audit_event["class_name"],
                    {},
                    audit_event["uuids"],
                )

    # Disable audit-logging itself
    set_session_settings(AUDIT_READLOG_ENABLE="False")

    # Test that we can see all our auditlog entries
    response = graphapi_post(audit_filter_query, {"filter": {}})
    assert response.errors is None
    results = list(response.data["auditlog"]["objects"])
    assert len(results) == len(audit_log_entries)

    # Verify that the audit-log logging itself is indeed disabled for this test
    response = graphapi_post(audit_filter_query, {"filter": {}})
    assert response.errors is None
    results = list(response.data["auditlog"]["objects"])
    assert len(results) == len(audit_log_entries)

    # Create filter object
    filter_object = {}
    if uuid_filter is not None:
        filter_object["uuids"] = uuid_filter
    if actor_filter is not None:
        filter_object["actors"] = actor_filter
    if model_filter is not None:
        filter_object["models"] = model_filter
    # TODO: Add support for start + end filtering (time)

    # Calculate expected output by python filtering
    expected = audit_log_entries
    if "uuids" in filter_object:
        expected = filter(
            lambda x: set(x["uuids"]).intersection(set(filter_object["uuids"])),
            expected,
        )
    if "actors" in filter_object:
        expected = filter(
            lambda x: x["actor"] in set(filter_object["actors"]), expected
        )
    if "models" in filter_object:
        expected = filter(
            lambda x: AuditLogModel(x["class_name"]).name
            in set(filter_object["models"]),
            expected,
        )
    expected = list(expected)

    # Run query and verify equivalence
    response = graphapi_post(
        audit_filter_query, {"filter": jsonable_encoder(filter_object)}
    )
    assert response.errors is None
    objects = response.data["auditlog"]["objects"]
    assert len(objects) == len(expected)


@pytest.mark.integration_test
async def test_auditlog_disabled(
    empty_db: AsyncSession, set_settings: MonkeyPatch
) -> None:
    """Integrationtest for enabling the auditlog."""

    await assert_empty_audit_tables(empty_db)

    set_settings(AUDIT_READLOG_ENABLE="False")
    uuid = uuid4()
    audit_log(empty_db, "test_auditlog", "AuditLog", {}, [uuid])
    await assert_empty_audit_tables(empty_db)

    set_settings(AUDIT_READLOG_ENABLE="True")
    uuid = uuid4()
    audit_log(empty_db, "test_auditlog", "AuditLog", {}, [uuid])
    await assert_one_audit_entry(empty_db, "AuditLog", "test_auditlog", [uuid])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_auditlog_disabled_for_user_graphql(
    set_settings: MonkeyPatch,
    graphapi_post: GraphAPIPost,
) -> None:
    """Integrationtest for selectively disabling the auditlog (GraphQL)."""

    set_settings(AUDIT_READLOG_ENABLE="True")

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

    admin_uuid = str(await admin_auth_uuid())
    set_settings(AUDIT_READLOG_NO_LOG_UUIDS=f'["{admin_uuid}"]')
    # First call returns nothing, and produces nothing
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"auditlog": {"objects": []}}

    # Second call returns nothing, and produces nothing
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"auditlog": {"objects": []}}

    set_settings(AUDIT_READLOG_NO_LOG_UUIDS="[]")
    # First call returns nothing, but produces an audit event
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"auditlog": {"objects": []}}

    # Second call returns first call audit event, and produces yet another
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"auditlog": {"objects": [ANY]}}


@pytest.mark.integration_test
async def test_auditlog_disabled_for_user(
    empty_db: AsyncSession, set_settings: MonkeyPatch
) -> None:
    """Integrationtest for selectively disabling the auditlog."""

    set_settings(AUDIT_READLOG_ENABLE="True")

    await assert_empty_audit_tables(empty_db)

    set_settings(AUDIT_READLOG_NO_LOG_UUIDS=f'["{LORA_USER_UUID}"]')
    uuid = uuid4()
    audit_log(empty_db, "test_auditlog", "AuditLog", {}, [uuid])
    await assert_empty_audit_tables(empty_db)

    set_settings(AUDIT_READLOG_NO_LOG_UUIDS="[]")
    uuid = uuid4()
    audit_log(empty_db, "test_auditlog", "AuditLog", {}, [uuid])
    await assert_one_audit_entry(empty_db, "AuditLog", "test_auditlog", [uuid])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_auditlog_graphql_cursor(
    set_settings: MonkeyPatch,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure that auditlogs can be iterated without running indefinitely."""

    set_settings(AUDIT_READLOG_ENABLE="True")

    query = """
        query ReadAuditLog($cursor: Cursor) {
          auditlog(limit: 1, cursor: $cursor) {
            objects {
                id
            }
            page_info {
              next_cursor
            }
          }
        }
    """
    # First call returns nothing, but produces an audit event
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "auditlog": {"objects": [], "page_info": {"next_cursor": None}}
    }

    # Next call reads the first calls audit event and makes another
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "auditlog": {"objects": [ANY], "page_info": {"next_cursor": None}}
    }

    # Next call reads the two first calls audit events and makes yet another
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "auditlog": {"objects": [ANY], "page_info": {"next_cursor": ANY}}
    }
    next_cursor = response.data["auditlog"]["page_info"]["next_cursor"]
    assert next_cursor is not None

    # Check that iteration is not infinite
    response = graphapi_post(query, variables={"cursor": next_cursor})
    assert response.errors is None
    assert response.data == {
        "auditlog": {"objects": [ANY], "page_info": {"next_cursor": None}}
    }
