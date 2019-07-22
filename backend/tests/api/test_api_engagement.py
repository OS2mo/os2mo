#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from mock import patch

from tests import util


class Tests(util.LoRATestCase):

    def test_get_all(self):
        self.load_sample_structures()
        self.assertRequestResponse(
            '/service/api/engagement?only_primary_uuid',
            [{
                'engagement_type': {
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                'fraction': None,
                'job_function': {
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
                },
                'org_unit': {'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'},
                'person': {'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'},
                'primary': None,
                'user_key': 'bvn',
                'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
                'validity': {'from': '2017-01-01', 'to': None}
            }]
        )

    def test_get(self):
        self.load_sample_structures()
        self.assertRequestResponse(
            '/service/api/engagement/d000591f-8705-4324-897a-075e3623f37b'
            '?only_primary_uuid',
            [{
                'engagement_type': {
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'
                },
                'fraction': None,
                'job_function': {
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
                },
                'org_unit': {
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                },
                'primary': None,
                'user_key': 'bvn',
                'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
                'validity': {'from': '2017-01-01', 'to': None}
            }],
            method='GET',
        )

    def test_patch(self):
        self.load_sample_structures()
        obj_uuid = 'd000591f-8705-4324-897a-075e3623f37b'
        self.assertRequestResponse(
            '/service/api/engagement/{}?force=1'.format(obj_uuid),
            obj_uuid,
            json={
                'user_key': 'WHATEVER',
                'validity': {'from': '2017-01-01', 'to': None}
            },
            method='PATCH',
        )

        expected_bvn = 'WHATEVER'
        actual = self.assertRequest(
            '/service/api/engagement/{}?only_primary_uuid'.format(obj_uuid))[
            -1]

        self.assertEqual(expected_bvn, actual.get('user_key'))

    def test_post(self):
        self.load_sample_structures()

        obj_uuid = self.assertRequest(
            '/service/api/engagement?force=1',
            json={
                "person": {'uuid': "6ee24785-ee9a-4502-81c2-7697009c9053"},
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {
                    'uuid': "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "engagement_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                "user_key": "9876",
                "fraction": 99,
                "validity": {
                    "from": "2010-12-12",
                    "to": "2022-11-11",
                }
            }
        )

        actual = self.assertRequest(
            '/service/api/engagement/{}'.format(obj_uuid))

        self.assertEqual(1, len(actual), 'Exactly one object should exist')

    def test_put(self):
        self.load_sample_structures()

        obj_uuid = '9ad39a2a-8af4-41bd-87da-8f4fdcc2b490'

        obj_uuid = self.assertRequest(
            '/service/api/engagement/{}?force=1'.format(obj_uuid),
            json={
                "person": {'uuid': "6ee24785-ee9a-4502-81c2-7697009c9053"},
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {
                    'uuid': "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "engagement_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                "user_key": "4444",
                "fraction": 44,
                "validity": {
                    "from": "2010-12-12",
                    "to": "2022-11-11",
                }
            },
            method='PUT'
        )

        actual = self.assertRequest(
            '/service/api/engagement/{}'.format(obj_uuid))

        self.assertEqual(1, len(actual), 'Exactly one object should exist')
