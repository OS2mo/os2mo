# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from tests.util import ConfigTestCase


class Tests(ConfigTestCase):

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

    def test_inconsistent_settings(self):
        """
        Test that the conf module will raise in exception if the configuration
        settings are inconsistent.
        """

        self.set_global_conf((('show_roles', 'True'),
                              ('show_roles', 'True')))

        url = '/service/configuration'
        payload = {"org_units": {"show_roles": "False"}}
        assertion_raised = False
        try:
            self.assertRequest(url, json=payload)
        except Exception:
            assertion_raised = True
        self.assertTrue(assertion_raised)

    def test_global_user_settings_write(self):
        """
        Test that it is possible to write a global setting and read it back.
        """

        url = '/service/configuration'

        payload = {"org_units": {"show_roles": "False"}}
        self.assertRequest(url, json=payload)
        user_settings = self.assertRequest(url)
        self.assertTrue(user_settings['show_roles'] is False)

        payload = {"org_units": {"show_roles": "True"}}
        self.assertRequest(url, json=payload)
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
        self.assertRequest(url, json=payload)

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
        self.assertRequest(url, json=payload)
        payload = {"org_units": {"show_location": "False"}}
        self.assertRequest(url, json=payload)

        service_url = '/service/ou/{}/'.format(uuid)
        response = self.assertRequest(service_url)
        user_settings = response['user_settings']['orgunit']
        print(user_settings)
        self.assertTrue(user_settings['show_user_key'])
        self.assertFalse(user_settings['show_location'])
