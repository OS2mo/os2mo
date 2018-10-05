#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun
import notsouid

from mora import lora
from . import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_employee(self):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        mock_uuid = "b6c268d2-4671-4609-8441-6029077d8efc"

        payload = {
            "name": "Torkild Testperson",
            "cpr_no": "0101501234",
            "org": {
                'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
            }
        }

        with notsouid.freeze_uuid(mock_uuid):
            r = self.request('/service/e/create', json=payload)
        userid = r.json

        expected = {
            "livscykluskode": "Importeret",
            "note": "Oprettet i MO",
            "attributter": {
                "brugeregenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "1950-01-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "brugernavn": "Torkild Testperson"
                    }
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "1950-01-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedepersoner": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "1950-01-01 00:00:00+01"
                        },
                        "urn": "urn:dk:cpr:person:0101501234"
                    }
                ],
            },
            "tilstande": {
                "brugergyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "1950-01-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
        }

        actual = c.bruger.get(userid)

        self.assertRegistrationsEqual(expected, actual)

        self.assertRequestResponse(
            '/service/e/{}/'.format(userid),
            {
                'name': 'Torkild Testperson',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'user_key': mock_uuid,
                'cpr_no': '0101501234',
                'uuid': userid,
            },
        )

    def test_create_employee_like_import(self):
        '''Test creating a user that has no CPR number, but does have a
        user_key and a given UUID.

        '''
        self.load_sample_structures()

        userid = "ef78f929-2eb4-4d9e-8891-f9e8dcb47533"

        self.assertRequestResponse(
            '/service/e/create',
            userid,
            json={
                'name': 'Teodor Testfætter',
                'user_key': 'testfætter',
                'org': {
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                },
                'uuid': userid,
            },
        )

        self.assertRequestResponse(
            '/service/e/{}/'.format(userid),
            {
                'name': 'Teodor Testfætter',
                'user_key': 'testfætter',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'uuid': userid,
            },
        )

    def test_create_employee_fails_on_empty_payload(self):
        self.load_sample_structures()

        payload = {}

        self.assertRequestResponse(
            '/service/e/create',
            {
                'description': 'Missing name',
                'error': True,
                'error_key': 'V_MISSING_REQUIRED_VALUE',
                'key': 'name',
                'obj': {},
                'status': 400,
            },
            json=payload,
            status_code=400,
        )

    def test_create_employee_fails_on_invalid_cpr(self):
        payload = {
            "name": "Torkild Testperson",
            "cpr_no": "1",
            "org": {
                'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
            }
        }

        self.assertRequestResponse(
            '/service/e/create',
            {
                'cpr': '1',
                'description': 'Not a valid CPR number.',
                'error': True,
                'error_key': 'V_CPR_NOT_VALID',
                'status': 400,
            },
            json=payload,
            status_code=400,
        )

    def test_create_employee_existing_cpr_existing_org(self):
        self.load_sample_structures()

        payload = {
            "name": "Torkild Testperson",
            "cpr_no": "0906340000",
            "org": {
                'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
            }
        }

        expected = {
            'cpr': '0906340000',
            'description': 'Person with CPR number already exists.',
            'error': True,
            'error_key': 'V_EXISTING_CPR',
            'status': 409
        }

        self.assertRequestResponse(
            '/service/e/create',
            expected,
            json=payload,
            status_code=409,
        )

    def test_create_employee_existing_cpr_new_org(self):
        """
        Should be able to create employee with same CPR no,
        but in different organisation
        """
        self.load_sample_structures()

        payload = {
            "name": "Torkild Testperson",
            "cpr_no": "0906340000",
            "org": {
                'uuid': "3dcb1072-482e-491e-a8ad-647991d0bfcf"
            }
        }

        uuid = self.request('/service/e/create', json=payload).json

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        self.assertTrue(c.bruger.get(uuid))

    def test_create_employee_with_details(self):
        """Test creating an employee with added details"""
        self.load_sample_structures()

        employee_uuid = "f7bcc7b1-381a-4f0e-a3f5-48a7b6eedf1c"

        payload = {
            "name": "Torkild Testperson",
            "cpr_no": "0101501234",
            "org": {
                'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
            },
            "details": [
                {
                    "type": "engagement",
                    "org_unit": {
                        'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    },
                    "job_function": {
                        'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    },
                    "engagement_type": {
                        'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                    },
                    "validity": {
                        "from": "2016-12-01",
                        "to": None,
                    }
                }
            ],
            "uuid": employee_uuid
        }

        mock_uuid = "b6c268d2-4671-4609-8441-6029077d8efc"
        with notsouid.freeze_uuid(mock_uuid):
            self.request('/service/e/create', json=payload)

        self.assertRequestResponse(
            '/service/e/{}/'.format(employee_uuid),
            {
                'name': 'Torkild Testperson',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'user_key': mock_uuid,
                'cpr_no': '0101501234',
                'uuid': employee_uuid,
            },
        )

        r = self.request('/service/e/{}/details/engagement'.format(
            employee_uuid))
        self.assertEqual(1, len(r.json), 'One engagement should exist')

    def test_create_employee_with_details_fails_atomically(self):
        """Ensure that we only save data when everything validates correctly"""
        self.load_sample_structures()

        employee_uuid = "d2e1b69e-def1-41b1-b652-e704af02591c"

        payload_broken_engagement = {
            "name": "Torkild Testperson",
            "cpr_no": "0101501234",
            "org": {
                'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
            },
            "details": [
                {
                    "type": "engagement",
                    "org_unit": {
                        'uuid': "9d07123e-47ac-4a9a-"
                                "88c8-da82e3a4bc9e"
                    },
                    "job_function": {
                        'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    },
                    "engagement_type": {
                        'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                    },
                    "validity": {
                        "from": "1960-12-01",
                        "to": "2017-12-01",
                    }
                }
            ],
            "uuid": employee_uuid
        }

        self.assertRequestResponse(
            '/service/e/create',
            {
                'description': 'Date range exceeds validity '
                               'range of associated org unit.',
                'error': True,
                'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                'org_unit_uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                'status': 400,
                'valid_from': '2016-01-01',
                'valid_to': None,
                'wanted_valid_from': '1960-12-01',
                'wanted_valid_to': '2017-12-01'
            },
            status_code=400,
            json=payload_broken_engagement,
        )

        payload_broken_employee = {
            "name": "Torkild Testperson",
            "cpr_no": "0101174234",
            "org": {
                'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
            },
            "details": [
                {
                    "type": "engagement",
                    "org_unit": {
                        'uuid': "9d07123e-47ac-4a9a-"
                                "88c8-da82e3a4bc9e"
                    },
                    "job_function": {
                        'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    },
                    "engagement_type": {
                        'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                    },
                    "validity": {
                        "from": "2016-12-01",
                        "to": "2017-12-01",
                    }
                }
            ],
            "uuid": employee_uuid
        }

        self.assertRequestResponse(
            '/service/e/create',
            {
                'description': 'Date range exceeds validity '
                               'range of associated employee.',
                'error': True,
                'error_key': 'V_DATE_OUTSIDE_EMPL_RANGE',
                'status': 400,
                'valid_from': '2017-01-01',
                'valid_to': '9999-12-31',
                'wanted_valid_from': '2016-12-01',
                'wanted_valid_to': '2017-12-02'
            },
            status_code=400,
            json=payload_broken_employee,
        )

        # Assert that nothing has been written

        self.assertRequestResponse(
            '/service/e/{}/'.format(employee_uuid),
            {
                'status': 404,
                'error': True,
                'description': 'User not found.',
                'error_key': 'E_USER_NOT_FOUND'
            },
            status_code=404,
        )

        engagement = self.request('/service/e/{}/details/engagement'.format(
            employee_uuid)).json
        self.assertEqual([], engagement,
                         'No engagement should have been created')

    def test_cpr_lookup_prod_mode_false(self):
        # Arrange
        cpr = "0101501234"

        expected = {
            'name': 'Merle Mortensen',
            'cpr_no': cpr
        }

        # Act
        with util.override_settings(PROD_MODE=False):
            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q={}'.format(cpr),
                expected)

    def test_cpr_lookup_raises_on_wrong_length(self):
        # Arrange

        # Act
        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=1234/',
            {
                'cpr': '1234/',
                'description': 'Not a valid CPR number.',
                'error': True,
                'error_key': 'V_CPR_NOT_VALID',
                'status': 400,
            },
            status_code=400,
        )
        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=1234',
            {
                'cpr': '1234',
                'description': 'Not a valid CPR number.',
                'error': True,
                'error_key': 'V_CPR_NOT_VALID',
                'status': 400,
            },
            status_code=400,
        )
        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=1234567890123',
            {
                'cpr': '1234567890123',
                'description': 'Not a valid CPR number.',
                'error': True,
                'error_key': 'V_CPR_NOT_VALID',
                'status': 400,
            },
            status_code=400,
        )
