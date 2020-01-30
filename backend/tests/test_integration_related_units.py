# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import freezegun

from mora import util as mora_util
from . import util

HUM = {
    'org_unit': [
        {
            'name': 'Humanistisk fakultet',
            'user_key': 'hum',
            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            'validity': {
                'from': '2016-01-01',
                'to': None,
            },
        },
        {
            'name': 'Overordnet Enhed',
            'user_key': 'root',
            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            'validity': {
                'from': '2016-01-01',
                'to': None,
            },
        },
    ],
    'uuid': '5c68402c-2a8d-4776-9237-16349fc72648',
    'user_key': 'rod <-> hum',
    'validity': {
        'from': '2016-06-01',
        'to': None,
    },
}

HIST = {
    "org_unit": [
        {
            "name": "Historisk Institut",
            "user_key": "hist",
            "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa",
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31",
            },
        },
        {
            "name": "Overordnet Enhed",
            "user_key": "root",
            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "validity": {
                "from": "2016-01-01",
                "to": None,
            },
        },
    ],
    "uuid": "daa77a4d-6500-483d-b099-2c2eb7fa7a76",
    'user_key': 'rod <-> fil',
    "validity": {
        "from": "2017-01-01",
        "to": "2018-12-31",
    },
}


@freezegun.freeze_time('2017-06-01', tz_offset=2)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_reading(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/details/related_unit',
            [HUM, HIST],
            "Overodnet Enhed",
        )

        self.assertRequestResponse(
            '/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa'
            '/details/related_unit',
            [HIST],
            "Filosofisk Fakultet",
        )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/related_unit',
            [HUM],
            "Humaninistisk Fakultet",
        )

        self.assertRequestResponse(
            '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
            '/details/related_unit',
            [],
        )

        # should this be a 404?
        self.assertRequestResponse(
            '/service/ou/00000000-0000-0000-0000-000000000000'
            '/details/related_unit',
            [],
        )

    def test_validation(self):
        self.load_sample_structures()

        with self.subTest('past'):
            self.assertRequestResponse(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map',
                {
                    'description': 'Date range exceeds validity range '
                                   'of associated org unit.',
                    'error': True,
                    'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                    'org_unit_uuid': ['da77153e-30f3-4dc2-a611-ee912a28d8aa'],
                    'status': 400,
                },
                json={
                    'destination': [
                        'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    ],
                    'validity': {
                        'from': '2017-03-01',
                    },
                },
                status_code=400,
            )

        with self.subTest('outside'):
            self.assertRequestResponse(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map',
                {
                    'description': 'Date range exceeds validity range of '
                    'associated org unit.',
                    'error': True,
                    'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                    'org_unit_uuid': ['da77153e-30f3-4dc2-a611-ee912a28d8aa'],
                    'status': 400,
                },
                json={
                    'destination': [
                        'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    ],
                    'validity': {
                        'from': '2019-01-01',
                    },
                },
                status_code=400,
            )

        with self.subTest('across a change'):
            with freezegun.freeze_time('2016-03-01'):
                self.assertRequestResponse(
                    '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map',
                    {
                        'description': 'Date range exceeds validity range of '
                        'associated org unit.',
                        'error': True,
                        'error_key': 'V_DATE_OUTSIDE_ORG_UNIT_RANGE',
                        'org_unit_uuid': [
                            '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        ],
                        'status': 400,
                    },
                    json={
                        'destination': [
                            '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        ],
                        'validity': {
                            'from': '2017-06-01',
                        },
                    },
                    status_code=400,
                )

        with self.subTest('invalid origin'):
            self.assertRequestResponse(
                '/service/ou/00000000-0000-0000-0000-000000000000/map',
                {
                    'description': 'Org unit not found.',
                    'error': True,
                    'error_key': 'E_ORG_UNIT_NOT_FOUND',
                    'org_unit_uuid': ['00000000-0000-0000-0000-000000000000'],
                    'status': 404,
                },
                json={
                    'destination': [
                        '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    ],
                    'validity': {
                        'from': '2017-06-01',
                    },
                },
                status_code=404,
            )

        with self.subTest('invalid destination'):
            self.assertRequestResponse(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map',
                {
                    'description': 'Org unit not found.',
                    'error': True,
                    'error_key': 'E_ORG_UNIT_NOT_FOUND',
                    'org_unit_uuid': ['00000000-0000-0000-0000-000000000000'],
                    'status': 404,
                },
                json={
                    'destination': [
                        '00000000-0000-0000-0000-000000000000',
                    ],
                    'validity': {
                        'from': '2017-06-01',
                    },
                },
                status_code=404,
            )

    def test_writing(self):
        self.load_sample_structures()

        r = self.assertRequest(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/map',
            json={
                'destination': [
                    '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'b688513d-11f7-4efc-b679-ab082a2055d0',
                ],
                'validity': {
                    'from': '2017-06-01',
                },
            },
        )

        self.assertEqual(r.keys(),
                         {'added', 'deleted', 'unchanged'})
        self.assertEqual(r['deleted'],
                         ['daa77a4d-6500-483d-b099-2c2eb7fa7a76'])
        self.assertEqual(r['unchanged'],
                         ['9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'])
        functionid, = r['added']

        samf = {
            "org_unit": [
                {
                    "name": "Overordnet Enhed",
                    "user_key": "root",
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "validity": {
                        "from": "2016-01-01",
                        "to": None,
                    },
                },
                {
                    "name": "Samfundsvidenskabelige fakultet",
                    "user_key": "samf",
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "validity": {
                        "from": "2017-01-01",
                        "to": None,
                    },
                },
            ],
            "uuid": functionid,
            "user_key": "root <-> samf",
            "validity": {
                "from": "2017-06-01",
                "to": None,
            },
        }

        r = self.assertRequest(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/details/related_unit'
        )
        self.assertIn(samf, r)
        self.assertIn(HUM, r)

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/related_unit',
            [HUM],
            "Humaninistisk Fakultet",
        )

        self.assertRequestResponse(
            '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
            '/details/related_unit',
            [samf],
        )

        self.assertRequestResponse(
            '/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa'
            '/details/related_unit',
            [],
            "Historisk Institut",
        )

        self.assertRequestResponse(
            '/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa'
            '/details/related_unit',
            [],
        )

        with self.subTest('past'):
            hist = mora_util.set_obj_value(HIST, ('validity', 'to'),
                                           '2017-05-31')

            self.assertRequestResponse(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
                '/details/related_unit?validity=past',
                [hist],
                "Overordnet Enhed, past"
            )

            self.assertRequestResponse(
                '/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/details/related_unit?validity=past',
                [hist],
                "Historisk Institut, past",
            )

            self.assertRequestResponse(
                '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
                '/details/related_unit?validity=past',
                [],
                "Humaninistisk Fakultet, past",
            )

            self.assertRequestResponse(
                '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
                '/details/related_unit?validity=past',
                [],
            )
