#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""Run all end-to-end tests, and report the status."""

import functools
import json
import os
import platform
import subprocess
import traceback
import unittest

from mora import util as mora_util

from . import util

SKIP_FILES = {
    'support.js',
}


class TestCafeTests(util.LiveLoRATestCase):
    """Run tests with test-cafe."""

    TEST_DIR = os.path.join(util.FRONTEND_DIR, "e2e-tests")

    TESTCAFE_COMMAND = os.path.join(util.FRONTEND_DIR,
                                    "node_modules", ".bin", "testcafe")

    @unittest.skipUnless(
        util.is_frontend_built() and os.path.isfile(TESTCAFE_COMMAND),
        'frontend sources & TestCafé command required!',
    )
    @unittest.skipIf(
        'SKIP_TESTCAFE' in os.environ,
        'TestCafé disabled by $SKIP_TESTCAFE!',
    )
    def test_with_testcafe(self):
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

        test_files = sorted(
            os.path.join(dirpath, file_name)
            for dirpath, dirs, file_names in os.walk(self.TEST_DIR)
            for file_name in file_names
            if file_name.endswith('.js') and file_name not in SKIP_FILES
        )

        for test_file in test_files:
            test_name = os.path.splitext(os.path.basename(test_file))[0]

            with self.subTest(test_name):
                # TODO: reset_db shouldn't be private
                self._TestCaseMixin__reset_db()

                with util.mock('dawa-ballerup.json', allow_mox=True):
                    util.import_fixture('BALLERUP.csv')

                xml_report_file = os.path.join(util.REPORTS_DIR,
                                               test_name + ".xml")
                json_report_file = os.path.join(util.REPORTS_DIR,
                                                test_name + ".json")

                process = subprocess.run(
                    [
                        self.TESTCAFE_COMMAND,
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
