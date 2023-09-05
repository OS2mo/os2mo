# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pathlib
from contextlib import suppress

import pytest
from more_itertools import one
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from tap.parser import Parser

from oio_rest import config
from oio_rest.db import dbname_context
from oio_rest.db import get_connection
from oio_rest.db import get_new_connection
from tests.conftest import create_test_database
from tests.db_testing import reset_testing_database
from tests.oio_rest import util


@pytest.fixture(scope="session")
def pgsql_testing_db():
    """Setup a new empty database.

    Yields:
        The newly created databases name.
    """
    with create_test_database("pgsql_empty") as db_name:
        yield db_name


@pytest.fixture(scope="session")
def setup_pgsql_test(pgsql_testing_db: str):
    with get_new_connection(pgsql_testing_db) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            cursor.execute('CREATE EXTENSION "pgtap";')
            cursor.execute(
                'CREATE SCHEMA test AUTHORIZATION "{}";'.format(
                    config.get_settings().db_user,
                )
            )

    yield pgsql_testing_db

    with get_new_connection(pgsql_testing_db) as connection:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            with suppress():
                cursor.execute("DROP SCHEMA test CASCADE")
                cursor.execute('DROP EXTENSION IF EXISTS "pgtap" CASCADE;')


@pytest.fixture
def pgsql_empty_db(setup_pgsql_test: str):
    # Set dbname_context again, as we are just about to run a test,
    # and as it may be set to another testing database
    token = dbname_context.set(setup_pgsql_test)
    reset_testing_database()
    try:
        yield setup_pgsql_test
    finally:
        dbname_context.reset(token)


@pytest.mark.integration_test
@pytest.mark.usefixtures("pgsql_empty_db")
@pytest.mark.parametrize("dbfile", pathlib.Path(util.TESTS_DIR).glob("sql/*.sql"))
def test_pgsql(subtests, dbfile):
    with get_connection() as conn, conn.cursor() as curs:
        # Run the actual test
        curs.execute(dbfile.read_text())
        # Fetch results in TAP format
        curs.execute("SELECT * FROM runtests ('test'::name)")
        assert curs.rowcount > 0
        taptext = "\n".join(map(one, curs))
        # Test is done, rollback changes
        conn.rollback()

    # Parse tap test-results and very if that all tests passed
    tests = Parser().parse_text(taptext)
    tests = filter(lambda result: result.category == "test", tests)
    for test in tests:
        with subtests.test(test.description):
            if test.skip:
                pytest.skip()
            elif not test.ok:
                pytest.fail(test.diagnostics or test.description)
