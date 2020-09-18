# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import freezegun

from unittest.mock import patch

from . import util


org_unit_type_facet = {
    'description': '',
    'user_key': 'org_unit_type',
    'uuid': 'fc917e7c-fc3b-47c2-8aa5-a0383342a280'
}
org_unit_address_type_facet = {
    'description': '',
    'user_key': 'org_unit_address_type',
    'uuid': '3c44e5d2-7fef-4448-9bf6-449bf414ec49'
}


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@patch('mora.conf_db.get_configuration',
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
                    'facet': org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    'top_level_facet': org_unit_type_facet,
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
                    'facet': org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    'top_level_facet': org_unit_type_facet,
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
                    'facet': org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    'top_level_facet': org_unit_type_facet,
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
                    'facet': org_unit_type_facet,
                    'full_name': 'Afdeling',
                    'name': 'Afdeling',
                    'scope': None,
                    'top_level_facet': org_unit_type_facet,
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
                '?at=1920-01-01T00:00:00Z',
                404,
            )

        result = {
            'items': [
                {
                    'cpr_no': '0910810000',
                    'givenname': 'Erik Smidt',
                    'name': 'Erik Smidt Hansen',
                    'nickname': '',
                    'nickname_givenname': '',
                    'nickname_surname': '',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'surname': 'Hansen',
                    'user_key': 'eriksmidthansen',
                    'uuid': '236e0a78-11a0-4ed9-8545-6286bb8611c7'
                },
                {
                    'cpr_no': '0906340000',
                    'givenname': 'Anders',
                    'name': 'Anders And',
                    'nickname': 'Donald Duck',
                    'nickname_givenname': 'Donald',
                    'nickname_surname': 'Duck',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'surname': 'And',
                    'user_key': 'andersand',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                },
                {
                    'cpr_no': '1205320000',
                    'givenname': 'Fedtmule',
                    'name': 'Fedtmule Hund',
                    'nickname': 'George Geef',
                    'nickname_givenname': 'George',
                    'nickname_surname': 'Geef',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'surname': 'Hund',
                    'user_key': 'fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053'
                },
                {
                    'cpr_no': '0906730000',
                    'givenname': 'Lis',
                    'name': 'Lis Jensen',
                    'nickname': '',
                    'nickname_givenname': '',
                    'nickname_surname': '',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'surname': 'Jensen',
                    'user_key': 'lisjensen',
                    'uuid': '7626ad64-327d-481f-8b32-36c78eb12f8c'
                }
            ],
            'offset': 0,
            'total': 4
        }

        self.assertRequestResponse(
            '/service/o/00000000-0000-0000-0000-000000000000/e/',
            result
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/',
            result
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/',
            {
                'name': 'Anders And',
                'givenname': 'Anders',
                'surname': 'And',
                'nickname': 'Donald Duck',
                'nickname_givenname': 'Donald',
                'nickname_surname': 'Duck',
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
                'nickname': 'George Geef',
                'nickname_givenname': 'George',
                'nickname_surname': 'Geef',
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
                'items': [
                    {
                        'cpr_no': '0910810000',
                        'givenname': 'Erik Smidt',
                        'name': 'Erik Smidt Hansen',
                        'nickname': '',
                        'nickname_givenname': '',
                        'nickname_surname': '',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'Hansen',
                        'user_key': 'eriksmidthansen',
                        'uuid': '236e0a78-11a0-4ed9-8545-6286bb8611c7'
                    },
                    {
                        'cpr_no': '0906340000',
                        'givenname': 'Anders',
                        'name': 'Anders And',
                        'nickname': 'Donald Duck',
                        'nickname_givenname': 'Donald',
                        'nickname_surname': 'Duck',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'And',
                        'user_key': 'andersand',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                    },
                    {
                        'cpr_no': '1205320000',
                        'givenname': 'Fedtmule',
                        'name': 'Fedtmule Hund',
                        'nickname': 'George Geef',
                        'nickname_givenname': 'George',
                        'nickname_surname': 'Geef',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'Hund',
                        'user_key': 'fedtmule',
                        'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053'
                    },
                    {
                        'cpr_no': '0906730000',
                        'givenname': 'Lis',
                        'name': 'Lis Jensen',
                        'nickname': '',
                        'nickname_givenname': '',
                        'nickname_surname': '',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'Jensen',
                        'user_key': 'lisjensen',
                        'uuid': '7626ad64-327d-481f-8b32-36c78eb12f8c'
                    },
                    {
                        'cpr_no': '0901370000',
                        'givenname': 'Andersine',
                        'name': 'Andersine And',
                        'nickname': 'Daisy Duck',
                        'nickname_givenname': 'Daisy',
                        'nickname_surname': 'Duck',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'And',
                        'user_key': 'andersineand',
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
                'items': [{
                    'cpr_no': '0906340000',
                    'givenname': 'Anders',
                    'name': 'Anders And',
                    'nickname': 'Donald Duck',
                    'nickname_givenname': 'Donald',
                    'nickname_surname': 'Duck',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'surname': 'And',
                    'user_key': 'andersand',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                }],
                'offset': 0,
                'total': 5
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?limit=1&start=1',
            {
                'items': [{
                    'cpr_no': '0901370000',
                    'givenname': 'Andersine',
                    'name': 'Andersine And',
                    'nickname': 'Daisy Duck',
                    'nickname_givenname': 'Daisy',
                    'nickname_surname': 'Duck',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'surname': 'And',
                    'user_key': 'andersineand',
                    'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24'
                }],
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
                        'cpr_no': '0906340000',
                        'givenname': 'Anders',
                        'name': 'Anders And',
                        'nickname': 'Donald Duck',
                        'nickname_givenname': 'Donald',
                        'nickname_surname': 'Duck',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'And',
                        'user_key': 'andersand',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                    },
                    {
                        'cpr_no': '1205320000',
                        'givenname': 'Fedtmule',
                        'name': 'Fedtmule Hund',
                        'nickname': 'George Geef',
                        'nickname_givenname': 'George',
                        'nickname_surname': 'Geef',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'Hund',
                        'user_key': 'fedtmule',
                        'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053'
                    }
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
                        'cpr_no': '0906340000',
                        'givenname': 'Anders',
                        'name': 'Anders And',
                        'nickname': 'Donald Duck',
                        'nickname_givenname': 'Donald',
                        'nickname_surname': 'Duck',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'And',
                        'user_key': 'andersand',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                    },
                    {
                        'cpr_no': '0901370000',
                        'givenname': 'Andersine',
                        'name': 'Andersine And',
                        'nickname': 'Daisy Duck',
                        'nickname_givenname': 'Daisy',
                        'nickname_surname': 'Duck',
                        'org': {
                            'name': 'Aarhus Universitet',
                            'user_key': 'AU',
                            'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                        },
                        'surname': 'And',
                        'user_key': 'andersineand',
                        'uuid': 'df55a3ad-b996-4ae0-b6ea-a3241c4cbb24'
                    }
                ],
                'offset': 0,
                'total': 2
            }
        )

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?at=1937-01-01&query=Anders',
            {
                'items': [{
                    'cpr_no': '0906340000',
                    'givenname': 'Anders',
                    'name': 'Anders And',
                    'nickname': 'Donald Duck',
                    'nickname_givenname': 'Donald',
                    'nickname_surname': 'Duck',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'surname': 'And',
                    'user_key': 'andersand',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                }],
                'offset': 0,
                'total': 1
            }
        )

        # allow searching by cpr number
        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/e/'
            '?query=0906340000',
            {
                'items': [{
                    'cpr_no': '0906340000',
                    'givenname': 'Anders',
                    'name': 'Anders And',
                    'nickname': 'Donald Duck',
                    'nickname_givenname': 'Donald',
                    'nickname_surname': 'Duck',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62'
                    },
                    'surname': 'And',
                    'user_key': 'andersand',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                }],
                'offset': 0,
                'total': 1
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
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                'org_unit': {
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'engagement_type': {
                    'uuid': '06f95678-166a-455a-a2ab-121a8d92ea23',
                },
                'uuid': 'd000591f-8705-4324-897a-075e3623f37b',
                'user_key': 'bvn',
                'primary': None,
                'is_primary': None,
                'fraction': None,
                'extension_1': 'test1',
                'extension_2': 'test2',
                'extension_3': None,
                'extension_4': None,
                'extension_5': None,
                'extension_6': None,
                'extension_7': None,
                'extension_8': None,
                'extension_9': 'test9',
                'extension_10': None,
                "validity": {
                    'from': '2017-01-01',
                    'to': None,
                },
            },
        ]

        with self.subTest('user'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/engagement?only_primary_uuid=1',
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
                '/details/engagement?at=2016-01-01&validity=future&only_primary_uuid=1',
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
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'role_type': {
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
                '/details/role?only_primary_uuid=1',
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
                '/details/role?at=2016-01-01&validity=future&only_primary_uuid=1',
                func,
            )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/role?only_primary_uuid=1',
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

        expected = [{
            'engagement': {'uuid': 'd000591f-8705-4324-897a-075e3623f37b'},
            'leave_type': {'uuid': 'bf65769c-5227-49b4-97c5-642cfbe41aa1'},
            'person': {'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'},
            'user_key': 'bvn',
            'uuid': 'b807628c-030c-4f5f-a438-de41c1f26ba5',
            'validity': {'from': '2017-01-01', 'to': None}
        }]

        actual = self.assertRequest(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
            '/details/leave?only_primary_uuid=1',
        )

        self.assertEqual(expected, actual)

    def test_manager(self):
        self.load_sample_structures()

        func = [
            {
                'address': [{
                    'address_type': {'uuid': '28d71012-2919-4b67-a2f0-7b59ed52561e'},
                    'href': 'https://www.openstreetmap.org/?mlon=10.19938084'
                            '&mlat=56.17102843&zoom=16',
                    'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                    'uuid': '414044e0-fe5f-4f82-be20-1e107ad50e80',
                    'value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197'
                }],
                'manager_level': {
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'person': {
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'org_unit': {
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                },
                'manager_type': {
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                'responsibility': [{
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
                '/details/manager?only_primary_uuid=1',
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
                '/details/manager?at=2016-01-01&validity=future&only_primary_uuid=1',
                func,
            )

        self.assertRequestResponse(
            '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
            '/details/manager?only_primary_uuid=1',
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
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/engagement_job_function/",
                    "user_key": "engagement_job_function",
                    "uuid": "1a6045a2-7a8e-4916-ab27-b2402e64f2be",
                },
                {
                    "description": "",
                    'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                            '/f/primary_type/',
                    'user_key': 'primary_type',
                    'uuid': '1f6f34d8-d065-4bb7-9af0-738d25dc0fbf'
                },
                {
                    "description": "",
                    'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                            '/f/kle_number/',
                    'user_key': 'kle_number',
                    'uuid': '27935dbb-c173-4116-a4b5-75022315749d'
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/org_unit_address_type/",
                    "user_key": "org_unit_address_type",
                    "uuid": "3c44e5d2-7fef-4448-9bf6-449bf414ec49",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/engagement_type/",
                    "user_key": "engagement_type",
                    "uuid": "3e702dd1-4103-4116-bb2d-b150aebe807d",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/responsibility/",
                    "user_key": "responsibility",
                    "uuid": "452e1dd0-658b-477a-8dd8-efba105c06d6",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/role_type/",
                    "user_key": "role_type",
                    "uuid": "68ba77bc-4d57-43e2-9c24-0c9eda5fddc7",
                },
                {
                    "description": "",
                    'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                            '/f/org_unit_level/',
                    'user_key': 'org_unit_level',
                    'uuid': '77c39616-dd98-4cf5-87fb-cdb9f3a0e455'
                },
                {
                    "description": "",
                    'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                            '/f/kle_aspect/',
                    'user_key': 'kle_aspect',
                    'uuid': '8a29b2cf-ef98-46f4-9794-0e39354d6ddf'
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/leave_type/",
                    "user_key": "leave_type",
                    "uuid": "99a9d0ab-615e-4e99-8a43-bc9d3cea8438",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/manager_type/",
                    "user_key": "manager_type",
                    "uuid": "a22f8575-89b4-480b-a7ba-b3f1372e25a4",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/employee_address_type/",
                    "user_key": "employee_address_type",
                    "uuid": "baddc4eb-406e-4c6b-8229-17e4a21d3550",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/time_planning/",
                    "user_key": "time_planning",
                    "uuid": "c4ad4c87-28a8-4d5c-afeb-b59de9c9f549",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/visibility/",
                    "user_key": "visibility",
                    "uuid": "c9f103c7-3d53-47c0-93bf-ccb34d044a3f",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/manager_level/",
                    "user_key": "manager_level",
                    "uuid": "d56f174d-c45d-4b55-bdc6-c57bf68238b9",
                },
                {
                    "description": "",
                    "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62"
                    "/f/association_type/",
                    "user_key": "association_type",
                    "uuid": "ef71fe9c-7901-48e2-86d8-84116e210202",
                },
                {
                    "description": "",
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
                     'facet': org_unit_type_facet,
                     'full_name': 'Afdeling',
                     'name': 'Afdeling',
                     'scope': None,
                     'top_level_facet': org_unit_type_facet,
                     'user_key': 'afd',
                     'uuid': '32547559-cfc1-4d97-94c6-70b192eff825'},
                    {'example': None,
                     'facet': org_unit_type_facet,
                     'full_name': 'Fakultet',
                     'name': 'Fakultet',
                     'scope': None,
                     'top_level_facet': org_unit_type_facet,
                     'user_key': 'fak',
                     'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6'},
                    {'example': None,
                     'facet': org_unit_type_facet,
                     'full_name': 'Institut',
                     'name': 'Institut',
                     'scope': None,
                     'top_level_facet': org_unit_type_facet,
                     'user_key': 'inst',
                     'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52'}]},
                'description': '',
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
                     'facet': org_unit_address_type_facet,
                     'full_name': 'Telefon',
                     'name': 'Telefon',
                     'scope': 'PHONE',
                     'top_level_facet': org_unit_address_type_facet,
                     'user_key': 'OrgEnhedTelefon',
                     'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec'},
                    {'example': '<UUID>',
                     'facet': org_unit_address_type_facet,
                     'full_name': 'Postadresse',
                     'name': 'Postadresse',
                     'scope': 'DAR',
                     'top_level_facet': org_unit_address_type_facet,
                     'user_key': 'OrgEnhedPostadresse',
                     'uuid': '28d71012-2919-4b67-a2f0-7b59ed52561e'},
                    {'example': 'test@example.com',
                     'facet': org_unit_address_type_facet,
                     'full_name': 'Email',
                     'name': 'Email',
                     'scope': 'EMAIL',
                     'top_level_facet': org_unit_address_type_facet,
                     'user_key': 'OrgEnhedEmail',
                     'uuid': '73360db1-bad3-4167-ac73-8d827c0c8751'},
                    {'example': '5712345000014',
                     'facet': org_unit_address_type_facet,
                     'full_name': 'EAN',
                     'name': 'EAN',
                     'scope': 'EAN',
                     'top_level_facet': org_unit_address_type_facet,
                     'user_key': 'EAN',
                     'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2'},
                ]},
                'description': '',
                'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                        '/f/org_unit_address_type/',
                'user_key': 'org_unit_address_type',
                'uuid': '3c44e5d2-7fef-4448-9bf6-449bf414ec49'}
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
                    'kle': False,
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
                    'kle': False,
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
                    'kle': False,
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
                    'kle': False,
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
                    'kle': False,
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
                    'kle': False,
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
                    'kle': False,
                    'leave': False,
                    'manager': False,
                    'org_unit': True,
                    'related_unit': False,
                    'role': False,
                },
            )
