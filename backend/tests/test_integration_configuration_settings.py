# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from mora.config import Settings, NavLink

from tests import util

from tests.cases import ConfigTestCase

from mora.conf_db import set_configuration


class Tests(ConfigTestCase):
    def setUp(self):
        super().setUp()
        set_configuration({
            "org_units": {
                "show_location": True,
                "show_user_key": True,
                "show_roles": True,
            }
        })

    def test_global_user_settings_read(self):
        """
        Test that it is possible to correctly read default global settings.
        """
        url = '/service/configuration'
        user_settings = self.assertRequest(url)
        self.assertTrue('show_location' in user_settings)
        self.assertTrue('show_user_key' in user_settings)
        self.assertTrue('show_roles' in user_settings)
        self.assertTrue(user_settings['show_location'] is True)

    def test_global_user_settings_write(self):
        """
        Test that it is no longer possible to write a global setting
        """

        url = '/service/configuration'

        payload = {"org_units": {"show_roles": "False"}}
        self.assertRequest(url, json=payload, status_code=410)
        user_settings = self.assertRequest(url)
        self.assertTrue(user_settings['show_roles'] is True)

        payload = {"org_units": {"show_roles": "True"}}
        self.assertRequest(url, json=payload, status_code=410)
        user_settings = self.assertRequest(url)
        self.assertTrue(user_settings['show_roles'] is True)

    def test_ou_user_settings(self):
        """
        Test that reading and writing settings on units works corrcectly.
        """

        self.load_sample_structures()
        uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        payload = {"org_units": {"show_user_key": "True"}}
        url = '/service/ou/{}/configuration'.format(uuid)
        self.assertRequest(url, json=payload, status_code=410)

        user_settings = self.assertRequest(url)
        self.assertTrue(user_settings['show_user_key'] is True)

    def test_ou_service_response(self):
        """
        Test that the service endpoint for units returns the correct
        configuration settings, including that this endpoint should convert
        the magic strings 'True' and 'False' into boolean values.
        """

        self.load_sample_structures()
        uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        url = '/service/ou/{}/configuration'.format(uuid)
        payload = {"org_units": {"show_user_key": "True"}}
        self.assertRequest(url, json=payload, status_code=410)
        payload = {"org_units": {"show_location": "False"}}
        self.assertRequest(url, json=payload, status_code=410)

        service_url = '/service/ou/{}/'.format(uuid)
        response = self.assertRequest(service_url)
        user_settings = response['user_settings']['orgunit']
        self.assertTrue(user_settings['show_user_key'])
        self.assertTrue(user_settings['show_location'])


class TestNavLink(ConfigTestCase):
    """
    Test the retrieval of "nav links" via the "/service/navlinks" endpoint
    """

    def setUp(self):
        super().setUp()
        self.url = '/service/navlinks'

    def test_empty_list(self):
        empty_list = self.assertRequest(self.url)
        self.assertSequenceEqual(empty_list, [{}])

    def test_populated_list(self):
        href = "http://google.com"
        text = "Google"

        with util.override_config(Settings(navlinks=[NavLink(href=href, text=text)])):
            populated_list = self.assertRequest(self.url)
        self.assertEqual(len(populated_list), 1)
        self.assertEqual(populated_list[0]["href"], href)
        self.assertEqual(populated_list[0]["text"], text)
