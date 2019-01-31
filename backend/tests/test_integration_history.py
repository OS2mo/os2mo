#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from flask import json

from . import util


class EmployeeHistoryTest(util.LoRATestCase):

    def test_invalid_employee_history(self):
        userid = "00000000-0000-0000-0000-000000000000"

        # Assert
        self.assertRequestResponse(
            '/service/e/{}/history/'.format(userid),
            {
                'description': 'User not found.',
                'error': True,
                'error_key': 'E_USER_NOT_FOUND',
                'status': 404,
                'employee_uuid': userid,
            },
            status_code=404,
        )

    @unittest.expectedFailure
    def test_employee_history(self):
        # Create and edit a bunch of stuff, followed by a terminate
        # Arrange
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        # Act
        self.assertRequest(
            '/service/details/edit',
            json=[
                {
                    "type": "engagement",
                    "uuid": 'd000591f-8705-4324-897a-075e3623f37b',
                    "data": {
                        "person": {"uuid": userid},
                        "validity": {
                            "from": "2018-04-01",
                        }
                    },
                },
                {
                    "type": "association",
                    "uuid": 'c2153d5d-4a2b-492d-a18c-c498f7bb6221',
                    "data": {
                        "person": {"uuid": userid},
                        "validity": {
                            "from": "2018-04-01",
                        }
                    },
                },
                {
                    "type": "role",
                    "uuid": '1b20d0b9-96a0-42a6-b196-293bb86e62e8',
                    "data": {
                        "person": {"uuid": userid},
                        "validity": {
                            "from": "2018-04-01",
                        }
                    },
                },
                {
                    "type": "leave",
                    "uuid": 'b807628c-030c-4f5f-a438-de41c1f26ba5',
                    "data": {
                        "person": {"uuid": userid},
                        "validity": {
                            "from": "2018-04-01",
                        }
                    },
                },
                {
                    "type": "manager",
                    "uuid": '05609702-977f-4869-9fb4-50ad74c6999a',
                    "data": {
                        "person": {"uuid": userid},
                        "validity": {
                            "from": "2018-04-01",
                        }
                    },
                },
            ])

        self.assertRequest(
            '/service/details/create',
            json=[
                {
                    "type": "engagement",
                    "person": {
                        "uuid": userid},
                    "org_unit": {
                        'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                    "job_function": {
                        'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                    "engagement_type": {
                        'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                    "validity": {
                        "from": "2017-12-01",
                        "to": "2017-12-01",
                    }
                },
                {
                    "type": "association",
                    "person": {
                        "uuid": userid},
                    "org_unit": {
                        'uuid': "04c78fc2-72d2-4d02-b55f-807af19eac48"},
                    "job_function": {
                        'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                    "association_type": {
                        'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                    },
                    "validity": {
                        "from": "2017-12-01",
                        "to": "2017-12-01",
                    },
                },
                {
                    "type": "role",
                    "person": {
                        "uuid": userid},
                    "org_unit": {
                        'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                    "role_type": {
                        'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                    "validity": {
                        "from": "2017-12-01",
                        "to": "2017-12-01",
                    },
                },
                {
                    "type": "leave",
                    "person": {
                        "uuid": userid},
                    "leave_type": {
                        'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                    "validity": {
                        "from": "2017-12-01",
                        "to": "2017-12-01",
                    },
                },
                {
                    "type": "manager",
                    "person": {
                        "uuid": userid},
                    "org_unit": {
                        'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                    "responsibility": [{
                        'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"}],
                    "manager_type": {
                        'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                    },
                    "manager_level": {
                        "uuid": "1edc778c-bf9b-4e7e-b287-9adecd6ee293"
                    },
                    "validity": {
                        "from": "2017-12-01",
                        "to": "2017-12-01",
                    },
                },
            ])

        self.assertRequestResponse(
            '/service/e/{}/terminate'.format(userid),
            userid,
            json={
                "validity": {
                    "to": "2017-12-01"
                }
            })

        expected_result = [
            {
                'action': 'Afsluttet',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Opret leder',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Opret orlov',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Opret rolle',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Opret tilknytning',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Opret engagement',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Rediger leder',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Rediger orlov',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Rediger rolle',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Rediger tilknytning',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': 'Rediger engagement',
                'life_cycle_code': 'Rettet',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            },
            {
                'action': None,
                'life_cycle_code': 'Importeret',
                'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'
            }
        ]

        # Assert
        r = self.request(
            '/service/e/{}/history/'.format(userid),
        )
        self.assert200(r)
        actual_result = json.loads(r.get_data())
        # 'From' and 'to' contain timestamps generated by the database,
        # and as such are unreliable in testing
        for obj in actual_result:
            del obj['from']
            del obj['to']

        self.assertEqual(expected_result, actual_result)


class OrgUnitHistoryTest(util.LoRATestCase):
    def test_invalid_org_unit_history(self):
        unitid = "00000000-0000-0000-0000-000000000000"

        # Assert
        self.assertRequestResponse(
            '/service/ou/{}/history/'.format(unitid),
            {
                'description': 'Org unit not found.',
                'error': True,
                'error_key': 'E_ORG_UNIT_NOT_FOUND',
                'org_unit_uuid': unitid,
                'status': 404,
            },
            status_code=404,
        )

    @unittest.expectedFailure
    def test_org_unit_history(self):
        # A create, some edits, followed by a termination
        # Arrange
        self.load_sample_structures()

        # Act
        r = self.request(
            '/service/ou/create',
            json={
                "name": "History test",
                "parent": {
                    'uuid': "2874e1dc-85e6-4269-823a-e1125484dfd3"
                },
                "org_unit_type": {
                    'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                },
                "validity": {
                    "from": "2016-02-04",
                    "to": "2017-10-21",
                }
            }
        )
        self.assert200(r)
        unitid = json.loads(r.get_data())

        self.assertRequest(
            '/service/details/edit',
            json={
                "type": "org_unit",
                "data": {
                    "name": "History test II",
                    "org_unit": {"uuid": unitid},
                    "validity": {
                        "from": "2016-01-05",
                    }
                }
            }
        )

        self.assertRequest(
            '/service/details/edit',
            json={
                "type": "org_unit",
                "data": {
                    "name": "History test III",
                    "org_unit": {"uuid": unitid},
                    "validity": {
                        "from": "2016-01-12",
                    }
                }
            }
        )

        self.assertRequestResponse(
            '/service/ou/{}/create'.format(unitid),
            unitid,
            json=[{
                "type": "manager",
                "job_function": {
                    'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                }
            }],
        )

        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(unitid),
            unitid,
            json={
                "validity": {
                    "to": "2017-12-01"
                }
            })

        expected_result = [
            {'action': 'Afslut enhed',
             'life_cycle_code': 'Rettet',
             'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'},
            {'action': 'Opret leder',
             'life_cycle_code': 'Rettet',
             'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'},
            {'action': 'Rediger organisationsenhed',
             'life_cycle_code': 'Rettet',
             'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'},
            {'action': 'Rediger organisationsenhed',
             'life_cycle_code': 'Rettet',
             'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'},
            {'action': 'Oprettet i MO',
             'life_cycle_code': 'Opstaaet',
             'user_ref': '42c432e8-9c4a-11e6-9f62-873cf34a735f'}
        ]

        # Assert
        r = self.request(
            '/service/ou/{}/history/'.format(unitid),
        )
        actual_result = json.loads(r.get_data())
        # 'From' and 'to' contain timestamps generated by the database,
        # and as such are unreliable in testing
        for obj in actual_result:
            del obj['from']
            del obj['to']

        self.assertEqual(expected_result, actual_result)
