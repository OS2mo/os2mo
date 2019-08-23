#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import util
from mora.service import org


class TestConfig(util.LoRATestCase):
    maxDiff = None

    def setUp(self):
        super().setUp()
        org.ConfiguredOrganisation.valid = False  # force validation each test
        self._get_valid_organisations = org.get_valid_organisations

    def tearDown(self):
        super().tearDown()
        org.get_valid_organisations = self._get_valid_organisations
        org.ConfiguredOrganisation.valid = False  # force validation each test

    def test_missing_conf_values_in_prod(self):
        "error if not configured in production"
        class AppProd():
            env = "production"
            config = {}
        with self.assertRaises(KeyError):
            org.check_config(AppProd)

    def test_more_than_one_org_in_mo(self):
        self.load_sample_structures()
        org.get_valid_organisations = lambda: [{}, {}]
        r = self.request('/service/o/')
        self.assertEqual({
            'error': True,
            'count': 2,
            'error_key': 'E_ORG_TOO_MANY',
            'status': 400,
            'description': 'Too many organisations in lora, max one allowed'
        }, r.json)


class Tests(util.LoRATestCase):
    maxDiff = None

    def setUp(self):
        super().setUp()
        org.ConfiguredOrganisation.valid = False  # force validation each test

    def tearDown(self):
        super().tearDown()
        org.ConfiguredOrganisation.valid = False  # force validation each test

    @util.override_config(
        ORGANISATION_NAME='Aarhus Universitet',
        ORGANISATION_USER_KEY='AU',
        ORGANISATION_UUID='456362c4-0ee4-4e5e-a72c-751239745e62',
    )
    def test_org_same_as_config(self):
        self.load_sample_structures()
        r = self.request('/service/o/')
        self.assertEqual([{
            "uuid": '456362c4-0ee4-4e5e-a72c-751239745e62',
            "user_key": 'AU',
            "name": 'Aarhus Universitet',
        }], r.json)

    @util.override_config(
        ORGANISATION_NAME='Universitet',
        ORGANISATION_USER_KEY='UU',
        ORGANISATION_UUID='456362c4-0ee4-4e5e-a72c-751239745e62',
    )
    def test_org_different_from_config(self):
        self.load_sample_structures()
        r = self.request('/service/o/')
        self.assertEqual({
            'error': True,
            'ORGANISATION_NAME': 'Universitet',
            'ORGANISATION_USER_KEY': 'UU',
            'error_key': 'E_ORG_CONFIG_BAD',
            'status': 400,
            'description': 'Organisation configuration differs from database'
        }, r.json)
