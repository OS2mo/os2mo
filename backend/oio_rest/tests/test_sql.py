# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os
import pathlib
import unittest

import tap.parser

from oio_rest import config
from oio_rest.db import db_templating
from oio_rest.db import get_connection
from oio_rest.tests import util
from oio_rest.tests.util import DBTestCase


class SQLTests(DBTestCase):
    def setUp(self):
        super().setUp()
        with get_connection() as conn, conn.cursor() as curs:
            curs.execute('CREATE EXTENSION "pgtap";')

            curs.execute(
                'CREATE SCHEMA test AUTHORIZATION "{}";'.format(
                    config.get_settings().db_user,
                ),
            )

            for dbfile in pathlib.Path(util.TESTS_DIR).glob("sql/*.sql"):
                curs.execute(dbfile.read_text())

    def tearDown(self):
        super().setUp()

        with get_connection() as conn, conn.cursor() as curs:
            curs.execute("DROP SCHEMA test CASCADE")
            curs.execute('DROP EXTENSION IF EXISTS "pgtap" CASCADE;')

    def test_pgsql(self):
        with get_connection() as conn, conn.cursor() as curs:
            curs.execute("SELECT * FROM runtests ('test'::name)")

            self.assertGreater(curs.rowcount, 0)

            # tap.py doesn't support subtests yet, so strip the line
            # see https://github.com/python-tap/tappy/issues/71
            #
            # please note that the tuple unpacking below is
            # deliberate; we're iterating over over a cursor
            # containing single-item rows
            taptext = "\n".join(line.strip() for (line,) in curs)

        for result in tap.parser.Parser().parse_text(taptext):
            if result.category == "test":
                print(result)

                with self.subTest(result.description):
                    if result.skip:
                        raise unittest.SkipTest()
                    elif not result.ok:
                        self.fail(result.diagnostics or result.description)


class TextTests(unittest.TestCase):
    def test_sql_unchanged(self):
        schema_path = os.path.join(
            util.BASE_DIR, "..", "alembic", "versions", "initial_schema.sql"
        )
        expected_path = pathlib.Path(schema_path)
        expected = expected_path.read_text()
        actual = "\n".join(db_templating.get_sql()) + "\n"
        actual = actual.replace("OWNER TO mox", "OWNER TO {{ mox_user }}")
        self.assertEqual(
            expected,
            actual,
            "SQL changed unexpectedly! We are using Alembic to manage database "
            "changes from now on. Please don't introduce database schema "
            "changes in other ways.",
        )
