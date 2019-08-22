#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import util
from mora.service import org


class AppProd():
    env = "production"
    config = {}


class TestConfig(util.TestCase):

    def setUp(self):
        self._get_valid_organisations = org.get_valid_organisations

    def tearDown(self):
        org.get_valid_organisations = self._get_valid_organisations

    def test_org_same_as_config(self):
        "succed if OS2MO_ORGANISATION_UUID is the same as the one in lora"
        with util.override_config(
            OS2MO_ORGANISATION_UUID="c5395419-4c76-417f-9939-5a4bf81648d8"
        ):
            org.check_config(self.app)

    def test_org_different_from_config(self):
        "raise ValueError if OS2MO_ORGANISATION_UUID is different from loras"
        with util.override_config(
            OS2MO_ORGANISATION_UUID="1234"
        ):
            with self.assertRaises(ValueError):
                org.check_config(self.app)

    def test_more_than_one_org_in_mo(self):
        "only one organisation allowed in lora - IndexError"
        org.get_valid_organisations = lambda: [{}, {}]
        with self.assertRaises(IndexError):
            org.check_config(self.app)

    def test_missing_conf_values_in_prod(self):
        "error if not configured in production"
        with self.assertRaises(KeyError):
            org.check_config(AppProd)

    def test_inferred_org_in_mo(self):
        "succeed if only one org in mo - config is inferred"
        org.check_config(self.app)
        self.assertEqual(
            "c5395419-4c76-417f-9939-5a4bf81648d8",
            self.app.config["OS2MO_ORGANISATION_UUID"]
        )
