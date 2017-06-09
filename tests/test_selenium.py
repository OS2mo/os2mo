#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools
import os
import unittest

import flask_testing

from . import util
from mora import lora

try:
    import selenium
except ImportError:
    selenium = None


@unittest.skipUnless(selenium, 'selenium not installed')
class RightsTests(util.LoRATestCase, flask_testing.LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        from selenium import webdriver
        from selenium.common import exceptions

        driver_name = os.environ.get('BROWSER', 'Firefox')
        driver = getattr(webdriver, driver_name, None)

        if not driver:
            raise unittest.SkipTest('$BROWSER unset or invalid')

        if driver_name == 'Safari':
            preview_app = '/Applications/Safari Technology Preview.app'
            if os.path.isdir(preview_app):
                driver = functools.partial(
                    driver,
                    executable_path=os.path.join(
                        preview_app, 'Contents/MacOS/safaridriver',
                    )
                )

        try:
            cls.browser = driver()
        except Exception as exc:
            raise unittest.SkipTest(exc.args[0])

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        cls.browser.quit()

    def test_login(self):
        # logout
        self.browser.delete_all_cookies()
        self.browser.get(self.get_server_url())

        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        self.browser.implicitly_wait(1)
        self.browser.find_element_by_id("organisationLogin").click()

        self.browser.implicitly_wait(1)
        self.browser.find_element_by_id("elLoginUser").send_keys('admin')
        self.browser.find_element_by_id("elLoginPass").send_keys('secret')
        self.browser.find_element_by_id("elLoginSubmit").click()

        WebDriverWait(self.browser, 1).until(
            EC.invisibility_of_element_located((By.ID, 'loginForm')),
        )
