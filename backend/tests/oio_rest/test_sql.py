# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os
import pathlib
import unittest

import pytest
from more_itertools import one
from tap.parser import Parser

from oio_rest import config
from oio_rest.db import db_templating
from oio_rest.db import get_connection
from tests.oio_rest import util


@pytest.fixture(scope="session")
def setup_pgsql_test(testing_db: None):
    with get_connection() as conn, conn.cursor() as curs:
        curs.execute('CREATE EXTENSION "pgtap";')

        curs.execute(
            'CREATE SCHEMA test AUTHORIZATION "{}";'.format(
                config.get_settings().db_user,
            )
        )

    yield

    with get_connection() as conn, conn.cursor() as curs:
        curs.execute("DROP SCHEMA test CASCADE")
        curs.execute('DROP EXTENSION IF EXISTS "pgtap" CASCADE;')


@pytest.mark.integration_test
@pytest.mark.usefixtures("setup_pgsql_test", "transactional_connection")
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


@unittest.expectedFailure
class TextTests(unittest.TestCase):
    # TODO: Remove
    def test_sql_unchanged(self):
        schema_path = os.path.join(
            util.BASE_DIR, "..", "alembic", "versions", "initial_schema.sql"
        )
        expected_path = pathlib.Path(schema_path)
        expected = expected_path.read_text()
        actual = "\n".join(db_templating.get_sql()) + "\n"
        actual = actual.replace("OWNER TO mox", "OWNER TO {{ mox_user }}")
        assert expected == actual, (
            "SQL changed unexpectedly!"
            "We are using Alembic to manage database changes from now on."
            "Please don't introduce database schema changes in other ways."
        )
