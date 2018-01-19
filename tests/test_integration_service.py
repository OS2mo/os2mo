#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime

import freezegun

from mora import lora

from . import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_organisation(self):
        with self.subTest('empty'):
            self.assertRequestResponse('/service/o/', [])

            self.assertRequestFails(
                '/service/o/00000000-0000-0000-0000-000000000000/',
                404,
            )

        self.load_sample_structures(minimal=True)

        org_list = [
            {
                'name': 'Aarhus Universitet',
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'user_key': 'AU',
            }
        ]

        org_only = {
            'name': 'Aarhus Universitet',
            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
            'user_key': 'AU',
            'unit_count': 1,
            'person_count': 2,
            'employment_count': 1,
            'child_count': 1,
        }

        self.assertRequestResponse('/service/o/', org_list)

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/',
            org_only,
        )

        with self.subTest('time machine'):
            old_time = datetime.date(2015, 1, 1).isoformat()
            new_time = datetime.date(2017, 1, 1).isoformat()

            with freezegun.freeze_time(new_time, tz_offset=1):
                self.assertRequestResponse(
                    '/service/o/?at=' + old_time, [],
                )

                self.assertRequestFails(
                    '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/?at=' +
                    old_time,
                    404,
                )

            with freezegun.freeze_time(old_time, tz_offset=1):
                self.assertRequestResponse(
                    '/service/o/?at=' + new_time, org_list,
                )

                self.assertRequestResponse(
                    '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/?at=' +
                    new_time,
                    org_only,
                )

        self.load_sample_structures()
        org_only['unit_count'] = 6

        self.assertRequestResponse(
            '/service/o/',
            org_list,
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/',
            org_only,
        )

        with self.subTest('deleted'):
            lora.delete('organisation/organisationenhed',
                        '2874e1dc-85e6-4269-823a-e1125484dfd3')

            self.assertRequestResponse('/service/o/', [])

            # we don't care much about this case; why would you query
            # an unlisted organisation? let's test it regardless...
            org_only['unit_count'] = 5
            org_only['child_count'] = 0
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/', org_only,
            )

    def test_children(self):
        self.load_sample_structures(minimal=True)

        with self.subTest('invalid'):
            self.assertRequestFails(
                '/service/o/00000000-0000-0000-0000-000000000000/children',
                404,
            )

            self.assertRequestFails(
                '/service/ou/00000000-0000-0000-0000-000000000000/children',
                404,
            )

        with self.subTest('resolving a unit as an org, and vice versa'):
            self.assertRequestFails(
                '/service/o/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
                404,
            )
            self.assertRequestFails(
                '/service/ou/456362c4-0ee4-4e5e-a72c-751239745e62/children',
                404,
            )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/children',
            [
                {
                    'child_count': 0,
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
            [],
        )

        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/children',
            [
                {
                    'child_count': 2,
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
            [
                {
                    "name": "Humanistisk fakultet",
                    "user_key": "hum",
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "child_count": 2,
                },
                {
                    "name": "Samfundsvidenskabelige fakultet",
                    "user_key": "samf",
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "child_count": 0,
                }
            ],
        )

    def test_orgunit_search(self):
        self.load_sample_structures()

        result_list = [
            {
                'user_key': 'frem',
                'name': 'Afdeling for Samtidshistorik',
                'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
            },
            {
                'user_key': 'root',
                'name': 'Overordnet Enhed',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
            {
                'user_key': 'fil',
                'name': 'Filosofisk Institut',
                'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
            },
            {
                'user_key': 'hum',
                'name': 'Humanistisk fakultet',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            },
            {
                'user_key': 'samf',
                'name': 'Samfundsvidenskabelige fakultet',
                'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
            },
            {
                'user_key': 'hist',
                'name': 'Historisk Institut',
                'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
            },
        ]

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/',
            result_list,
        )

        with self.subTest('list with a limit'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=2',
                [
                    {
                        'user_key': 'hum',
                        'name': 'Humanistisk fakultet',
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    },
                    {
                        'user_key': 'hist',
                        'name': 'Historisk Institut',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                ],
            )

        with self.subTest('list with a limit and a start'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3&start=1',
                result_list[1:4],
            )

        with self.subTest('paging'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3',
                [
                    {
                        'user_key': 'root',
                        'name': 'Overordnet Enhed',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    },
                    {
                        'user_key': 'hum',
                        'name': 'Humanistisk fakultet',
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    },
                    {
                        'user_key': 'hist',
                        'name': 'Historisk Institut',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3&start=3',
                [
                    {
                        'user_key': 'frem',
                        'name': 'Afdeling for Samtidshistorik',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    },
                    {
                        'user_key': 'fil',
                        'name': 'Filosofisk Institut',
                        'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                    },
                    {
                        'user_key': 'samf',
                        'name': 'Samfundsvidenskabelige fakultet',
                        'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    },
                ],
            )

        with self.subTest('searching'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?query=frem',
                [
                    {
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'name': 'Afdeling for Samtidshistorik',
                        'user_key': 'frem',
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?query=over',
                [
                    {
                        'name': 'Overordnet Enhed',
                        'user_key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    }
                ],
            )

    def test_orgunit(self):
        self.load_sample_structures(minimal=True)

        with self.subTest('invalid'):
            self.assertRequestFails(
                '/service/ou/00000000-0000-0000-0000-000000000000/',
                404,
            )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/',
            {
                'child_count': 0,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/tree',
            {
                'children': [],
                'parent': None,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
        )

        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/',
            {
                'child_count': 2,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/tree',
            {
                'children': [
                    {
                        'child_count': 2,
                        'name': 'Humanistisk fakultet',
                        'user_key': 'hum',
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    },
                    {
                        'child_count': 0,
                        'name': 'Samfundsvidenskabelige fakultet',
                        'user_key': 'samf',
                        'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    },
                ],
                'parent': None,
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            },
        )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e/tree',
            {
                'children': [
                    {
                        'child_count': 0,
                        'name': 'Filosofisk Institut',
                        'user_key': 'fil',
                        'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                    },
                    {
                        'child_count': 1,
                        'name': 'Historisk Institut',
                        'user_key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    },
                ],
                'parent': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                },
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            },
        )
