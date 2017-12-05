#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import platform
import unittest

from . import util

try:
    import selenium.webdriver
except ImportError:
    selenium = None


SAFARI_PREVIEW_DRIVER = ('/Applications/Safari Technology Preview.app'
                         '/Contents/MacOS/safaridriver')
CHROME_UBUNTU_DRIVER = '/usr/lib/chromium-browser/chromedriver'


@unittest.skipUnless(selenium, 'selenium not installed')
class RightsTests(util.LiveLoRATestCase):
    @classmethod
    def setUpClass(cls):
        default_driver = (
            'Safari'
            if platform.system() == 'Darwin'
            else 'Chrome'
        )
        driver_name = os.environ.get('BROWSER', default_driver)

        driver = getattr(selenium.webdriver, driver_name, None)

        if not driver:
            raise unittest.SkipTest('$BROWSER unset or invalid')

        args = {}

        if driver_name == 'Safari' and os.path.isfile(SAFARI_PREVIEW_DRIVER):
            args.update(executable_path=SAFARI_PREVIEW_DRIVER)

        if driver_name == 'Chrome' and platform.dist()[0] == 'Ubuntu':
            args.update(executable_path=CHROME_UBUNTU_DRIVER)

        try:
            cls.browser = driver(**args)
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

    def test_autocomplete(self):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains as AC
        from selenium.webdriver.common.by import By

        self.load_sample_structures()
        self.test_login()

        # hover over the new org. unit button, and click it
        btn = self.browser.find_element_by_id("elOrgNewBtn")

        hover = AC(self.browser).move_to_element_with_offset(btn, 5, 5).click()
        hover.perform()

        # a few utility methods
        def wait_for_search():
            '''wait for the autocomplete refresh spinner to appear, then
            disappear, so we know that the search occurred and
            succeeded

            '''
            WebDriverWait(self.browser, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                  '#sys-search .refresh')),
            )

            WebDriverWait(self.browser, 15).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR,
                                                    '#sys-search .refresh')),
            )

        def get_result_count():
            '''return the amount of results displayed'''
            dropdown = self.browser.find_element_by_css_selector(
                '#search-address ul.dropdown-menu',
            )

            items = dropdown.find_elements_by_css_selector(
                'li',
            )

            return len(items)

        self.browser.implicitly_wait(5)

        # focus the address search field
        search_field = self.browser.find_element_by_css_selector(
            '#search-address input[name=query]',
        )
        search_field.click()

        # enter a string we know matches many roads in Aarhus
        search_field.send_keys('Pile')

        wait_for_search()
        self.assertEqual(get_result_count(), 20)

        # now enter more letters it so the query matches no roads in Aarhus
        search_field.send_keys('stræ')

        wait_for_search()
        self.assertEqual(get_result_count(), 0)

        # now expand the search to the entire country, and enter more
        # letters it so that the search occurs again
        self.browser.find_element_by_css_selector(
            '.modal.organisationNew .geoLocationLocal'
        ).click()

        self.assertTrue(
            self.browser.find_element_by_css_selector(
                'input[type=checkbox][name=geoLocal]'
            ).is_selected,
            'checkbox is not checked!'
        )

        search_field.send_keys('de')
        wait_for_search()
        self.assertEqual(get_result_count(), 20)

    def test_unit_view(self):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains as AC  # noqa
        from selenium.webdriver.common.by import By

        self.load_sample_structures()
        self.test_login()

        # a few utility methods
        def wait(id='loading-bar-spinner'):
            'wait for the action spinner to appear, then disappear'

            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.ID, id)),
            )

            el = self.browser.find_element_by_id(id)
            WebDriverWait(self.browser, 5).until(EC.staleness_of(el))

        self.browser.implicitly_wait(5)
        self.browser.find_element_by_css_selector('treecontrol span').click()

        wait()

        self.assertEqual(
            'Overordnet Enhed',
            self.browser.find_element_by_css_selector(
                '[ng-bind="organisation.activeName"]',
            ).text,
        )
