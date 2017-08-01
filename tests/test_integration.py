#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json

import freezegun
import requests

from . import util
from mora import lora


class IntegrationTests(util.LoRATestCase):
    maxDiff = None

    def test_sanity(self):
        r = requests.get(lora.LORA_URL)
        self.assertTrue(r.ok)
        self.assertEqual(r.json().keys(), {'site-map'})

    def test_empty(self):
        r = requests.get(lora.LORA_URL)
        self.assertTrue(r.ok)
        self.assertEqual(r.json().keys(), {'site-map'})

    def test_list_classes(self):
        self.load_sample_structures()

        self.assertEqual(
            self.client.get('/org-unit/type').json,
            [
                {
                    'name': 'Afdeling',
                    'userKey': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                {
                    'name': 'Fakultet',
                    'userKey': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                {
                    'name': 'Institut',
                    'userKey': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                }
            ],
        )

    def test_organisation(self):
        'Test getting the organisation'

        self.assertRequestResponse('/o/', [])

        r = self.client.get('/o/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, [])

        self.load_sample_structures()

        self.assertRequestResponse('/o/', [
            {
                'hierarchy': {
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'children': [],
                    'name': 'Overordnet Enhed',
                    'hasChildren': True,
                    'valid-to': 'infinity',
                    'valid-from': '01-01-2016',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'valid-to': 'infinity',
                'valid-from': '01-01-2016',
            },
        ])

    def test_organisation_empty(self):
        'Handle no organisations'
        self.assertRequestResponse('/o/', [])

    def test_hierarchies(self):
        'Test the full-hierarchy listing'

        # then inject an organisation and find it
        self.load_sample_structures()

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/full-hierarchy'
            '?treeType=treeType',
            {
                'hierarchy': {
                    'children': [
                        {
                            'children': [],
                            'hasChildren': True,
                            'name': 'Humanistisk fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'type': {'name': 'Institut'},
                            'user-key': 'hum',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        {
                            'children': [],
                            'hasChildren': False,
                            'name': 'Samfundsvidenskabelige fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'type': {'name': 'Fakultet'},
                            'user-key': 'samf',
                            'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                            'valid-from': '01-01-2017',
                            'valid-to': 'infinity'
                        },
                    ],
                    'hasChildren': True,
                    'name': 'Overordnet Enhed',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': None,
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'valid-from': '01-01-2016',
                    'type': {'name': 'Afdeling'},
                    'valid-to': 'infinity'},
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'valid-from': '01-01-2016',
                'valid-to': 'infinity',
            })

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/full-hierarchy',
            {
                'hierarchy': {
                    'children': [
                        {
                            'children': [],
                            'hasChildren': True,
                            'name': 'Humanistisk fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'user-key': 'hum',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                            'type': {'name': 'Institut'},
                        },
                        {
                            'children': [],
                            'hasChildren': False,
                            'name': 'Samfundsvidenskabelige fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'user-key': 'samf',
                            'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                            'valid-from': '01-01-2017',
                            'valid-to': 'infinity',
                            'type': {'name': 'Fakultet'},
                        },
                    ],
                    'hasChildren': True,
                    'name': 'Overordnet Enhed',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': None,
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'valid-from': '01-01-2016',
                    'type': {'name': 'Afdeling'},
                    'valid-to': 'infinity'},
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'valid-from': '01-01-2016',
                'valid-to': 'infinity',
            })

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/full-hierarchy?'
            'treeType=specific&orgUnitId=2874e1dc-85e6-4269-823a-e1125484dfd3',
            [
                {
                    'children': [],
                    'hasChildren': True,
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'type': {'name': 'Institut'},
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
                {
                    'children': [],
                    'hasChildren': False,
                    'name': 'Samfundsvidenskabelige fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'type': {'name': 'Fakultet'},
                    'user-key': 'samf',
                    'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    'valid-from': '01-01-2017',
                    'valid-to': 'infinity',
                }
            ]
        )

    @freezegun.freeze_time('2017-06-01')
    def test_org_units(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e/',
            [
                {
                    'activeName': 'Humanistisk fakultet',
                    'hasChildren': True,
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': {
                        'activeName': 'Overordnet Enhed',
                        'hasChildren': True,
                        'name': 'Overordnet Enhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': None,
                        'parent-object': None,
                        'user-key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                        'type': {'name': 'Afdeling'},
                    },
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                    'type': {'name': 'Institut'},
                }
            ]
        )

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            '?query=Hum%',
            [
                {
                    'activeName': 'Humanistisk fakultet',
                    'hasChildren': True,
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': {
                        'activeName': 'Overordnet Enhed',
                        'hasChildren': True,
                        'name': 'Overordnet Enhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': None,
                        'parent-object': None,
                        'user-key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                        'type': {'name': 'Afdeling'},
                    },
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                    'type': {'name': 'Institut'},
                }
            ]
        )
        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            '?query=9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            [
                {
                    'activeName': 'Humanistisk fakultet',
                    'hasChildren': True,
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': {
                        'activeName': 'Overordnet Enhed',
                        'hasChildren': True,
                        'name': 'Overordnet Enhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': None,
                        'parent-object': None,
                        'user-key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                        'type': {'name': 'Afdeling'},
                    },
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                    'type': {'name': 'Institut'},
                }
            ]
        )

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
            '/org-unit/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/role-types/location/?validity=present',
            [
                {
                    'location': {
                        'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'user-key': '07515902___1_______',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'valid-from': '2014-05-05T19:07:48.577000',
                        'valid-to': 'infinity',
                    },
                    'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                    'org-unit': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'primaer': True,
                    'role-type': 'location',
                    'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
            ],
        )

        with self.subTest('invalid validity'):
            self.assert400(self.client.get(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/2874e1dc-85e6-4269-823a-e1125484dfd3/'
                '?validity=kaflaflibob',
            ))

    @freezegun.freeze_time('2017-06-01')
    def test_org_unit_temporality(self):
        self.load_sample_structures()

        with self.subTest('past'):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
                '04c78fc2-72d2-4d02-b55f-807af19eac48/?validity=past',
                [
                    {
                        'activeName': 'Afdeling for Fremtidshistorik',
                        'hasChildren': False,
                        'name': 'Afdeling for Fremtidshistorik',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': None,
                        'parent-object': None,
                        'type': {'name': ''},
                        'user-key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'valid-from': '01-01-2016',
                        'valid-to': '01-01-2018',
                    },
                ],
            )

        with self.subTest('present'):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
                '04c78fc2-72d2-4d02-b55f-807af19eac48/?validity=present',
                [
                    {
                        'activeName': 'Afdeling for Samtidshistorik',
                        'hasChildren': False,
                        'name': 'Afdeling for Samtidshistorik',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                        'parent-object': {
                            'activeName': 'Historisk Institut',
                            'hasChildren': True,
                            'name': 'Historisk Institut',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'parent-object': {
                                'activeName': 'Humanistisk fakultet',
                                'hasChildren': True,
                                'name': 'Humanistisk fakultet',
                                'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                                'parent':
                                    '2874e1dc-85e6-4269-823a-e1125484dfd3',
                                'parent-object': {
                                    'activeName': 'Overordnet '
                                                  'Enhed',
                                    'hasChildren': True,
                                    'name': 'Overordnet '
                                            'Enhed',
                                    'org':
                                        '456362c4-0ee4-4e5e-a72c-751239745e62',
                                    'parent': None,
                                    'parent-object': None,
                                    'user-key': 'root',
                                    'uuid':
                                        '2874e1dc-85e6-4269-823a-e1125484dfd3',
                                    'valid-from': '01-01-2016',
                                    'valid-to': 'infinity',
                                    'type': {'name': 'Afdeling'},
                                },
                                'user-key': 'hum',
                                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                                'valid-from': '01-01-2016',
                                'valid-to': 'infinity',
                                'type': {'name': 'Institut'},
                            },
                            'user-key': 'hist',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                            'type': {'name': 'Institut'},
                        },
                        'user-key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'valid-from': '01-01-2016',
                        'valid-to': '01-01-2018',
                        'type': {'name': 'Afdeling'},
                    },
                ],
            )

        with self.subTest('future'):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
                '04c78fc2-72d2-4d02-b55f-807af19eac48/?validity=future',
                [
                    {
                        'activeName': 'Afdeling for Fortidshistorik',
                        'hasChildren': False,
                        'name': 'Afdeling for Fortidshistorik',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': None,
                        'parent-object': None,
                        'type': {'name': ''},
                        'user-key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'valid-from': '01-01-2016',
                        'valid-to': '01-01-2018',
                    },
                ],
            )

    def test_should_add_one_new_contact_channel_correctly(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            'b688513d-11f7-4efc-b679-ab082a2055d0/role-types/location/'
            '00000000-0000-0000-0000-000000000000',
            {'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0'},
            json=util.get_mock_data(
                'mo/writing/update_org_unit_contact_channel.json',
            )
        )

        # TODO: This test should also ask for the values from LoRa
