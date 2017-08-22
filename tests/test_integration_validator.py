#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json

from mora import validator
from tests import util


class TestHelper(util.LoRATestCase):
    maxDiff = None

    # parent = samf, valid from 2017-01-01 to infinity
    ORG = '456362c4-0ee4-4e5e-a72c-751239745e62'
    PARENT = 'b688513d-11f7-4efc-b679-ab082a2055d0'

    def expire_org_unit(self, org_unit):
        # Expire the parent from 2018-01-01
        self.assertRequestResponse(
            '/o/%s/org-unit/%s?endDate=01-01-2018' % (self.ORG, org_unit),
            {
                'uuid': org_unit,
            },
            method='DELETE',
        )


class TestIntegrationCreateOrgUnitValidator(TestHelper):
    # Test validator._is_date_range_valid

    def test_should_return_true_when_interval_contained(self):
        """
        [------ super ------)
           [--- sub ---)
        """
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)

        startdate = '01-02-2017'
        enddate = '01-06-2017'

        self.assertTrue(
            validator._is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_return_true_when_interval_contained2(self):
        """
        [------ super ------)
        [------ sub ---)
        """
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)

        startdate = '01-01-2017'
        enddate = '01-06-2017'

        self.assertTrue(
            validator._is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_return_true_when_interval_contained3(self):
        """
        [------ super ------)
          [------ sub ------)
        """
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)

        startdate = '01-02-2017'
        enddate = '01-01-2018'

        self.assertTrue(
            validator._is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_false_true_when_interval_not_contained1(self):
        """
          [---- super ------)
        [------ sub ---)
        """
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)

        startdate = '01-01-2016'
        enddate = '01-06-2017'

        self.assertFalse(
            validator._is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_return_false_when_interval_not_contained2(self):
        """
        [------ super ------)
          [---- sub -----------)
        """
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)

        startdate = '01-02-2017'
        enddate = '01-06-2019'

        self.assertFalse(
            validator._is_date_range_valid(self.PARENT, startdate, enddate))

    def test_should_return_false_when_interval_not_contained3(self):
        """
                                   [------ super ------)
        [---- sub -----------)
        """
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)

        startdate = '01-02-2010'
        enddate = '01-06-2015'

        self.assertFalse(
            validator._is_date_range_valid(self.PARENT, startdate, enddate))

    # Test validator.is_create_org_unit_request_valid

    def test_should_create_org_unit_when_interval_contained(self):
        self.load_sample_structures()

        frontend_req = {
            "user-key": "NULL", "name": "AAA",
            "valid-from": "01-02-2017",
            "org": self.ORG,
            "parent": self.PARENT,
            "type": {
                "name": "Afdeling 003",
                "userKey": "Afdeling003",
                "uuid": "0034fa1f-b1ef-4764-8505-c5b9ca43aaa9"
            },
            "locations": [
                {
                    "name": "pil1",
                    "primaer": True,
                    "location": {
                        "UUID_EnhedsAdresse": "0a3f50c3-df6f-32b8-"
                                              "e044-0003ba298018",
                        "postdistrikt": "Risskov",
                        "postnr": "8240",
                        "vejnavn": "Pilevej 3, 8240 Risskov"
                    },
                    "contact-channels": [
                        {
                            "contact-info": "12345678",
                            "visibility": {
                                "name": "Må vises eksternt",
                                "user-key": "external",
                                "uuid": "external"
                            },
                            "type": {
                                "name": "Phone Number",
                                "prefix": "urn:magenta.dk:telefon:",
                                "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
                            }
                        }
                    ]
                }
            ]
        }

        self.assertTrue(
            validator.is_create_org_unit_request_valid(frontend_req))

    def test_should_not_create_org_unit_when_not_interval_contained1(self):
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)

        frontend_req = {
            "user-key": "NULL", "name": "AAA",
            "valid-from": "01-02-2017",
            "valid-to": "01-06-2020",
            "org": self.ORG,
            "parent": self.PARENT,
            "type": {
                "name": "Afdeling 003",
                "userKey": "Afdeling003",
                "uuid": "0034fa1f-b1ef-4764-8505-c5b9ca43aaa9"
            },
            "locations": [
                {
                    "name": "pil1",
                    "primaer": True,
                    "location": {
                        "UUID_EnhedsAdresse": "0a3f50c3-df6f-32b8-"
                                              "e044-0003ba298018",
                        "postdistrikt": "Risskov",
                        "postnr": "8240",
                        "vejnavn": "Pilevej 3, 8240 Risskov"
                    },
                    "contact-channels": [
                        {
                            "contact-info": "12345678",
                            "visibility": {
                                "name": "Må vises eksternt",
                                "user-key": "external",
                                "uuid": "external"
                            },
                            "type": {
                                "name": "Phone Number",
                                "prefix": "urn:magenta.dk:telefon:",
                                "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
                            }
                        }
                    ]
                }
            ]
        }

        self.assertFalse(
            validator.is_create_org_unit_request_valid(frontend_req))

    def test_should_not_create_org_unit_when_not_interval_contained2(self):
        self.load_sample_structures()

        frontend_req = {
            "user-key": "NULL", "name": "AAA",
            "valid-from": "01-02-2000",
            "org": self.ORG,
            "parent": self.PARENT,
            "type": {
                "name": "Afdeling 003",
                "userKey": "Afdeling003",
                "uuid": "0034fa1f-b1ef-4764-8505-c5b9ca43aaa9"
            },
            "locations": [
                {
                    "name": "pil1",
                    "primaer": True,
                    "location": {
                        "UUID_EnhedsAdresse": "0a3f50c3-df6f-32b8-"
                                              "e044-0003ba298018",
                        "postdistrikt": "Risskov",
                        "postnr": "8240",
                        "vejnavn": "Pilevej 3, 8240 Risskov"
                    },
                    "contact-channels": [
                        {
                            "contact-info": "12345678",
                            "visibility": {
                                "name": "Må vises eksternt",
                                "user-key": "external",
                                "uuid": "external"
                            },
                            "type": {
                                "name": "Phone Number",
                                "prefix": "urn:magenta.dk:telefon:",
                                "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
                            }
                        }
                    ]
                }
            ]
        }

        self.assertFalse(
            validator.is_create_org_unit_request_valid(frontend_req))

    def test_should_return_status_400_when_date_range_invalid(self):
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)

        payload = {
            "user-key": "NULL",
            "name": "NyEnhed",
            "valid-from": "01-02-2020",
            "org": self.ORG,
            "parent": self.PARENT,
            "type": {
                "name": "Afdeling",
                "userKey": "Afdeling",
                "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
            },
            "locations": [
                {
                    "name": "lnavn",
                    "primaer": True,
                    "location": {
                        "UUID_EnhedsAdresse":
                            "98001816-a7cc-4115-a9e6-2c5c06c79e5d",
                        "postdistrikt": "Risskov",
                        "postnr": "8240",
                        "vejnavn": "Pilevej 2, 8240 Risskov"
                    },
                    "contact-channels": [
                        {
                            "contact-info": "12345678",
                            "visibility": {
                                "name": "flaf",
                                "user-key": "blyf",
                                "uuid": "00000000-0000-0000-0000-000000000000"
                            },
                            "type": {
                                "name": "Phone Number",
                                "prefix": "urn:magenta.dk:telefon:",
                                "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
                            }
                        }
                    ]
                }
            ]
        }
        r = self.client.post('/o/%s/org-unit' % self.ORG,
                             data=json.dumps(payload),
                             content_type='application/json')
        self.assertEqual(400, r.status_code)


