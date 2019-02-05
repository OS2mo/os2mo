#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""Run all end-to-end tests, and report the status."""

import json
import os
import platform
import subprocess
import traceback
import unittest

import psycopg2
import mora.settings as settings

from mora import util as mora_util
from oio_rest.utils import test_support

from . import util

SKIP_FILES = {
    'support.js',
}


TEST_DIR = os.path.join(util.FRONTEND_DIR, "e2e-tests")

TESTCAFE_COMMAND = os.path.join(util.FRONTEND_DIR,
                                "node_modules", ".bin", "testcafe")

TEST_FILES = sorted(
    os.path.join(dirpath, file_name)
    for dirpath, dirs, file_names in os.walk(TEST_DIR)
    for file_name in file_names
    if (file_name.endswith('.js') and
        not file_name.startswith('.') and
        file_name not in SKIP_FILES)
)


class TestCafeTests(util.LiveLoRATestCase):
    """Run tests with test-cafe."""

    def _create_conf_data(self, inconsistent=False):

        defaults = {'show_roles': 'True',
                    'show_user_key': 'False',
                    'show_location': 'True'}

        p_url = test_support.psql().url()
        p_port = p_url[p_url.rfind(':') + 1:p_url.rfind('/')]

        with psycopg2.connect(p_url) as conn:
            conn.autocommit = True
            with conn.cursor() as curs:
                try:
                    curs.execute(
                        "CREATE USER {} WITH ENCRYPTED PASSWORD '{}'".format(
                            settings.USER_SETTINGS_DB_USER,
                            settings.USER_SETTINGS_DB_PASSWORD
                        )
                    )
                except psycopg2.ProgrammingError:
                    curs.execute(
                        "DROP DATABASE {};".format(
                            settings.USER_SETTINGS_DB_NAME,
                        )
                    )

                curs.execute(
                    "CREATE DATABASE {} OWNER {};".format(
                        settings.USER_SETTINGS_DB_NAME,
                        settings.USER_SETTINGS_DB_USER
                    )
                )
                curs.execute(
                    "GRANT ALL PRIVILEGES ON DATABASE {} TO {};".format(
                        settings.USER_SETTINGS_DB_NAME,
                        settings.USER_SETTINGS_DB_USER
                    )
                )

        with psycopg2.connect(user=settings.USER_SETTINGS_DB_USER,
                              dbname=settings.USER_SETTINGS_DB_NAME,
                              host=settings.USER_SETTINGS_DB_HOST,
                              password=settings.USER_SETTINGS_DB_PASSWORD,
                              port=p_port) as conn:
            conn.autocommit = True
            with conn.cursor() as curs:

                curs.execute("""
                CREATE TABLE orgunit_settings(id serial PRIMARY KEY,
                object UUID, setting varchar(255) NOT NULL,
                value varchar(255) NOT NULL);
                """)

                query = """
                INSERT INTO orgunit_settings (object, setting, value)
                VALUES (NULL, %s, %s);
                """

                for setting, value in defaults.items():
                    curs.execute(query, (setting, value))

                if inconsistent:
                    # Insert once more, making an invalid configuration set
                    for setting, value in defaults.items():
                        curs.execute(query, (setting, value))
        return p_port

    @unittest.skipUnless(
        util.is_frontend_built() and os.path.isfile(TESTCAFE_COMMAND),
        'frontend sources & TestCafé command required!',
    )
    @unittest.skipIf(
        'SKIP_TESTCAFE' in os.environ,
        'TestCafé disabled by $SKIP_TESTCAFE!',
    )
    def _test_with_testcafe(self, test_file, test_name):
        self.load_sql_fixture()
        p_port = self._create_conf_data()

        # Start the testing process
        print("----------------------")
        print("Running testcafe tests")
        print("----------------------")
        print("Against url:", self.get_server_url())
        print("----------------------")

        os.makedirs(util.REPORTS_DIR, exist_ok=True)

        env = {
            **os.environ,
            'BASE_URL': self.get_server_url(),
        }

        browser = os.environ.get('BROWSER',
                                 'safari' if platform.system() == 'Darwin'
                                 else 'chromium:headless --no-sandbox')

        xml_report_file = os.path.join(util.REPORTS_DIR,
                                       test_name + ".xml")
        json_report_file = os.path.join(util.REPORTS_DIR,
                                        test_name + ".json")

        with util.override_settings(USER_SETTINGS_DB_PORT=p_port):
            process = subprocess.run(
                [
                    TESTCAFE_COMMAND,
                    "'{} --no-sandbox'".format(browser),
                    test_file,
                    "-r", ','.join(["spec",
                                    "xunit:" + xml_report_file,
                                    "json:" + json_report_file]),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                cwd=util.BASE_DIR,
                env=env,
            )

        print(process.stdout.decode(), end='')

        try:
            with open(json_report_file, 'rt') as fp:
                res = json.load(fp)
        except IOError:
            print('FAILED TO GATHER REPORT')
            traceback.print_exc()

            res = None

        if res is not None:
            duration = (
                mora_util.from_iso_time(res['endTime']) -
                mora_util.from_iso_time(res['startTime'])
            )

            print("")
            print("Status:")
            print("ran {} tests in {}".format(res['total'], duration))
            print("{} tests passed".format(res['passed']))
            print("{} tests skipped".format(res['skipped']))

        self.assertEqual(process.returncode, 0, "Test run failed!")

    for test_file in TEST_FILES:
        test_name = os.path.splitext(os.path.basename(test_file))[0]

        def test_with_testcafe(self, test_file=test_file, test_name=test_name):
            self._test_with_testcafe(test_file, test_name)

        locals()['test_' + test_name] = test_with_testcafe

        del test_file, test_name, test_with_testcafe
