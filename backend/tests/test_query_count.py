# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from mora.db import AsyncSession
from more_itertools import one
from sqlalchemy import event

from .conftest import GraphAPIPost


class QueryCounter:
    """Context manager to capture and count SQL queries executed on a database session.

    This class works by listening to SQLAlchemy's 'before_cursor_execute' event
    on the underlying engine of the provided session. It captures the SQL statements
    for later inspection and counting.

    Attributes:
        engine: The SQLAlchemy sync engine associated with the session.
        queries: A list of captured SQL statements.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.engine = session.bind.sync_engine
        self.queries: list[str] = []

    def __enter__(self) -> "QueryCounter":
        event.listen(self.engine, "before_cursor_execute", self._callback)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        event.remove(self.engine, "before_cursor_execute", self._callback)

    async def __aenter__(self) -> "QueryCounter":
        return self.__enter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.__exit__(exc_type, exc_val, exc_tb)

    def _callback(
        self,
        conn: Any,
        cursor: Any,
        statement: str,
        parameters: Any,
        context: Any,
        executemany: bool,
    ) -> None:
        self.queries.append(statement)

    def count(self) -> int:
        return len(self.queries)


def normalize_sql(sql: str) -> str:
    """Normalize SQL by stripping comments and multiple whitespaces.

    We do this to be able to assert using `startswith` without worrying about
    minor whitespace differences or comments.

    Args:
        sql: The SQL string to normalize.

    Returns:
        The normalized SQL string.
    """
    # Strip single-line comments starting with --
    sql = re.sub(r"--.*", "", sql)
    # Collapse all whitespace and newlines to a single space and strip edges
    return re.sub(r"\s+", " ", sql.strip())


@pytest.mark.integration_test
async def test_person_create(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
) -> None:
    given_name = "Ava"
    surname = "Greenleaf"

    # Assert arguments in create query
    # We avoid asserting the full complex ROW structure as it is very verbose and brittle,
    # but we verify that our input data and the resulting UUID are present in the query.
    async with QueryCounter(empty_db) as qc:
        person_uuid = create_person(
            {
                "given_name": given_name,
                "surname": surname,
            }
        )

    assert qc.count() == 3
    q_exists1, q_exists2, q_create = qc.queries
    query_exists_expected = normalize_sql(
        "SELECT EXISTS( SELECT 1 FROM bruger_registrering WHERE bruger_id = %(uuid)s )"
    )
    assert normalize_sql(q_exists1) == query_exists_expected
    assert normalize_sql(q_exists2) == query_exists_expected

    assert normalize_sql(q_create).startswith(
        "SELECT * from as_create_or_import_bruger("
    )
    assert f"'{given_name}'" in q_create
    assert f"'{surname}'" in q_create
    assert f"'{person_uuid}' :: uuid" in q_create


@pytest.mark.integration_test
async def test_person_read_standard(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    person_uuid = create_person()

    query = """
        query GetPerson($uuid: UUID!) {
            employees(filter: { uuids: [$uuid] }) {
                objects {
                    uuid
                    current {
                        given_name
                        surname
                    }
                }
            }
        }
    """

    async with QueryCounter(empty_db) as qc_read:
        response = graphapi_post(query, {"uuid": str(person_uuid)})
        assert response.errors is None

    assert qc_read.count() == 1
    q_lookup = one(qc_read.queries)
    q_lookup_norm = normalize_sql(q_lookup)

    # Standard read uses UUID with dashes and single ::uuid[] casting.
    # Observed: SELECT as_list_bruger( '{uuid-with-dashes}'::uuid[], NULL, '[-infinity,infinity)'::tstzrange ) :: json[];
    expected_sql = (
        f"SELECT as_list_bruger( '{{{person_uuid}}}'::uuid[], NULL, "
        "'[-infinity,infinity)'::tstzrange ) :: json[];"
    )
    assert q_lookup_norm == expected_sql


@pytest.mark.integration_test
async def test_person_read_registration_time_on_current(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    person_uuid = create_person()

    # We use a future date (3050) to ensure the person exists (created 'now' with infinite validity).
    query_at_current = """
        query GetPersonAtCurrent($uuid: UUID!) {
            employees(filter: { uuids: [$uuid] }) {
                objects {
                    uuid
                    current(registration_time: "3050-01-01T00:00:00+00:00") {
                        given_name
                        surname
                    }
                }
            }
        }
    """

    async with QueryCounter(empty_db) as qc_read:
        response = graphapi_post(query_at_current, {"uuid": str(person_uuid)})
        assert response.errors is None

    # Observed behavior: 3 queries
    assert qc_read.count() == 3
    q1, q2, q3 = qc_read.queries

    # Q1: Standard lookup (default validity) uses dashes and single casting.
    q1_norm = normalize_sql(q1)
    expected_q1 = (
        f"SELECT as_list_bruger( '{{{person_uuid}}}'::uuid[], NULL, "
        "'[-infinity,infinity)'::tstzrange ) :: json[];"
    )
    assert q1_norm == expected_q1

    # Q2: Search for ID existence at 3050
    assert normalize_sql(q2).startswith(
        f"SELECT bruger_registrering.bruger_id as id FROM bruger_registrering WHERE (bruger_registrering.registrering).livscykluskode != 'Slettet'::livscykluskode AND bruger_registrering.bruger_id = '{person_uuid}'"
    )
    assert (
        "tstzrange('3050-01-01T00:00:00+00:00'::timestamptz, '3050-01-01T00:00:00.000001+00:00'::timestamptz)"
        in normalize_sql(q2)
    )

    # Q3: Lookup data at 3050. Bitemporal/nested reads use hex UUIDs and double ::uuid[]::uuid[] casting.
    q3_norm = normalize_sql(q3)
    # Using juxtaposition to safely embed quotes without syntax errors
    expected_q3 = (
        f"SELECT as_list_bruger( '{{{person_uuid.hex}}}'::uuid[]::uuid[], '["
        '"3050-01-01 00:00:00+00:00","3050-01-01 00:00:00.000001+00:00")'
        "'::tstzrange, '[-infinity,infinity)'::tstzrange ) :: json[];"
    )
    assert q3_norm == expected_q3


@pytest.mark.integration_test
async def test_person_read_registration_time_on_filter(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    person_uuid = create_person()

    query_filter_only = """
        query GetPersonFilterOnly($uuid: UUID!) {
            employees(filter: { uuids: [$uuid], registration_time: "3050-01-01T00:00:00+00:00" }) {
                objects {
                    uuid
                    current {
                        given_name
                        surname
                    }
                }
            }
        }
    """

    async with QueryCounter(empty_db) as qc_read:
        response = graphapi_post(query_filter_only, {"uuid": str(person_uuid)})
        assert response.errors is None

    # Observed behavior: 2 queries
    assert qc_read.count() == 2
    q1, q2 = qc_read.queries

    # Search for ID at registration_time
    assert normalize_sql(q1).startswith(
        f"SELECT bruger_registrering.bruger_id as id FROM bruger_registrering WHERE (bruger_registrering.registrering).livscykluskode != 'Slettet'::livscykluskode AND bruger_registrering.bruger_id = '{person_uuid}'"
    )
    assert (
        "tstzrange('3050-01-01T00:00:00+00:00'::timestamptz, '3050-01-01T00:00:00.000001+00:00'::timestamptz)"
        in normalize_sql(q1)
    )

    # Lookup data at 3050 uses hex UUIDs and double ::uuid[]::uuid[] casting.
    q2_norm = normalize_sql(q2)
    expected_q2 = (
        f"SELECT as_list_bruger( '{{{person_uuid.hex}}}'::uuid[]::uuid[], '["
        '"3050-01-01 00:00:00+00:00","3050-01-01 00:00:00.000001+00:00")'
        "'::tstzrange, '[-infinity,infinity)'::tstzrange ) :: json[];"
    )
    assert q2_norm == expected_q2


@pytest.mark.integration_test
async def test_person_read_registration_time_on_both(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    person_uuid = create_person()

    query_both = """
        query GetPersonBoth($uuid: UUID!) {
            employees(filter: { uuids: [$uuid], registration_time: "3050-01-01T00:00:00+00:00" }) {
                objects {
                    uuid
                    current(registration_time: "3050-01-01T00:00:00+00:00") {
                        given_name
                        surname
                    }
                }
            }
        }
    """

    async with QueryCounter(empty_db) as qc_read:
        response = graphapi_post(query_both, {"uuid": str(person_uuid)})
        assert response.errors is None

    # Observed behavior: 4 queries
    assert qc_read.count() == 4
    q1, q2, q3, q4 = qc_read.queries

    # Top-level search
    assert normalize_sql(q1).startswith(
        f"SELECT bruger_registrering.bruger_id as id FROM bruger_registrering WHERE (bruger_registrering.registrering).livscykluskode != 'Slettet'::livscykluskode AND bruger_registrering.bruger_id = '{person_uuid}'"
    )
    assert (
        "tstzrange('3050-01-01T00:00:00+00:00'::timestamptz, '3050-01-01T00:00:00.000001+00:00'::timestamptz)"
        in normalize_sql(q1)
    )

    # Top-level lookup at 3050 uses hex UUIDs and double casting.
    q2_norm = normalize_sql(q2)
    expected_at_3050 = (
        f"SELECT as_list_bruger( '{{{person_uuid.hex}}}'::uuid[]::uuid[], '["
        '"3050-01-01 00:00:00+00:00","3050-01-01 00:00:00.000001+00:00")'
        "'::tstzrange, '[-infinity,infinity)'::tstzrange ) :: json[];"
    )
    assert q2_norm == expected_at_3050

    # Nested 'current' search
    assert normalize_sql(q3).startswith(
        f"SELECT bruger_registrering.bruger_id as id FROM bruger_registrering WHERE (bruger_registrering.registrering).livscykluskode != 'Slettet'::livscykluskode AND bruger_registrering.bruger_id = '{person_uuid}'"
    )

    # Nested 'current' lookup at 3050 uses hex UUIDs and double casting.
    q4_norm = normalize_sql(q4)
    assert q4_norm == expected_at_3050


@pytest.mark.integration_test
async def test_person_read_current_at(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    person_uuid = create_person()

    query = """
        query GetPersonAt($uuid: UUID!) {
            employees(filter: { uuids: [$uuid] }) {
                objects {
                    uuid
                    current(at: "3050-01-01T00:00:00+00:00") {
                        given_name
                        surname
                    }
                }
            }
        }
    """

    async with QueryCounter(empty_db) as qc:
        response = graphapi_post(query, {"uuid": str(person_uuid)})
        assert response.errors is None

    # Observed behavior: 2 queries.
    # Q1: employees(filter: {uuids: [$uuid]})
    # Q2: current(at: "3050-01-01...")
    # Both result in 'as_list_bruger' with full 'virkning' range because
    # OS2mo defaults to 'konsolider=True' for these lookups, which
    # forces '[-infinity, infinity)' at the SQL level and performs
    # trimming in Python later.
    assert qc.count() == 2
    q1, q2 = qc.queries

    expected_sql = (
        f"SELECT as_list_bruger( '{{{person_uuid}}}'::uuid[], NULL, "
        "'[-infinity,infinity)'::tstzrange ) :: json[];"
    )
    assert normalize_sql(q1) == expected_sql
    assert normalize_sql(q2) == expected_sql


@pytest.mark.integration_test
async def test_person_read_filter_dates(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    person_uuid = create_person()

    query = """
        query GetPersonFilterDates($uuid: UUID!) {
            employees(filter: {
                uuids: [$uuid],
                from_date: "3050-01-01T00:00:00+00:00",
                to_date: "3051-01-01T00:00:00+00:00"
            }) {
                objects {
                    uuid
                    current {
                        given_name
                        surname
                    }
                }
            }
        }
    """

    async with QueryCounter(empty_db) as qc:
        response = graphapi_post(query, {"uuid": str(person_uuid)})
        assert response.errors is None

    # Observed behavior: 1 query.
    # Even though top-level validity filters are set, consolidation forces
    # the SQL level range to be infinite.
    assert qc.count() == 1
    q1 = one(qc.queries)

    expected_sql = (
        f"SELECT as_list_bruger( '{{{person_uuid}}}'::uuid[], NULL, "
        "'[-infinity,infinity)'::tstzrange ) :: json[];"
    )
    assert normalize_sql(q1) == expected_sql


@pytest.mark.integration_test
async def test_person_read_combined_dates(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    person_uuid = create_person()

    query = """
        query GetPersonCombined($uuid: UUID!) {
            employees(filter: {
                uuids: [$uuid],
                from_date: "3050-01-01T00:00:00+00:00",
                to_date: "3051-01-01T00:00:00+00:00"
            }) {
                objects {
                    uuid
                    current(at: "3050-06-01T00:00:00+00:00") {
                        given_name
                        surname
                    }
                }
            }
        }
    """

    async with QueryCounter(empty_db) as qc:
        response = graphapi_post(query, {"uuid": str(person_uuid)})
        assert response.errors is None

    # Observed behavior: 2 queries.
    # Both queries use infinite range at SQL level due to consolidation.
    assert qc.count() == 2
    q1, q2 = qc.queries

    expected_sql = (
        f"SELECT as_list_bruger( '{{{person_uuid}}}'::uuid[], NULL, "
        "'[-infinity,infinity)'::tstzrange ) :: json[];"
    )
    assert normalize_sql(q1) == expected_sql
    assert normalize_sql(q2) == expected_sql
