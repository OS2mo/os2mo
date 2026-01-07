# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
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
from mora.access_log import access_log
from mora.auth.keycloak.models import Token
from mora.auth.middleware import NO_AUTH_MIDDLEWARE_UUID
from mora.auth.middleware import set_authenticated_user
from mora.db import AccessLogOperation
from mora.db import AccessLogRead
from mora.db import AsyncSession
from mora.graphapi.versions.latest.access_log import AccessLogModel
from mora.mapping import ADMIN
from mora.util import DEFAULT_TIMEZONE
from more_itertools import flatten
from more_itertools import one
from sqlalchemy import delete
from sqlalchemy import select

from tests.conftest import BRUCE_UUID
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import admin_auth_uuid


async def assert_empty_access_log_tables(session) -> None:
    query = select(AccessLogOperation)
    result = list(await session.scalars(query))
    assert result == []

    query = select(AccessLogRead)
    result = list(await session.scalars(query))
    assert result == []


async def assert_one_access_log_entry(
    session,
    model: str,
    operation: str,
    uuids: list[UUID] | None = None,
    actor: UUID | None = None,
    arguments: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> None:
    actor = actor or NO_AUTH_MIDDLEWARE_UUID
    arguments = arguments or {}
    now = now or (datetime.now(tz=DEFAULT_TIMEZONE) - timedelta(minutes=1))
    uuids = uuids or []

    query = select(AccessLogOperation)
    access_log_operation = one(await session.scalars(query))

    assert access_log_operation.time > now
    assert access_log_operation.actor == actor
    assert access_log_operation.model == model

    assert access_log_operation.operation == operation
    assert access_log_operation.arguments == arguments

    query = select(AccessLogRead)
    reads = list(await session.scalars(query))
    read_uuids = []
    for read in reads:
        assert read.operation_id == access_log_operation.id
        read_uuids.append(read.uuid)

    assert read_uuids == uuids


@pytest.mark.integration_test
async def test_access_log_database(
    empty_db: AsyncSession, set_settings: MonkeyPatch
) -> None:
    """Integrationtest for reading and writing the access log."""

    set_settings(ACCESS_LOG_ENABLE="True")

    await assert_empty_access_log_tables(empty_db)

    uuid = uuid4()
    access_log(empty_db, "test_accesslog", "AccessLog", {}, [uuid])

    await assert_one_access_log_entry(empty_db, "AccessLog", "test_accesslog", [uuid])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_access_log_graphql_self(
    set_settings: MonkeyPatch, graphapi_post: GraphAPIPost
) -> None:
    """Integrationtest for reading and writing the access log."""

    set_settings(ACCESS_LOG_ENABLE="True")
    now = datetime.now(tz=DEFAULT_TIMEZONE)

    query = """
        query ReadAccessLog {
          access_log {
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
    # First call returns nothing, but produces an access log event
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"access_log": {"objects": []}}

    # Next call reads the first calls access log event and makes another
    response = graphapi_post(query)
    assert response.errors is None
    result = one(response.data["access_log"]["objects"])

    assert datetime.fromisoformat(result["time"]) > now
    assert result["actor"] == str(await admin_auth_uuid())
    assert result["model"] == "ACCESS_LOG"
    assert result["uuids"] == []

    # This call reads both access log events (and makes yet another)
    response = graphapi_post(query)
    assert response.errors is None
    old_result, new_result = list(response.data["access_log"]["objects"])

    assert old_result == result

    assert datetime.fromisoformat(new_result["time"]) > now
    assert new_result["actor"] == str(await admin_auth_uuid())
    assert new_result["model"] == "ACCESS_LOG"
    assert new_result["uuids"] == [old_result["id"]]


simple_text = st.text(alphabet=st.characters(whitelist_categories=("L",)), min_size=1)


@st.composite
def access_log_entries_and_filter(
    draw: st.DrawFn,
) -> tuple[list[dict[str, Any]], list[UUID], list[UUID], list[UUID]]:
    access_log_entries = draw(
        st.lists(
            st.fixed_dictionaries(
                {
                    "actor": st.uuids(),
                    "operation": simple_text,
                    "class_name": st.sampled_from(AccessLogModel).map(
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
        graphql_filter(list(flatten([x["uuids"] for x in access_log_entries])))
    )
    actor_filter = draw(graphql_filter([x["actor"] for x in access_log_entries]))
    model_filter = draw(
        graphql_filter(
            [AccessLogModel(x["class_name"]).name for x in access_log_entries]
        )
    )

    return (access_log_entries, uuid_filter, actor_filter, model_filter)


@pytest.mark.integration_test
@settings(
    suppress_health_check=[
        # Running multiple tests on the same database is okay; we clear the access log
        # table manually in the beginning of each test.
        HealthCheck.function_scoped_fixture,
    ],
)
@given(access_log_entries_and_filter=access_log_entries_and_filter())
# TODO: Add support for id filtering
async def test_access_log_filters(
    another_transaction,
    graphapi_post: GraphAPIPost,
    set_session_settings: MonkeyPatch,
    empty_db: AsyncSession,
    access_log_entries_and_filter: tuple[
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
        access_log_entries,
        uuid_filter,
        actor_filter,
        model_filter,
    ) = access_log_entries_and_filter

    # Remove all access log entries present since hypothesis doesn't work with
    # function-scoped fixtures.
    async with another_transaction() as (_, session):
        await session.execute(delete(AccessLogRead))
        await session.execute(delete(AccessLogOperation))

    access_filter_query = """
        query ReadAccessLog($filter: AccessLogFilter) {
          access_log(filter: $filter) {
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

    # Test that the access log is empty
    response = graphapi_post(access_filter_query, {"filter": {}})
    assert response.errors is None
    assert response.data == {"access_log": {"objects": []}}

    # Add access log entries
    set_session_settings(ACCESS_LOG_ENABLE="True")

    async with another_transaction() as (_, session):
        for access_event in access_log_entries:

            async def get_token() -> Token:
                return Token(azp="mo", uuid=access_event["actor"])

            async for _ in set_authenticated_user(get_token):
                # TODO: Set time somehow
                access_log(
                    session,
                    access_event["operation"],
                    access_event["class_name"],
                    {},
                    access_event["uuids"],
                )

    # Disable access-logging itself
    set_session_settings(ACCESS_LOG_ENABLE="False")

    # Test that we can see all our access log entries
    response = graphapi_post(access_filter_query, {"filter": {}})
    assert response.errors is None
    results = list(response.data["access_log"]["objects"])
    assert len(results) == len(access_log_entries)

    # Verify that the access-log logging itself is indeed disabled for this test
    response = graphapi_post(access_filter_query, {"filter": {}})
    assert response.errors is None
    results = list(response.data["access_log"]["objects"])
    assert len(results) == len(access_log_entries)

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
    expected = access_log_entries
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
            lambda x: AccessLogModel(x["class_name"]).name
            in set(filter_object["models"]),
            expected,
        )
    expected = list(expected)

    # Run query and verify equivalence
    response = graphapi_post(
        access_filter_query, {"filter": jsonable_encoder(filter_object)}
    )
    assert response.errors is None
    assert response.data is not None
    objects = response.data["access_log"]["objects"]
    assert len(objects) == len(expected)


@pytest.mark.integration_test
async def test_access_log_disabled(
    empty_db: AsyncSession, set_settings: MonkeyPatch
) -> None:
    """Integrationtest for enabling the access log."""

    await assert_empty_access_log_tables(empty_db)

    set_settings(ACCESS_LOG_ENABLE="False")
    uuid = uuid4()
    access_log(empty_db, "test_access_log", "AccessLog", {}, [uuid])
    await assert_empty_access_log_tables(empty_db)

    set_settings(ACCESS_LOG_ENABLE="True")
    uuid = uuid4()
    access_log(empty_db, "test_access_log", "AccessLog", {}, [uuid])
    await assert_one_access_log_entry(empty_db, "AccessLog", "test_access_log", [uuid])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_access_log_disabled_for_user_graphql(
    set_settings: MonkeyPatch,
    graphapi_post: GraphAPIPost,
) -> None:
    """Integrationtest for selectively disabling the access log (GraphQL)."""

    set_settings(ACCESS_LOG_ENABLE="True")

    query = """
        query ReadAccessLog {
          access_log {
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
    set_settings(ACCESS_LOG_NO_LOG_UUIDS=f'["{admin_uuid}"]')
    # First call returns nothing, and produces nothing
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"access_log": {"objects": []}}

    # Second call returns nothing, and produces nothing
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"access_log": {"objects": []}}

    set_settings(ACCESS_LOG_NO_LOG_UUIDS="[]")
    # First call returns nothing, but produces an access event
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"access_log": {"objects": []}}

    # Second call returns first call access event, and produces yet another
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"access_log": {"objects": [ANY]}}


@pytest.mark.integration_test
async def test_access_log_disabled_for_user(
    empty_db: AsyncSession, set_settings: MonkeyPatch
) -> None:
    """Integrationtest for selectively disabling the access log."""

    set_settings(ACCESS_LOG_ENABLE="True")

    await assert_empty_access_log_tables(empty_db)

    set_settings(ACCESS_LOG_NO_LOG_UUIDS=f'["{NO_AUTH_MIDDLEWARE_UUID}"]')
    uuid = uuid4()
    access_log(empty_db, "test_access_log", "AccessLog", {}, [uuid])
    await assert_empty_access_log_tables(empty_db)

    set_settings(ACCESS_LOG_NO_LOG_UUIDS="[]")
    uuid = uuid4()
    access_log(empty_db, "test_access_log", "AccessLog", {}, [uuid])
    await assert_one_access_log_entry(empty_db, "AccessLog", "test_access_log", [uuid])


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_access_log_graphql_cursor(
    set_settings: MonkeyPatch,
    graphapi_post: GraphAPIPost,
) -> None:
    """Ensure that access logs can be iterated without running indefinitely."""

    set_settings(ACCESS_LOG_ENABLE="True")

    query = """
        query ReadAccessLog($cursor: Cursor) {
          access_log(limit: 1, cursor: $cursor) {
            objects {
                id
            }
            page_info {
              next_cursor
            }
          }
        }
    """
    # First call returns nothing, but produces an access log event
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "access_log": {"objects": [], "page_info": {"next_cursor": None}}
    }

    # Next call reads the first calls access log event and makes another
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "access_log": {"objects": [ANY], "page_info": {"next_cursor": None}}
    }

    # Next call reads the two first calls access log events and makes yet another
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "access_log": {"objects": [ANY], "page_info": {"next_cursor": ANY}}
    }
    next_cursor = response.data["access_log"]["page_info"]["next_cursor"]
    assert next_cursor is not None

    # Check that iteration is not infinite
    response = graphapi_post(query, variables={"cursor": next_cursor})
    assert response.errors is None
    assert response.data == {
        "access_log": {"objects": [ANY], "page_info": {"next_cursor": None}}
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_accesslog_actor_object(
    set_settings: Callable[..., None],
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    create_person: Callable[..., UUID],
) -> None:
    set_settings(ACCESS_LOG_ENABLE="True")
    read_query = """
        query ReadActorAccess($uuid: UUID!) {
          access_log(filter: {uuids: [$uuid]}) {
            objects {
              actor_object {
                display_name
                uuid
              }
            }
          }
        }
    """
    person_uuid = str(create_person())
    bruce_uuid = str(BRUCE_UUID)

    response = graphapi_post(read_query, {"uuid": person_uuid})
    assert response.errors is None
    assert response.data
    for obj in response.data["access_log"]["objects"]:
        assert obj["actor_object"] == {"display_name": "bruce", "uuid": bruce_uuid}

    set_auth(ADMIN, bruce_uuid, preferred_username="new name")
    # Actor names are updated on mutations
    response = graphapi_post("""
    mutation RandomMutation {
      facet_create(input: {user_key: "Example", validity: {from: "2021-01-01"}}) {
        uuid
      }
    }
    """)

    response = graphapi_post(read_query, {"uuid": person_uuid})
    assert response.errors is None
    assert response.data
    for obj in response.data["access_log"]["objects"]:
        assert obj["actor_object"] == {"display_name": "new name", "uuid": bruce_uuid}
