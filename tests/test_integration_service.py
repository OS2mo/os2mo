#
# Copyright (c) 2017-2018, Magenta ApS
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

    @classmethod
    def get_lora_environ(cls):
        # force LoRA to run under a UTC timezone, ensuring that we
        # handle this case correctly for reading
        return {
            'TZ': 'UTC',
        }

    def test_organisation(self):
        with self.subTest('empty'):
            self.assertRequestResponse('/service/o/', [])

            self.assertRequestFails(
                '/service/o/00000000-0000-0000-0000-000000000000/',
                404,
            )

        self.load_sample_structures(minimal=True)

        with self.subTest('invalid'):
            self.assertRequestFails(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/'
                '?at=2000-01-01T00:00:00Z',
                404,
            )

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
            'engagement_count': 1,
            'association_count': 1,
            'leave_count': 1,
            'role_count': 1,
            'manager_count': 1,
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
                    'validity': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': None,
                    },
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
                    'validity': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': None,
                    },
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
                    "validity": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": None,
                    },
                    "child_count": 2,
                },
                {
                    "name": "Samfundsvidenskabelige fakultet",
                    "user_key": "samf",
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "validity": {
                        "from": "2017-01-01T00:00:00+01:00",
                        "to": None,
                    },
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
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'to': '2019-01-01T00:00:00+01:00',
                },
            },
            {
                'user_key': 'root',
                'name': 'Overordnet Enhed',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
            {
                'user_key': 'fil',
                'name': 'Filosofisk Institut',
                'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
            {
                'user_key': 'hum',
                'name': 'Humanistisk fakultet',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
            {
                'user_key': 'samf',
                'name': 'Samfundsvidenskabelige fakultet',
                'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                'validity': {
                    'from': '2017-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
            {
                'user_key': 'hist',
                'name': 'Historisk Institut',
                'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'to': '2019-01-01T00:00:00+01:00',
                },
            },
        ]

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/',
            {
                'items': result_list,
                'offset': 0,
                'total': 6
            }
        )

        with self.subTest('list with a limit'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=2',
                {
                    'items': [
                        {
                            'user_key': 'hum',
                            'name': 'Humanistisk fakultet',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'validity': {
                                'from': '2016-01-01T00:00:00+01:00',
                                'to': None,
                            },
                        },
                        {
                            'user_key': 'hist',
                            'name': 'Historisk Institut',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'validity': {
                                'from': '2016-01-01T00:00:00+01:00',
                                'to': '2019-01-01T00:00:00+01:00',
                            },
                        },
                    ],
                    'offset': 0,
                    'total': 6
                }
            )

        with self.subTest('list with a limit and a start'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3&start=1',
                {
                    'items': result_list[1:4],
                    'offset': 1,
                    'total': 6
                }
            )

        with self.subTest('paging'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3',
                {
                    'items': [
                        {
                            'user_key': 'root',
                            'name': 'Overordnet Enhed',
                            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'validity': {
                                'from': '2016-01-01T00:00:00+01:00',
                                'to': None,
                            },
                        },
                        {
                            'user_key': 'hum',
                            'name': 'Humanistisk fakultet',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'validity': {
                                'from': '2016-01-01T00:00:00+01:00',
                                'to': None,
                            },
                        },
                        {
                            'user_key': 'hist',
                            'name': 'Historisk Institut',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'validity': {
                                'from': '2016-01-01T00:00:00+01:00',
                                'to': '2019-01-01T00:00:00+01:00',
                            },
                        },
                    ],
                    'offset': 0,
                    'total': 6
                }
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3&start=3',
                {
                    'items': [
                        {
                            'user_key': 'frem',
                            'name': 'Afdeling for Samtidshistorik',
                            'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                            'validity': {
                                'from': '2016-01-01T00:00:00+01:00',
                                'to': '2019-01-01T00:00:00+01:00',
                            },
                        },
                        {
                            'user_key': 'fil',
                            'name': 'Filosofisk Institut',
                            'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                            'validity': {
                                'from': '2016-01-01T00:00:00+01:00',
                                'to': None,
                            },
                        },
                        {
                            'user_key': 'samf',
                            'name': 'Samfundsvidenskabelige fakultet',
                            'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                            'validity': {
                                'from': '2017-01-01T00:00:00+01:00',
                                'to': None,
                            },
                        },
                    ],
                    'offset': 3,
                    'total': 6
                }
            )

        with self.subTest('searching'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?query=frem',
                {
                    'items': [{
                        'name': 'Afdeling for Samtidshistorik',
                        'user_key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': '2019-01-01T00:00:00+01:00',
                        },
                    }],
                    'offset': 0,
                    'total': 1
                }
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?query=over',
                {
                    'items': [{
                        'name': 'Overordnet Enhed',
                        'user_key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    }],
                    'offset': 0,
                    'total': 1
                }
            )

    def test_orgunit(self):
        self.load_sample_structures(minimal=True)

        with self.subTest('invalid'):
            self.assertRequestFails(
                '/service/ou/00000000-0000-0000-0000-000000000000/',
                404,
            )

            self.assertRequestFails(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/'
                '?at=2000-01-01T00:00:00Z',
                404,
            )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/',
            {
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'to': None,
                },
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'parent': None,
            },
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/details/org_unit',
            [{
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'parent': None,
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                }
            }],
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
            [],
        )

        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/details/org_unit',
            [{
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'parent': None,
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                },
            }],
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/',
            {
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'to': None,
                },
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'parent': None,
            },
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
            [{'child_count': 2,
              'name': 'Humanistisk fakultet',
              'user_key': 'hum',
              'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
              'validity': {'from': '2016-01-01T00:00:00+01:00',
                           'to': None}},
             {'child_count': 0,
              'name': 'Samfundsvidenskabelige fakultet',
              'user_key': 'samf',
              'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
              'validity': {'from': '2017-01-01T00:00:00+01:00',
                           'to': None}}],
        )

    def test_employee(self):
        with self.subTest('empty'):
            self.assertRequestResponse(
                '/service/o/00000000-0000-0000-0000-000000000000/e/',
                {'total': 0, 'items': [], 'offset': 0},
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
                {'total': 0, 'items': [], 'offset': 0},
            )

        self.load_sample_structures(minimal=True)

        with self.subTest('invalid'):
            self.assertRequestFails(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/'
                '?at=1900-01-01T00:00:00Z',
                404,
            )

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/e/',
            {'total': 0, 'items': [], 'offset': 0},
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
            {'items': [{'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'},
                       {'name': 'Fedtmule',
                        'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053'}],
             'offset': 0,
             'total': 2}
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/',
            {
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                'user_key': 'andersand',
                'cpr_no': '0906340000',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
            },
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/',
            {
                'name': 'Fedtmule',
                'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                'user_key': 'fedtmule',
                'cpr_no': '1205320000',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
            },
        )

        with freezegun.freeze_time('1900-01-01'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
                {'total': 0, 'items': [], 'offset': 0},
            )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?at=1900-01-01',
            {'total': 0, 'items': [], 'offset': 0},
        )

        util.load_fixture('organisation/bruger',
                          'create_bruger_andersine.json',
                          'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24')

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
            {
                'items':
                    [
                        {
                            'name': 'Anders And',
                            'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                        },
                        {
                            'name': 'Fedtmule',
                            'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053'
                        },
                        {
                            'name': 'Andersine And',
                            'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24'
                        }
                    ],
                'offset': 0,
                'total': 3
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?limit=1',
            {
                'items': [
                    {
                        'name': 'Andersine And',
                        'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24'
                    }
                ],
                'offset': 0,
                'total': 3
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?limit=1&start=1',
            {
                'items': [
                    {
                        'name': 'Fedtmule',
                        'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                    }
                ],
                'offset': 1,
                'total': 3
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?at=1937-01-01',
            {
                'items': [
                    {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    {
                        'name': 'Fedtmule',
                        'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                    },
                ],
                'offset': 0,
                'total': 2
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?query=Anders',
            {
                'items': [
                    {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    {
                        'name': 'Andersine And',
                        'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24',
                    },
                ],
                'offset': 0,
                'total': 2
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?at=1937-01-01&query=Anders',
            {
                'items': [
                    {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                ],
                'offset': 0,
                'total': 1
            }
        )

        # allow searching by cpr number
        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?query=0906340000',
            {
                'items': [
                    {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                ],
                'offset': 0,
                'total': 1,
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?query=1205320000',
            {
                'items': [
                    {
                        'name': 'Fedtmule',
                        'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                    },
                ],
                'offset': 0,
                'total': 1,
            }
        )

        # disallow partial matches for CPR numbers
        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?query=090634',
            {
                'items': [],
                'offset': 0,
                'total': 0,
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?query=1',
            {
                'items': [],
                'offset': 0,
                'total': 0,
            }
        )

        # bogus
        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?query=0000000000',
            {
                'items': [],
                'offset': 0,
                'total': 0,
            }
        )

    def test_engagement(self):
        self.load_sample_structures()

        func = [
            {
                'job_function': {
                    'example': None,
                    'name': 'Fakultet',
                    'scope': None,
                    'user_key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                'org_unit': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'validity': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': None,
                    },
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'engagement_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
                "validity": {
                    'from': '2017-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
        ]

        with self.subTest('user'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement',
                func,
            )

        with self.subTest('past'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement?validity=past',
                [],
            )

        with self.subTest('future'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement?validity=future',
                [],
            )

            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement?at=2016-01-01&validity=future',
                func,
            )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/engagement',
            func,
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
            '/details/engagement',
            [],
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000'
            '/details/engagement',
            [],
        )

    def test_role(self):
        self.load_sample_structures()

        func = [
            {
                'org_unit': {
                    'name': 'Humanistisk fakultet',
                    'user_key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'validity': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': None,
                    },
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'role_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'uuid': '1b20d0b9-96a0-42a6-b196-293bb86e62e8',
                "validity": {
                    'from': '2017-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
        ]

        with self.subTest('user'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/role',
                func,
            )

        with self.subTest('past'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/role?validity=past',
                [],
            )

        with self.subTest('future'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/role?validity=future',
                [],
            )

            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/role?at=2016-01-01&validity=future',
                func,
            )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/role',
            func,
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
            '/details/role',
            [],
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000'
            '/details/role',
            [],
        )

    def test_leave(self):
        self.load_sample_structures()

        func = [
            {
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'leave_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'uuid': 'b807628c-030c-4f5f-a438-de41c1f26ba5',
                "validity": {
                    'from': '2017-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
        ]

        with self.subTest('user'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/leave',
                func,
            )

        with self.subTest('past'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/leave?validity=past',
                [],
            )

        with self.subTest('future'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/leave?validity=future',
                [],
            )

            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/leave?at=2016-01-01&validity=future',
                func,
            )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/leave',
            [],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
            '/details/leave',
            [],
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000'
            '/details/leave',
            [],
        )

    def test_manager(self):
        self.load_sample_structures()

        func = [
            {
                'address': {
                    'href': 'mailto:ceo@example.com',
                    'name': 'ceo@example.com',
                    'urn': 'urn:mailto:ceo@example.com',
                    'address_type': {
                        'example': 'test@example.com',
                        'name': 'Emailadresse',
                        'scope': 'EMAIL',
                        'user_key': 'Email',
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                },
                'manager_level': {
                    'example': None,
                    'name': 'Institut',
                    'scope': None,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'org_unit': {
                    "name": "Humanistisk fakultet",
                    "user_key": "hum",
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "validity": {
                        "from": "2016-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
                'manager_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'responsibility': {
                    'example': None,
                    'name': 'Fakultet',
                    'scope': None,
                    'user_key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
                },
                'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                "validity": {
                    'from': '2017-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
        ]

        with self.subTest('user'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/manager',
                func,
            )

        with self.subTest('past'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/manager?validity=past',
                [],
            )

        with self.subTest('future'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/manager?validity=future',
                [],
            )

            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/manager?at=2016-01-01&validity=future',
                func,
            )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/manager',
            func,
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
            '/details/manager',
            [],
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000'
            '/details/manager',
            [],
        )

    def test_facet(self):
        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/f/',
            [],
        )

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/f/address_type/',
            [],
        )

        self.assertRequestFails(
            '/service/o/00000000-0000-0000-0000-000000000000/f/kaflaflibob/',
            404,
        )

        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/f/org_unit_type/',
            [],
        )

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/f/address_type/',
            [],
        )

        self.assertRequestFails(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/kaflaflibob/',
            404,
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/',
            [{'name': 'address_type',
              'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                      '/f/address_type/',
              'user_key': 'Adressetype',
              'uuid': 'e337bab4-635f-49ce-aa31-b44047a43aa1'},
             {'name': 'association_type',
              'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
              '/f/association_type/',
              'user_key': 'Tilknytningstype',
              'uuid': 'ef71fe9c-7901-48e2-86d8-84116e210202'},
             {'name': 'org_unit_type',
              'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                      '/f/org_unit_type/',
              'user_key': 'Enhedstype',
              'uuid': 'fc917e7c-fc3b-47c2-8aa5-a0383342a280'}],
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/org_unit_type/',
            {'data': {
                'offset': 0,
                'total': 3,
                'items': [
                    {'example': None,
                     'name': 'Afdeling',
                     'scope': None,
                     'user_key': 'afd',
                     'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'},
                    {'example': None,
                     'name': 'Fakultet',
                     'scope': None,
                     'user_key': 'fak',
                     'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'},
                    {'example': None,
                     'name': 'Institut',
                     'scope': None,
                     'user_key': 'inst',
                     'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'}]},
                'name': 'org_unit_type',
                'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                        '/f/org_unit_type/',
                'user_key': 'Enhedstype',
                'uuid': 'fc917e7c-fc3b-47c2-8aa5-a0383342a280'}
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address_type/',
            {'data': {
                'offset': 0,
                'total': 4,
                'items': [
                    {'example': '20304060',
                     'name': 'Telefonnummer',
                     'scope': 'PHONE',
                     'user_key': 'Telefon',
                     'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec'},
                    {'example': '<UUID>',
                     'name': 'Adresse',
                     'scope': 'DAR',
                     'user_key': 'AdressePost',
                     'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed'},
                    {'example': 'test@example.com',
                     'name': 'Emailadresse',
                     'scope': 'EMAIL',
                     'user_key': 'Email',
                     'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0'},
                    {'example': '5712345000014',
                     'name': 'EAN',
                     'scope': 'EAN',
                     'user_key': 'EAN',
                     'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2'},
                ]},
                'name': 'address_type',
                'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                        '/f/address_type/',
                'user_key': 'Adressetype',
                'uuid': 'e337bab4-635f-49ce-aa31-b44047a43aa1'}
        )

    def test_detail_list(self):
        self.load_sample_structures()

        with self.subTest('fedtmule'):
            self.assertRequestResponse(
                '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
                '/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': False,
                    'it': True,
                    'leave': False,
                    'manager': False,
                    'role': False,
                },
            )

        with self.subTest('anders'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/',
                {
                    'address': True,
                    'association': True,
                    'engagement': True,
                    'it': False,
                    'leave': True,
                    'manager': True,
                    'role': True,
                },
            )

        with self.subTest('hum'):
            self.assertRequestResponse(
                '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
                '/details/',
                {
                    'address': True,
                    'association': True,
                    'engagement': True,
                    'leave': False,
                    'manager': True,
                    'org_unit': True,
                    'role': True,
                },
            )

        with self.subTest('samf'):
            self.assertRequestResponse(
                '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
                '/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'role': False,
                },
            )

        with self.subTest('fil'):
            self.assertRequestResponse(
                '/service/ou/85715fc7-925d-401b-822d-467eb4b163b6'
                '/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'role': False,
                },
            )

        with self.subTest('hist'):
            self.assertRequestResponse(
                '/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'role': False,
                },
            )

        with self.subTest('frem'):
            self.assertRequestResponse(
                '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'role': False,
                },
            )
