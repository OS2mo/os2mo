#
# Copyright (c) 2017-2018, Magenta ApS
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

    from selenium.webdriver.support import ui
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains as AC
    from selenium.webdriver.common.by import By
except ImportError:
    selenium = None


SAFARI_PREVIEW_DRIVER = ('/Applications/Safari Technology Preview.app'
                         '/Contents/MacOS/safaridriver')
CHROME_UBUNTU_DRIVER = '/usr/lib/chromium-browser/chromedriver'


@unittest.skip('just too unstable')
@unittest.skipUnless(selenium, 'selenium not installed')
class RightsTests(util.LiveLoRATestCase):
    def assertTableContents(self, expected, element):
        self.assertEqual(
            expected,
            [
                [
                    cell.text
                    for cell in row.find_elements_by_tag_name('td')
                ]
                for row in element.find_elements_by_css_selector('tbody > tr')
            ],
        )

    def get_tab_visibility(self):
        return {
            tab.get_property('innerText').strip(): tab.is_displayed()
            for tab in self.browser.find_elements_by_tag_name('tab-heading')
        }

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

        # 1280x720 is about as small as it gets nowadays...
        cls.browser.set_window_size(1200, 700)

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        cls.browser.quit()

    def test_login(self):
        # logout
        self.browser.delete_all_cookies()
        self.browser.get(self.get_server_url() + '/mo')

        self.browser.implicitly_wait(1)
        self.browser.find_element_by_id("organisationLogin").click()

        self.browser.implicitly_wait(1)
        self.browser.find_element_by_id("elLoginUser").send_keys('admin')
        self.browser.find_element_by_id("elLoginPass").send_keys('secret')
        self.browser.find_element_by_id("elLoginSubmit").click()

        ui.WebDriverWait(self.browser, 1).until(
            EC.invisibility_of_element_located((By.ID, 'loginForm')),
        )

    def test_autocomplete(self):
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
            ui.WebDriverWait(self.browser, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                  '#sys-search .refresh')),
            )

            ui.WebDriverWait(self.browser, 15).until(
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
        self.load_sample_structures()
        self.test_login()

        # a few utility methods
        def wait(id='loading-bar-spinner'):
            'wait for the action spinner to appear, then disappear'

            ui.WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.ID, id)),
            )

            el = self.browser.find_element_by_id(id)
            ui.WebDriverWait(self.browser, 5).until(EC.staleness_of(el))

        self.browser.implicitly_wait(5)
        self.browser.find_element_by_css_selector('treecontrol span').click()

        wait()

        self.assertEqual(
            'Overordnet Enhed',
            self.browser.find_element_by_css_selector(
                '[ng-bind="organisation.activeName"]',
            ).text,
        )

    def test_create_unit_to_infinity_without_contact_channel(self):
        self.load_sample_structures()
        self.test_login()

        # hover over the new org. unit button, and click it
        btn = self.browser.find_element_by_id("elOrgNewBtn")

        hover = AC(self.browser).move_to_element_with_offset(btn, 5, 5).click()
        hover.perform()

        self.browser.implicitly_wait(5)

        self.browser.find_element_by_id('orgStartDate').send_keys('01-01-2016')
        self.browser.find_element_by_name('orgUnitName').send_keys('Ny Enhed Uden Slutdato')

        select = ui.Select(self.browser.find_element_by_name('orgUnitType'))
        select.select_by_visible_text('Afdeling')

        inputel = self.browser.find_element_by_css_selector('[ng-model=valueEnhead]')
        inputel.click()

        self.browser.implicitly_wait(5)

        top_level = self.browser.find_element_by_css_selector(
            '.modal-dialog treecontrol [tree-transclude]',
        )

        self.assertEqual(top_level.text, 'Overordnet Enhed')
        top_level.click()

        self.assertEqual(inputel.get_property('value'), 'Overordnet Enhed')

        self.browser.find_element_by_name('geoLocal').click()

        # focus the address search field
        search_field = self.browser.find_element_by_css_selector(
            '#search-address input[name=query]',
        )
        search_field.click()
        search_field.send_keys('Pilestræde 43, 3')

        dropdown = self.browser.find_element_by_css_selector(
            '#search-address ul.dropdown-menu',
        )

        dropdown.find_element_by_css_selector('li').click()

        self.browser.find_element_by_css_selector('[placeholder=Lokationsnavn]').send_keys(
            'stednavn',
        )

        ui.Select(self.browser.find_element_by_css_selector(
            'form[name=contactChannelForm] select[name=type]',
        )).select_by_visible_text('Telefonnummer')

        ui.Select(self.browser.find_element_by_css_selector(
            'form[name=contactChannelForm] select[name=visibility]',
        )).select_by_visible_text('Hemmeligt')

        self.browser.find_element_by_css_selector(
            'form[name=contactChannelForm] input[name=contact-info]',
        ).send_keys('00000000')

        # NB: horrible UI - we're entering text into the contact channel item, but
        # not actually clicking the "create" button - so we don't get
        # one

        self.browser.find_element_by_id('elOrgCreateOk').click()

        ui.WebDriverWait(self.browser, 1).until(
            EC.invisibility_of_element_located((By.ID, 'elOrgCreateOk')),
        )

        # TODO: check work log

        # we've created the unit, now search for it
        self.browser.find_element_by_css_selector(
            '.input-group-btn > input'
        ).send_keys('Uden Slutdato')
        self.browser.find_element_by_css_selector(
            '.input-group-btn > button'
        ).click()

        self.assertTableContents(
            [
                ['Ny Enhed Uden Slutdato', '01-01-2016', 'infinity', ''],
            ],
            self.browser.find_element_by_id('organisationList'),
        )

        found = self.browser.find_elements_by_css_selector(
            'table#organisationList > tbody > tr'
        )

        self.assertEqual(1, len(found))

        # show it!
        found[0].find_element_by_tag_name('a').click()

        self.browser.implicitly_wait(15)

        unit_tabs = self.browser.find_elements_by_id('elOrgorg-unitTab')

        # yes, three items with the same ID :(
        self.assertEqual(3, len(unit_tabs))

        # Check that present is visible, and the others aren't
        self.assertEqual(
            [True, False, False],
            [v.is_displayed() for v in unit_tabs]
        )
        self.assertEqual(
            {
                'Association': False,
                'Contact Channel': False,
                'Engagement': False,
                'Enhed': True,
                'Leder': False,
                'Lokation': True,
                'Rolle': False,
            },
            self.get_tab_visibility(),
        )

        self.assertTableContents(
            [
                [
                    'Ny Enhed Uden Slutdato',
                    'Afdeling',
                    'Overordnet Enhed',
                    '01-01-2016',
                    'infinity'
                ],
            ],
            unit_tabs[0],
        )

        self.assertEqual(
            'Ny Enhed Uden Slutdato',
            self.browser.find_element_by_css_selector(
                '.org-detail span[ng-bind="organisation.activeName"]',
            ).text,
        )

    def test_create_unit_to_2020_with_contact_channel(self):
        self.load_sample_structures()
        self.test_login()

        # hover over the new org. unit button, and click it
        btn = self.browser.find_element_by_id("elOrgNewBtn")

        hover = AC(self.browser).move_to_element_with_offset(btn, 5, 5).click()
        hover.perform()

        self.browser.implicitly_wait(5)

        self.browser.find_element_by_id('orgStartDate').send_keys('01-01-2016')
        self.browser.find_element_by_id('orgEndDate').send_keys('01-01-2020')
        self.browser.find_element_by_name('orgUnitName').send_keys('Ny Enhed Med Slutdato')

        select = ui.Select(self.browser.find_element_by_name('orgUnitType'))
        select.select_by_visible_text('Afdeling')

        inputel = self.browser.find_element_by_css_selector('[ng-model=valueEnhead]')
        inputel.click()

        self.browser.implicitly_wait(5)

        top_level = self.browser.find_element_by_css_selector(
            '.modal-dialog treecontrol [tree-transclude]',
        )

        self.assertEqual(top_level.text, 'Overordnet Enhed')
        top_level.click()

        self.assertEqual(inputel.get_property('value'), 'Overordnet Enhed')

        self.browser.find_element_by_name('geoLocal').click()

        # focus the address search field
        search_field = self.browser.find_element_by_css_selector(
            '#search-address input[name=query]',
        )
        search_field.click()
        search_field.send_keys('Pilestræde 43, 3')

        dropdown = self.browser.find_element_by_css_selector(
            '#search-address ul.dropdown-menu',
        )

        dropdown.find_element_by_css_selector('li').click()

        self.browser.find_element_by_css_selector('[placeholder=Lokationsnavn]').send_keys(
            'stednavn',
        )

        ui.Select(self.browser.find_element_by_css_selector(
            'form[name=contactChannelForm] select[name=type]',
        )).select_by_visible_text('Telefonnummer')

        ui.Select(self.browser.find_element_by_css_selector(
            'form[name=contactChannelForm] select[name=visibility]',
        )).select_by_visible_text('Hemmeligt')

        self.browser.find_element_by_css_selector(
            'form[name=contactChannelForm] input[name=contact-info]',
        ).send_keys('00000000')

        # NB: horrible UI - actually click the button to create the location
        self.browser.find_element_by_id('elOrgCreateBtn_contact').click()

        self.browser.find_element_by_id('elOrgCreateOk').click()

        ui.WebDriverWait(self.browser, 1).until(
            EC.invisibility_of_element_located((By.ID, 'elOrgCreateOk')),
        )

        # TODO: check work log

        # we've created the unit, now search for it - intentionally incorrectly
        self.browser.find_element_by_css_selector(
            '.input-group-btn > input'
        ).send_keys('Uden Slutdato')
        self.browser.find_element_by_css_selector(
            '.input-group-btn > button'
        ).click()

        # oops, we didn't find anything!
        self.assertTableContents(
            [],
            self.browser.find_element_by_id('organisationList'),
        )

        # we've created the unit, now search for it
        self.browser.find_element_by_css_selector(
            '.input-group-btn > input'
        ).clear()
        self.browser.find_element_by_css_selector(
            '.input-group-btn > input'
        ).send_keys('Med Slutdato')
        self.browser.find_element_by_css_selector(
            '.input-group-btn > button'
        ).click()

        self.assertTableContents(
            [
                ['Ny Enhed Med Slutdato', '01-01-2016', '01-01-2020', ''],
            ],
            self.browser.find_element_by_id('organisationList'),
        )

        found = self.browser.find_elements_by_css_selector(
            'table#organisationList > tbody > tr'
        )

        self.assertEqual(1, len(found))

        # show it!
        found[0].find_element_by_tag_name('a').click()

        self.browser.implicitly_wait(15)

        unit_tabs = self.browser.find_elements_by_id('elOrgorg-unitTab')

        # yes, three items with the same ID :(
        self.assertEqual(3, len(unit_tabs))

        # Check that present is visible, and the others aren't
        self.assertEqual(
            [True, False, False],
            [v.is_displayed() for v in unit_tabs]
        )
        self.assertEqual(
            {
                'Association': False,
                'Contact Channel': True,
                'Engagement': False,
                'Enhed': True,
                'Leder': False,
                'Lokation': True,
                'Rolle': False,
            },
            self.get_tab_visibility(),
        )

        self.assertTableContents(
            [
                [
                    'Ny Enhed Med Slutdato',
                    'Afdeling',
                    'Overordnet Enhed',
                    '01-01-2016',
                    '01-01-2020'
                ],
            ],
            unit_tabs[0],
        )

        self.assertEqual(
            'Ny Enhed Med Slutdato',
            self.browser.find_element_by_css_selector(
                '.org-detail span[ng-bind="organisation.activeName"]',
            ).text,
        )