class TestIntegrationMoveOrgUnitValidator(TestHelper):
    UNIT_TO_MOVE = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'  # Hum

    def test_cannot_move_unit_to_own_subtree(self):
        self.load_sample_structures()

        candidate_parent = '04c78fc2-72d2-4d02-b55f-807af19eac48'  # Frem

        frontend_req = {
            'moveDate': '01-02-2017',
            'newParentOrgUnitUUID': candidate_parent
        }

        self.assertFalse(
            validator.is_candidate_parent_valid(self.UNIT_TO_MOVE,
                                                frontend_req))

    def test_should_allow_move_unit_to_valid_orgtree_location(self):
        self.load_sample_structures()

        candidate_parent = 'b688513d-11f7-4efc-b679-ab082a2055d0'  # Samf

        frontend_req = {
            'moveDate': '01-02-2017',
            'newParentOrgUnitUUID': candidate_parent
        }

        self.assertTrue(
            validator.is_candidate_parent_valid(self.UNIT_TO_MOVE,
                                                frontend_req))

    def test_should_not_move_root_org_unit(self):
        self.load_sample_structures()

        root_org_unit = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        candidate_parent = 'b688513d-11f7-4efc-b679-ab082a2055d0'  # Samf

        frontend_req = {
            'moveDate': '01-02-2017',
            'newParentOrgUnitUUID': candidate_parent
        }

        self.assertFalse(
            validator.is_candidate_parent_valid(root_org_unit, frontend_req))

    def test_should_not_move_org_unit_to_child(self):
        self.load_sample_structures()

        candidate_parent = '85715fc7-925d-401b-822d-467eb4b163b6'  # Fil

        frontend_req = {
            'moveDate': '01-02-2017',
            'newParentOrgUnitUUID': candidate_parent
        }

        self.assertFalse(
            validator.is_candidate_parent_valid(self.UNIT_TO_MOVE,
                                                frontend_req))

    def test_should_not_move_org_unit_to_itself(self):
        self.load_sample_structures()

        frontend_req = {
            'moveDate': '01-02-2017',
            'newParentOrgUnitUUID': self.UNIT_TO_MOVE
        }

        self.assertFalse(
            validator.is_candidate_parent_valid(self.UNIT_TO_MOVE,
                                                frontend_req))

    def test_should_return_false_when_candicate_parent_is_inactive(self):
        self.load_sample_structures()
        self.expire_org_unit(self.PARENT)  # Expire the candidate parent unit

        frontend_req = {
            'moveDate': '01-02-2020',
            'newParentOrgUnitUUID': self.PARENT
        }

        self.assertFalse(validator.is_candidate_parent_valid(self.UNIT_TO_MOVE,
                                                             frontend_req))

    def test_should_return_status_400_when_move_invalid(self):
        self.load_sample_structures()

        candidate_parent = '04c78fc2-72d2-4d02-b55f-807af19eac48'  # Frem

        frontend_req = {
            'moveDate': '01-02-2017',
            'newParentOrgUnitUUID': candidate_parent
        }

        r = self.client.post(
            '/o/%s/org-unit/%s/actions/move' % (self.ORG, self.UNIT_TO_MOVE),
            data=json.dumps(frontend_req),
            content_type='application/json')

        self.assertEqual(400, r.status_code)


