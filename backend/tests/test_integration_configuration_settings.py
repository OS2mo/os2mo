# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest

import tests.cases
from mora.config import NavLink
from mora.config import Settings
from tests import util


class AsyncTests(tests.cases.AsyncTestCase):
    async def test_global_user_settings_read(self):
        """
        Test that it is possible to correctly read default global settings.
        """
        url = "/service/configuration"
        user_settings = await self.assertRequest(url)
        assert "show_location" in user_settings
        assert "show_user_key" in user_settings
        assert "show_roles" in user_settings
        assert user_settings["show_location"] is True

    async def test_global_user_settings_write(self):
        """
        Test that it is no longer possible to write a global setting
        """

        url = "/service/configuration"

        payload = {"org_units": {"show_roles": "False"}}
        await self.assertRequest(url, json=payload, status_code=410)
        user_settings = await self.assertRequest(url)
        assert user_settings["show_roles"] is True

        payload = {"org_units": {"show_roles": "True"}}
        await self.assertRequest(url, json=payload, status_code=410)
        user_settings = await self.assertRequest(url)
        assert user_settings["show_roles"] is True

    async def test_ou_user_settings(self):
        """
        Test that reading and writing settings on units works corrcectly.
        """

        uuid = "b688513d-11f7-4efc-b679-ab082a2055d0"

        payload = {"org_units": {"show_user_key": "True"}}
        url = f"/service/ou/{uuid}/configuration"
        await self.assertRequest(url, json=payload, status_code=410)

        user_settings = await self.assertRequest(url)
        assert "show_kle" in user_settings


@pytest.mark.usefixtures("load_fixture_data_with_reset")
class LoRaTest(tests.cases.LoRATestCase):
    def test_ou_service_response(self):
        """
        Test that the service endpoint for units returns the correct
        configuration settings, including that this endpoint should convert
        the magic strings 'True' and 'False' into boolean values.
        """
        uuid = "b688513d-11f7-4efc-b679-ab082a2055d0"

        url = f"/service/ou/{uuid}/configuration"
        payload = {"org_units": {"show_user_key": "True"}}
        self.assertRequest(url, json=payload, status_code=410)
        payload = {"org_units": {"show_location": "False"}}
        self.assertRequest(url, json=payload, status_code=410)

        service_url = f"/service/ou/{uuid}/"
        response = self.assertRequest(service_url)
        user_settings = response["user_settings"]["orgunit"]
        assert user_settings["show_user_key"]
        assert user_settings["show_location"]


class AsyncTestNavLink(tests.cases.AsyncTestCase):
    """
    Test the retrieval of "nav links" via the "/service/navlinks" endpoint
    """

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.url = "/service/navlinks"

    async def test_empty_list(self):
        empty_list = await self.assertRequest(self.url)
        self.assertSequenceEqual(empty_list, [{}])

    async def test_populated_list(self):
        href = "http://google.com"
        text = "Google"

        with util.override_config(Settings(navlinks=[NavLink(href=href, text=text)])):
            populated_list = await self.assertRequest(self.url)
        assert len(populated_list) == 1
        assert populated_list[0]["href"] == href
        assert populated_list[0]["text"] == text
