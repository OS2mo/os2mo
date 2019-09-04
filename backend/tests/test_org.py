#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import util
from mora.service import org


class Tests(util.LoRATestCase):
    maxDiff = None

    def setUp(self):
        super().setUp()
        org.ConfiguredOrganisation.valid = False  # force validation each test
        self._get_valid_organisations = org.get_valid_organisations

    def tearDown(self):
        super().tearDown()
        org.get_valid_organisations = self._get_valid_organisations
        org.ConfiguredOrganisation.valid = False  # force validation each test

    def test_no_orgs_in_mo(self):
        self.load_sample_structures()
        org.get_valid_organisations = lambda: []
        r = self.request('/service/o/')
        self.assertEqual({
            'error': True,
            'error_key': 'E_ORG_UNCONFIGURED',
            'status': 400,
            'description': 'Organisation has not been configured'
        }, r.json)

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