class TestInactivateOrgUnitValidation(util.LoRATestCase):
    maxDiff = None
    ORG = '456362c4-0ee4-4e5e-a72c-751239745e62'
    SAMF_UNIT = 'b688513d-11f7-4efc-b679-ab082a2055d0'
    HIST_UNIT = 'da77153e-30f3-4dc2-a611-ee912a28d8aa'

    def test_should_not_allow_end_date_2000_01_01(self):
        self.load_sample_structures()
        self.assertFalse(
            validator.is_inactivation_date_valid(self.SAMF_UNIT, '01-01-2000'))

    def test_should_allow_end_2019_01_01(self):
        self.load_sample_structures()
        self.assertTrue(
            validator.is_inactivation_date_valid(self.SAMF_UNIT, '01-01-2019'))

    def test_should_not_allow_end_date_2018_when_subunit_still_active(self):
        self.load_sample_structures()
        self.assertFalse(
            validator.is_inactivation_date_valid(self.HIST_UNIT, '01-01-2018')
        )

    def test_should_allow_end_date_2020_when_subunit_still_active(self):
        self.load_sample_structures()
        self.assertTrue(
            validator.is_inactivation_date_valid(self.HIST_UNIT, '01-01-2020')
        )

    def test_should_not_allow_end_date_2018_when_subunits_still_active(self):
        self.load_sample_structures()
        self.assertFalse(
            validator.is_inactivation_date_valid(
                '2874e1dc-85e6-4269-823a-e1125484dfd3', '01-01-2018')
        )

    def test_should_return_status_400_when_enddate_invalid(self):
        self.load_sample_structures()

        r = self.client.delete(
            '/o/%s/org-unit/%s?endDate=01-01-2018' %
            (self.ORG, self.HIST_UNIT))
        self.assertEqual(400, r.status_code)
