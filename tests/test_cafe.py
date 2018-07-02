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

from mora import util as mora_util

from . import util


class TestCafeTests(util.LiveLoRATestCase):
    """Run tests with test-cafe."""

    XML_REPORT_FILE = os.path.join(util.REPORTS_DIR, "testcafe.xml")
    JSON_REPORT_FILE = os.path.join(util.REPORTS_DIR, "testcafe.json")
    TEST_DIR = os.path.join(util.BASE_DIR, "e2e-tests")

    def test_with_testcafe(self):
        # Start the testing process
        print("----------------------")
        print("Running testcafe tests")
        print("----------------------")
        print("Against url:", self.get_server_url())
        print("----------------------")

        with util.mock('dawa-ballerup.json', allow_mox=True):
            util.import_fixture('BALLERUP.csv')

        os.makedirs(util.REPORTS_DIR, exist_ok=True)

        env = {
            **os.environ,
            'BASE_URL': self.get_server_url(),
        }

        browser = os.environ.get('BROWSER',
                                 'safari' if platform.system() == 'Darwin'
                                 else 'chromium:headless --no-sandbox')

        process = subprocess.run(
            [
                "node_modules/.bin/testcafe",
                "'{} --no-sandbox'".format(browser),
                self.TEST_DIR,
                "-r", ','.join(["spec",
                                "xunit:" + self.XML_REPORT_FILE,
                                "json:" + self.JSON_REPORT_FILE]),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            cwd=util.BASE_DIR,
            env=env,
        )

        print(process.stdout.decode(), end='')

        try:
            with open(self.JSON_REPORT_FILE, 'rt') as fp:
                res = json.load(fp)
        except IOError:
            res = None

        print("")
        print("Status:")

        if res is None:
            print('FAILED')
        else:
            duration = (
                mora_util.from_iso_time(res['endTime']) -
                mora_util.from_iso_time(res['startTime'])
            )

            print("ran {} tests in {}".format(res['total'], duration))
            print("{} tests passed".format(res['passed']))
            print("{} tests skipped".format(res['skipped']))

        print("")

        self.assertFalse(process.returncode, "Test run failed!")
