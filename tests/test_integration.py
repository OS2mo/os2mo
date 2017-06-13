#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import unittest

import requests

from . import util
from mora import lora


class IntegrationTests(util.LoRATestCase):
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
                    'valid-from': '2017-01-01 12:00:00+01',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'valid-to': 'infinity', 'valid-from': '2017-01-01 12:00:00+01',
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
                            'user-key': 'hum',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'valid-from': '2017-01-01 12:00:00+01',
                            'valid-to': 'infinity',
                        },
                        {
                            'children': [],
                            'hasChildren': False,
                            'name': 'Samfundsvidenskabelige fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'user-key': 'samf',
                            'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                            'valid-from': '2017-01-01 12:00:00+01',
                            'valid-to': 'infinity'
                        },
                    ],
                    'hasChildren': True,
                    'name': 'Overordnet Enhed',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': None,
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'valid-from': '2017-01-01 12:00:00+01',
                    'valid-to': 'infinity'},
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'valid-from': '2017-01-01 12:00:00+01',
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
                            'valid-from': '2017-01-01 12:00:00+01',
                            'valid-to': 'infinity',
                        },
                        {
                            'children': [],
                            'hasChildren': False,
                            'name': 'Samfundsvidenskabelige fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'user-key': 'samf',
                            'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                            'valid-from': '2017-01-01 12:00:00+01',
                            'valid-to': 'infinity'
                        },
                    ],
                    'hasChildren': True,
                    'name': 'Overordnet Enhed',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': None,
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'valid-from': '2017-01-01 12:00:00+01',
                    'valid-to': 'infinity'},
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'valid-from': '2017-01-01 12:00:00+01',
                'valid-to': 'infinity',
            })

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/full-hierarchy?'
            'treeType=specific&orgUnitId=2874e1dc-85e6-4269-823a-e1125484dfd3',
            [
                {
                    'children': [
                        {
                            'children': [],
                            'hasChildren': False,
                            'name': 'Filosofisk Institut',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'user-key': 'fil',
                            'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                            'valid-from': '2017-01-01 12:00:00+01',
                            'valid-to': 'infinity',
                        },
                        {
                            'children': [],
                            'hasChildren': True,
                            'name': 'Historisk Institut',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'user-key': 'hist',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'valid-from': '2017-01-01 12:00:00+01',
                            'valid-to': 'infinity',
                        }
                    ],
                    'hasChildren': True,
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '2017-01-01 12:00:00+01',
                    'valid-to': 'infinity',
                },
                {
                    'children': [],
                    'hasChildren': False,
                    'name': 'Samfundsvidenskabelige fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'user-key': 'samf',
                    'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    'valid-from': '2017-01-01 12:00:00+01',
                    'valid-to': 'infinity',
                }
            ]
        )
        print(self.client.get('/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e/').json)
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
                        'children': [],
                        'hasChildren': True,
                        'name': 'Overordnet Enhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': None,
                        'user-key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'valid-from': '2017-01-01 12:00:00+01',
                        'valid-to': 'infinity',
                    },
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '2017-01-01 12:00:00+01',
                    'valid-to': 'infinity',
                }
            ]
        )
