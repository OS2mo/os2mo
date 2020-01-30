# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import freezegun

from unittest.mock import patch
from mora import lora

from . import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@patch('mora.service.configuration_options.get_configuration',
       new=lambda *x: {})
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
            'person_count': 4,
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

        self.load_sample_structures()
        org_only['unit_count'] = 11
        org_only['child_count'] = 2

        self.assertRequestResponse(
            '/service/o/',
            org_list,
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/',
            org_only,
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
                        'from': '2016-01-01',
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
                    'child_count': 1,
                    'user_key': 'løn',
                    'name': 'Lønorganisation',
                    'uuid': 'b1f69701-86d8-496e-a3f1-ccef18ac1958',
                    'validity': {
                        'from': '2017-01-01',
                        'to': None
                    }
                },
                {
                    'child_count': 4,
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'validity': {
                        'from': '2016-01-01',
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
                        "from": "2016-01-01",
                        "to": None,
                    },
                    "child_count": 2,
                },
                {
                    "name": "Samfundsvidenskabelige fakultet",
                    "user_key": "samf",
                    "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                    "validity": {
                        "from": "2017-01-01",
                        "to": None,
                    },
                    "child_count": 0,
                },
                {
                    "name": "Skole og Børn",
                    "user_key": "skole-børn",
                    "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
                    "validity": {
                        "from": "2017-01-01",
                        "to": None
                    },
                    "child_count": 1,
                },
                {
                    "name": "Social og sundhed",
                    "user_key": "social-sundhed",
                    "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
                    "validity": {
                        "from": "2017-01-01",
                        "to": None
                    },
                    "child_count": 0,
                },
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
                    'from': '2016-01-01',
                    'to': '2018-12-31',
                },
            },
            {
                'user_key': 'root',
                'name': 'Overordnet Enhed',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'validity': {
                    'from': '2016-01-01',
                    'to': None,
                },
            },
            {
                'user_key': 'social_og_sundhed-løn',
                'name': 'Social og sundhed',
                'uuid': '5942ce50-2be8-476f-914b-6769a888a7c8',
                'validity': {
                    'from': '2017-01-01',
                    'to': None,
                },
            },
            {
                'user_key': 'social-sundhed',
                'name': 'Social og sundhed',
                'uuid': '68c5d78e-ae26-441f-a143-0103eca8b62a',
                'validity': {
                    'from': '2017-01-01',
                    'to': None,
                },
            },
            {
                'user_key': 'fil',
                'name': 'Filosofisk Institut',
                'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                'validity': {
                    'from': '2016-01-01',
                    'to': None,
                },
            },
            {
                'user_key': 'hum',
                'name': 'Humanistisk fakultet',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                'validity': {
                    'from': '2016-01-01',
                    'to': None,
                },
            },
            {
                'user_key': 'løn',
                'name': 'Lønorganisation',
                'uuid': 'b1f69701-86d8-496e-a3f1-ccef18ac1958',
                'validity': {
                    'from': '2017-01-01',
                    'to': None
                }
            },
            {
                'user_key': 'samf',
                'name': 'Samfundsvidenskabelige fakultet',
                'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                'validity': {
                    'from': '2017-01-01',
                    'to': None,
                },
            },
            {
                'user_key': 'hist',
                'name': 'Historisk Institut',
                'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                'validity': {
                    'from': '2016-01-01',
                    'to': '2018-12-31',
                },
            },
            {
                'user_key': 'skole-børn',
                'name': 'Skole og Børn',
                'uuid': 'dad7d0ad-c7a9-4a94-969d-464337e31fec',
                'validity': {
                    'from': '2017-01-01',
                    'to': None,
                },
            },
            {
                'user_key': 'it_sup',
                'name': 'IT-Support',
                'uuid': 'fa2e23c9-860a-4c90-bcc6-2c0721869a25',
                'validity': {
                    'from': '2016-01-01',
                    'to': None,
                },
            },
        ]

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/',
            {
                'items': result_list,
                'offset': 0,
                'total': 11
            }
        )

        with self.subTest('list with a limit'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=2',
                {
                    'items': [
                        {
                            'user_key': 'frem',
                            'name': 'Afdeling for Samtidshistorik',
                            'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                            'validity': {
                                'from': '2016-01-01',
                                'to': '2018-12-31',
                            },
                        },
                        {
                            'user_key': 'fil',
                            'name': 'Filosofisk Institut',
                            'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None,
                            },
                        },
                    ],
                    'offset': 0,
                    'total': 11,
                }
            )

        with self.subTest('list with a limit and a start'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3&start=1',
                {
                    'items': [
                        {
                            'user_key': 'frem',
                            'name': 'Afdeling for Samtidshistorik',
                            'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                            'validity': {
                                'from': '2016-01-01',
                                'to': '2018-12-31',
                            },
                        },
                        {
                            'user_key': 'hum',
                            'name': 'Humanistisk fakultet',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None,
                            },
                        },
                        {
                            'user_key': 'hist',
                            'name': 'Historisk Institut',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'validity': {
                                'from': '2016-01-01',
                                'to': '2018-12-31',
                            },
                        },
                    ],
                    'offset': 1,
                    'total': 11,
                }
            )

        with self.subTest('paging'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3',
                {
                    'items': [
                        {
                            'user_key': 'frem',
                            'name': 'Afdeling for Samtidshistorik',
                            'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                            'validity': {
                                'from': '2016-01-01',
                                'to': '2018-12-31',
                            },
                        },
                        {
                            'user_key': 'fil',
                            'name': 'Filosofisk Institut',
                            'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None,
                            },
                        },
                        {
                            'user_key': 'hist',
                            'name': 'Historisk Institut',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'validity': {
                                'from': '2016-01-01',
                                'to': '2018-12-31',
                            },
                        },
                    ],
                    'offset': 0,
                    'total': 11,
                }
            )

            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/ou/'
                '?limit=3&start=3',
                {
                    'items': [
                        {
                            'user_key': 'hum',
                            'name': 'Humanistisk fakultet',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None,
                            },
                        },
                        {
                            'user_key': 'løn',
                            'name': 'Lønorganisation',
                            'uuid': 'b1f69701-86d8-496e-a3f1-ccef18ac1958',
                            'validity': {
                                'from': '2017-01-01',
                                'to': None
                            }
                        },
                        {
                            'user_key': 'it_sup',
                            'name': 'IT-Support',
                            'uuid': 'fa2e23c9-860a-4c90-bcc6-2c0721869a25',
                            'validity': {
                                'from': '2016-01-01',
                                'to': None,
                            },
                        },
                    ],
                    'offset': 3,
                    'total': 11,
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
                            'from': '2016-01-01',
                            'to': '2018-12-31',
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
                            'from': '2016-01-01',
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
                'user_settings': {'orgunit': {}},
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'validity': {
                    'from': '2016-01-01',
                    'to': None,
                },
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_level': None,
                'org_unit_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'parent': None,
                'time_planning': None,
                'location': '',
            },
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/details/org_unit',
            [{
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'user_settings': {'orgunit': {}},
                'location': '',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_level': None,
                'org_unit_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'parent': None,
                'time_planning': None,
                'validity': {
                    'from': '2016-01-01', 'to': None,
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
                'user_settings': {'orgunit': {}},
                'location': '',
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_level': None,
                'org_unit_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'parent': None,
                'time_planning': None,
                'validity': {
                    'from': '2016-01-01', 'to': None,
                },
            }],
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/',
            {
                'name': 'Overordnet Enhed',
                'user_key': 'root',
                'user_settings': {'orgunit': {}},
                'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                'validity': {
                    'from': '2016-01-01',
                    'to': None,
                },
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_level': None,
                'org_unit_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'parent': None,
                'time_planning': None,
                'location': '',
            },
        )

        self.assertRequestResponse(
            '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3/children',
            [{'child_count': 2,
              'name': 'Humanistisk fakultet',
              'user_key': 'hum',
              'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
              'validity': {'from': '2016-01-01',
                           'to': None}},
             {'child_count': 0,
              'name': 'Samfundsvidenskabelige fakultet',
              'user_key': 'samf',
              'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
              'validity': {'from': '2017-01-01',
                           'to': None}},
             {"child_count": 1,
              "name": "Skole og Børn",
              "user_key": "skole-børn",
              "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
              "validity": {"from": "2017-01-01",
                           "to": None}},
             {"child_count": 0,
              "name": "Social og sundhed",
              "user_key": "social-sundhed",
              "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
              "validity": {"from": "2017-01-01",
                           "to": None}}],
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
            {'items': [{'name': 'Erik Smidt Hansen',
                        'givenname': 'Erik Smidt',
                        'surname': 'Hansen',
                        'uuid': '236e0a78-11a0-4ed9-8545-6286bb8611c7'},
                       {'name': 'Anders And',
                        'givenname': 'Anders',
                        'surname': 'And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'},
                       {'name': 'Fedtmule Hund',
                        'givenname': 'Fedtmule',
                        'surname': 'Hund',
                        'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053'},
                       {'name': 'Lis Jensen',
                        'givenname': 'Lis',
                        'surname': 'Jensen',
                        'uuid': '7626ad64-327d-481f-8b32-36c78eb12f8c'}],
             'offset': 0,
             'total': 4}
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/',
            {
                'name': 'Anders And',
                'givenname': 'Anders',
                'surname': 'And',
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
                'name': 'Fedtmule Hund',
                'givenname': 'Fedtmule',
                'surname': 'Hund',
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
                            'name': 'Erik Smidt Hansen',
                            'givenname': 'Erik Smidt',
                            'surname': 'Hansen',
                            'uuid': '236e0a78-11a0-4ed9-8545-6286bb8611c7'
                        },
                        {
                            'name': 'Anders And',
                            'givenname': 'Anders',
                            'surname': 'And',
                            'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                        },
                        {
                            'name': 'Fedtmule Hund',
                            'givenname': 'Fedtmule',
                            'surname': 'Hund',
                            'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053'
                        },
                        {
                            'name': 'Lis Jensen',
                            'givenname': 'Lis',
                            'surname': 'Jensen',
                            'uuid': '7626ad64-327d-481f-8b32-36c78eb12f8c'
                        },
                        {
                            'name': 'Andersine And',
                            'givenname': 'Andersine',
                            'surname': 'And',
                            'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24'
                        }
                    ],
                'offset': 0,
                'total': 5
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?limit=1',
            {
                'items': [
                    {
                        'name': 'Anders And',
                        'givenname': 'Anders',
                        'surname': 'And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                    }
                ],
                'offset': 0,
                'total': 5
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?limit=1&start=1',
            {
                'items': [
                    {
                        'name': 'Andersine And',
                        'givenname': 'Andersine',
                        'surname': 'And',
                        'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24'
                    }
                ],
                'offset': 1,
                'total': 5
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?at=1937-01-01',
            {
                'items': [
                    {
                        'name': 'Anders And',
                        'givenname': 'Anders',
                        'surname': 'And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    {
                        'name': 'Fedtmule Hund',
                        'givenname': 'Fedtmule',
                        'surname': 'Hund',
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
                        'givenname': 'Anders',
                        'surname': 'And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    {
                        'name': 'Andersine And',
                        'givenname': 'Andersine',
                        'surname': 'And',
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
                        'givenname': 'Anders',
                        'surname': 'And',
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
                        'givenname': 'Anders',
                        'surname': 'And',
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
                        'name': 'Fedtmule Hund',
                        'givenname': 'Fedtmule',
                        'surname': 'Hund',
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

        andersand = [
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
                        'from': '2016-01-01',
                        'to': None,
                    },
                },
                'person': {
                    'name': 'Anders And',
                    'givenname': 'Anders',
                    'surname': 'And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'engagement_type': {
                    'example': None,
                    'name': 'Ansat',
                    'scope': None,
                    'user_key': 'ansat',
                    'uuid': '06f95678-166a-455a-a2ab-121a8d92ea23',
                },
                'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
                'user_key': 'bvn',
                'primary': None,
                'is_primary': None,
                'fraction': None,
                "validity": {
                    'from': '2017-01-01',
                    'to': None,
                },
            },
        ]

        with self.subTest('user'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement',
                andersand,
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
                andersand,
            )

        r = self.assertRequest(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/engagement',
        )
        self.assertEqual(3, len(r))

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
                        'from': '2016-01-01',
                        'to': None,
                    },
                },
                'person': {
                    'name': 'Anders And',
                    'givenname': 'Anders',
                    'surname': 'And',
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
                'user_key': 'bvn',
                "validity": {
                    'from': '2017-01-01',
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
                    'givenname': 'Anders',
                    'surname': 'And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'leave_type': {
                    'example': None,
                    'name': 'Barselsorlov',
                    'scope': None,
                    'user_key': 'barselsorlov',
                    'uuid': 'bf65769c-5227-49b4-97c5-642cfbe41aa1',
                },
                'uuid': 'b807628c-030c-4f5f-a438-de41c1f26ba5',
                'user_key': 'bvn',
                "validity": {
                    'from': '2017-01-01',
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
                'address': [{
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Postadresse',
                        'scope': 'DAR',
                        'user_key': 'OrgEnhedPostadresse',
                        'uuid': '28d71012-2919-4b67-a2f0-7b59ed52561e'
                    },
                    'href': 'https://www.openstreetmap.org/'
                            '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                    'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                    'uuid': '414044e0-fe5f-4f82-be20-1e107ad50e80',
                    'value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197'
                }],
                'manager_level': {
                    'example': None,
                    'name': 'Institut',
                    'scope': None,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'person': {
                    'name': 'Anders And',
                    'givenname': 'Anders',
                    'surname': 'And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'org_unit': {
                    "name": "Humanistisk fakultet",
                    "user_key": "hum",
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "validity": {
                        "from": "2016-01-01",
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
                'responsibility': [{
                    'example': None,
                    'name': 'Fakultet',
                    'scope': None,
                    'user_key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
                }],
                'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                'user_key': 'be736ee5-5c44-4ed9-b4a4-15ffa19e2848',
                "validity": {
                    'from': '2017-01-01',
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

        self.assertRequestFails(
            '/service/o/00000000-0000-0000-0000-000000000000/f/address_type/',
            404,
        )

        self.assertRequestFails(
            '/service/o/00000000-0000-0000-0000-000000000000/f/kaflaflibob/',
            404,
        )

        self.load_sample_structures()

        self.assertRequestFails(
            '/service/o/00000000-0000-0000-0000-000000000000/f/org_unit_type/',
            404,
        )

        self.assertRequestFails(
            '/service/o/00000000-0000-0000-0000-000000000000/f/address_type/',
            404,
        )

        self.assertRequestFails(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/kaflaflibob/',
            404,
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/',
            [
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/engagement_job_function/",
                    "user_key": "engagement_job_function",
                    "uuid": "1a6045a2-7a8e-4916-ab27-b2402e64f2be",
                },
                {
                    'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                            '/f/primary_type/',
                    'user_key': 'primary_type',
                    'uuid': '1f6f34d8-d065-4bb7-9af0-738d25dc0fbf'
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/org_unit_address_type/",
                    "user_key": "org_unit_address_type",
                    "uuid": "3c44e5d2-7fef-4448-9bf6-449bf414ec49",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/engagement_type/",
                    "user_key": "engagement_type",
                    "uuid": "3e702dd1-4103-4116-bb2d-b150aebe807d",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/responsibility/",
                    "user_key": "responsibility",
                    "uuid": "452e1dd0-658b-477a-8dd8-efba105c06d6",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/role_type/",
                    "user_key": "role_type",
                    "uuid": "68ba77bc-4d57-43e2-9c24-0c9eda5fddc7",
                },
                {
                    'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                            '/f/org_unit_level/',
                    'user_key': 'org_unit_level',
                    'uuid': '77c39616-dd98-4cf5-87fb-cdb9f3a0e455'
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/leave_type/",
                    "user_key": "leave_type",
                    "uuid": "99a9d0ab-615e-4e99-8a43-bc9d3cea8438",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/manager_type/",
                    "user_key": "manager_type",
                    "uuid": "a22f8575-89b4-480b-a7ba-b3f1372e25a4",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/employee_address_type/",
                    "user_key": "employee_address_type",
                    "uuid": "baddc4eb-406e-4c6b-8229-17e4a21d3550",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/time_planning/",
                    "user_key": "time_planning",
                    "uuid": "c4ad4c87-28a8-4d5c-afeb-b59de9c9f549",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/visibility/",
                    "user_key": "visibility",
                    "uuid": "c9f103c7-3d53-47c0-93bf-ccb34d044a3f",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/manager_level/",
                    "user_key": "manager_level",
                    "uuid": "d56f174d-c45d-4b55-bdc6-c57bf68238b9",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/association_type/",
                    "user_key": "association_type",
                    "uuid": "ef71fe9c-7901-48e2-86d8-84116e210202",
                },
                {
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/org_unit_type/",
                    "user_key": "org_unit_type",
                    "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280",
                },
            ],
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
                'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                        '/f/org_unit_type/',
                'user_key': 'org_unit_type',
                'uuid': 'fc917e7c-fc3b-47c2-8aa5-a0383342a280'}
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/' +
            'org_unit_address_type/',
            {'data': {
                'offset': 0,
                'total': 4,
                'items': [
                    {'example': '20304060',
                     'name': 'Telefon',
                     'scope': 'PHONE',
                     'user_key': 'OrgEnhedTelefon',
                     'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec'},
                    {'example': '<UUID>',
                     'name': 'Postadresse',
                     'scope': 'DAR',
                     'user_key': 'OrgEnhedPostadresse',
                     'uuid': '28d71012-2919-4b67-a2f0-7b59ed52561e'},
                    {'example': 'test@example.com',
                     'name': 'Email',
                     'scope': 'EMAIL',
                     'user_key': 'OrgEnhedEmail',
                     'uuid': '73360db1-bad3-4167-ac73-8d827c0c8751'},
                    {'example': '5712345000014',
                     'name': 'EAN',
                     'scope': 'EAN',
                     'user_key': 'EAN',
                     'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2'},
                ]},
                'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                        '/f/org_unit_address_type/',
                'user_key': 'org_unit_address_type',
                'uuid': '3c44e5d2-7fef-4448-9bf6-449bf414ec49'}
        )

    def test_details_multiple(self):
        """Test that multiple details of a single type renders as expected"""
        self.load_sample_structures()
        c = lora.Connector()

        engagement = {
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "note": "Automatisk indl\u00e6sning",
            "relationer": {
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ],
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "2017-01-01 00:00:00+01:00",
                            "to": "infinity"
                        }
                    }
                ]
            }
        }

        c.organisationfunktion.create(
            engagement, '09e79d96-2904-444f-94b1-0e98b0b07e7c')

        expected = [{
            'engagement_type': {
                'example': None,
                'name': 'Ansat',
                'scope': None,
                'user_key': 'ansat',
                'uuid': '06f95678-166a-455a-a2ab-121a8d92ea23'
            },
            'job_function': {
                'example': None,
                'name': 'Fakultet',
                'scope': None,
                'user_key': 'fak',
                'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
            },
            'org_unit': {
                'name': 'Humanistisk fakultet',
                'user_key': 'hum',
                'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                'validity': {
                    'from': '2016-01-01',
                    'to': None
                }
            },
            'person': {
                'name': 'Anders And',
                'givenname': 'Anders',
                'surname': 'And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
            },
            'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
            'user_key': 'bvn',
            'primary': None,
            'is_primary': None,
            'fraction': None,
            'validity': {
                'from': '2017-01-01',
                'to': None
            }
        }, {
            'engagement_type': {
                'example': None,
                'name': 'Institut',
                'scope': None,
                'user_key': 'inst',
                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'
            },
            'job_function': {
                'example': None,
                'name': 'Fakultet',
                'scope': None,
                'user_key': 'fak',
                'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'
            },
            'org_unit': {
                'name': 'Samfundsvidenskabelige fakultet',
                'user_key': 'samf',
                'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                'validity': {
                    'from': '2017-01-01',
                    'to': None
                }
            },
            'person': {
                'name': 'Anders And',
                'givenname': 'Anders',
                'surname': 'And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
            },
            'uuid': '09e79d96-2904-444f-94b1-0e98b0b07e7c',
            'user_key': 'bvn',
            'primary': None,
            'is_primary': None,
            'fraction': None,
            'validity': {
                'from': '2017-01-01',
                'to': None
            }
        }]

        actual = self.request(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
            '/details/engagement',
        ).json

        def sorter(e):
            return e['uuid']

        self.assertEqual(
            sorted(expected, key=sorter),
            sorted(actual, key=sorter)
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
                    'it': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': False,
                    'related_unit': False,
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
                    'it': True,
                    'leave': True,
                    'manager': True,
                    'org_unit': False,
                    'related_unit': False,
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
                    'it': False,
                    'leave': False,
                    'manager': True,
                    'org_unit': True,
                    'related_unit': True,
                    'role': True,
                },
            )

        with self.subTest('samf'):
            self.assertRequestResponse(
                '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
                '/details/',
                {
                    'address': False,
                    'association': False,
                    'engagement': False,
                    'it': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'related_unit': False,
                    'role': False,
                },
            )

        with self.subTest('fil'):
            self.assertRequestResponse(
                '/service/ou/85715fc7-925d-401b-822d-467eb4b163b6'
                '/details/',
                {
                    'address': False,
                    'association': False,
                    'engagement': False,
                    'it': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'related_unit': False,
                    'role': False,
                },
            )

        with self.subTest('hist'):
            self.assertRequestResponse(
                '/service/ou/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/details/',
                {
                    'address': False,
                    'association': False,
                    'engagement': False,
                    'it': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'related_unit': True,
                    'role': False,
                },
            )

        with self.subTest('frem'):
            self.assertRequestResponse(
                '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/details/',
                {
                    'address': False,
                    'association': False,
                    'engagement': False,
                    'it': True,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'related_unit': False,
                    'role': False,
                },
            )
