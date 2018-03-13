#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy
import unittest

import freezegun

from mora import lora
from tests import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Writing(util.LoRATestCase):
    maxDiff = None

    @unittest.expectedFailure
    def test_errors(self):
        self.load_sample_structures(minimal=True)

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            {
                'message': 'missing "itsystem"',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    "itsystem": None,
                    "validity": {
                        "from": "2017-12-01T00:00:00+01",
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/create',
            {
                'message': 'no such it system; no such user',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    "itsystem": {
                        'uuid': '00000000-0000-0000-0000-000000000000',
                    },
                    "validity": {
                        "from": "2017-12-01T00:00:00+01",
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/create',
            {
                'message': 'missing "itsystem"; no such user',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    "itsystem": None,
                    "validity": {
                        "from": "2017-12-01T00:00:00+01",
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            {
                'message': 'missing or invalid start date',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    "itsystem": {
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    },
                    "validity": {
                        "from": None,
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            {
                'message': 'missing "itsystem"; missing or invalid start date',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    "itsystem": {},
                    "validity": {
                        "from": None,
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            {
                'message': 'missing or invalid "itsystem" UUID',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    "itsystem": {
                        'uuid': '42',
                    },
                    "validity": {
                        "from": "2017-12-01T00:00:00+01",
                        "to": None,
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            {
                'message': 'original entry not found!',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    "original": {
                        'name': 'Active Directory',
                        'user_name': 'Fedtmule',
                        # WRONG:
                        'uuid': '00000000-0000-0000-0000-000000000000',
                        "validity": {
                            'from': '2002-02-14T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    "data": {
                        "validity": {
                            "to": '2020-01-01T00:00:00+01:00',
                        },
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            {
                'message': 'original entry not found!',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    "original": {
                        'name': 'Active Directory',
                        'user_name': 'Fedtmule',
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                        # WRONG:
                        'valid_from': '2010-02-14T00:00:00+01:00',
                        'valid_to': None,
                    },
                    "data": {
                        "valid_to": '2020-01-01T00:00:00+01:00',
                    },
                },
            ],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            {
                'message': 'original entry not found!',
                'status': 400,
            },
            json=[
                {
                    "type": "it",
                    'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    "original": {
                        'name': 'Active Directory',
                        'user_name': 'Fedtmule',
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                        "validity": {
                            'from': '2001-02-14T00:00:00+01:00',
                            # WRONG:
                            'to': '3001-02-14T00:00:00+01:00',
                        },
                    },
                    "data": {
                        "validity": {
                            "to": '2020-01-01T00:00:00+01:00',
                        },
                    },
                },
            ],
            status_code=400,
        )

    def test_create_itsystem(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        relations = {
            'tilhoerer': [
                {
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'to_included': False,
                        'to': 'infinity',
                        'from': '2002-02-14 00:00:00+01',
                        'from_included': True,
                    },
                },
            ],
            'tilknyttedepersoner': [
                {
                    'virkning': {
                        'to_included': False,
                        'to': 'infinity',
                        'from': '2002-02-14 00:00:00+01',
                        'from_included': True,
                    },
                    'urn': 'urn:dk:cpr:person:1111111111',
                },
            ],
            'brugertyper': [
                {
                    'virkning': {
                        'to_included': False,
                        'to': 'infinity',
                        'from': '2002-02-14 00:00:00+01',
                        'from_included': True,
                    },
                    'urn': 'urn:email',
                },
            ],
            'adresser': [
                {
                    'virkning': {
                        'to_included': False,
                        'to': 'infinity',
                        'from': '2002-02-14 00:00:00+01',
                        'from_included': True,
                    },
                    'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    'urn': 'urn:mailto:bruger@example.com',
                },
            ],
        }

        original = c.bruger.get(userid)

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/e/{}/details/it?validity=past'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/it'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/it?validity=future'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/'.format(userid),
                {
                    'cpr_no': '1111111111',
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    'org': {
                        'name': 'Aarhus Universitet',
                        'user_key': 'AU',
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    },
                },
            )

            self.assertEqual(original['relationer'], relations)

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            userid,
            json=[
                {
                    "type": "it",
                    "itsystem": {
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    },
                    "validity": {
                        "from": "2017-12-01T00:00:00+01",
                        "to": None,
                    },
                },
            ])

        edited = c.bruger.get(userid)

        self.assertNotEqual(original, edited)

        # XXX: Remove 'garbage' value placed as part of create operation
        del edited['tilstande']['brugergyldighed'][0]['virkning']['notetekst']

        self.assertEqual(original['attributter'], edited['attributter'])
        self.assertEqual(original['tilstande'], edited['tilstande'])

        new_relations = copy.deepcopy(original['relationer'])

        assert 'tilknyttedeitsystemer' not in new_relations

        new_relations['tilknyttedeitsystemer'] = [
            {
                'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                'objekttype': 'itsystem',
                'virkning': {
                    'from': '2017-12-01 00:00:00+01',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False,
                },
            },
        ]

        self.assertEqual(new_relations, edited['relationer'])

        with self.subTest('sanity check'):
            self.assertRequestResponse(
                '/service/e/{}/details/it'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/it?validity=future'.format(userid),
                [
                    {
                        'name': 'Active Directory',
                        'user_name': 'Anders And',
                        'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                        "validity": {
                            'from': '2017-12-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                ],
            )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            userid,
            json=[
                {
                    "type": "it",
                    "itsystem": {
                        'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                    },
                    "validity": {
                        "from": "2016-01-01T00:00:00+01",
                        "to": "2020-01-01T00:00:00+01",
                    },
                },
            ],
        )

        edited = c.bruger.get(userid)

        # XXX: Remove 'garbage' value placed as part of create operation
        del edited['tilstande']['brugergyldighed'][0]['virkning']['notetekst']

        self.assertEqual(original['attributter'], edited['attributter'])
        self.assertEqual(original['tilstande'], edited['tilstande'])

        new_relations['tilknyttedeitsystemer'][:0] = [
            {
                'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                'objekttype': 'itsystem',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'from_included': True,
                    'to': '2020-01-01 00:00:00+01',
                    'to_included': False,
                },
            },
        ]

        self.assertEqual(new_relations, edited['relationer'])

    def test_edit_itsystem_no_overwrite(self):
        self.load_sample_structures()

        # "fedtmule" already has IT systems
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        system_uuid = '59c135c9-2b15-41cc-97c8-b5dff7180beb'

        req = [{
            "type": "it",
            "uuid": system_uuid,
            "data": {
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            {'message': 'original required!', 'status': 400},
            status_code=400,
            json=req,
        )

    def test_edit_itsystem(self):
        self.load_sample_structures()

        # "fedtmule" already has IT systems
        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(userid),
            [{'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              "validity": {
                  'from': '2002-02-14T00:00:00+01:00',
                  'to': None},
              },
             {'name': 'Lokal Rammearkitektur',
              'user_name': 'Fedtmule',
              'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
              "validity": {
                  'from': '2016-01-01T00:00:00+01:00',
                  'to': '2018-01-01T00:00:00+01:00'
              },
              }],
        )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid,
            json=[{
                "type": "it",
                "original": {
                    'name': 'Active Directory',
                    'user_name': 'Fedtmule',
                    'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    "validity": {
                        'from': '2002-02-14T00:00:00+01:00',
                        'to': None,
                    },
                },
                "data": {
                    "validity": {
                        "to": '2020-01-01T00:00:00+01:00',
                    },
                },
            }],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(userid),
            [{'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              "validity": {
                  'from': '2002-02-14T00:00:00+01:00',
                  'to': '2020-01-01T00:00:00+01:00'},
              },
             {'name': 'Lokal Rammearkitektur',
              'user_name': 'Fedtmule',
              'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
              "validity": {
                  'from': '2016-01-01T00:00:00+01:00',
                  'to': '2018-01-01T00:00:00+01:00'
              },
              }],
        )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid,
            json=[{
                "type": "it",
                "original": {
                    'name': 'Lokal Rammearkitektur',
                    'user_name': 'Fedtmule',
                    'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                    "validity": {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': '2018-01-01T00:00:00+01:00',
                    },
                },
                "data": {
                    "validity": {
                        "to": None,
                    },
                },
            }],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(userid),
            [{'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              "validity": {
                  'from': '2002-02-14T00:00:00+01:00',
                  'to': '2020-01-01T00:00:00+01:00'},
              },
             {'name': 'Lokal Rammearkitektur',
              'user_name': 'Fedtmule',
              'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
              "validity": {
                  'from': '2016-01-01T00:00:00+01:00',
                  'to': None
              },
              }],
        )

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid,
            json=[{
                "type": "it",
                "original": {
                    'name': 'Lokal Rammearkitektur',
                    'user_name': 'Fedtmule',
                    'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                    "validity": {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': None,
                    },
                },
                "data": {
                    'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    "validity": {
                        'to': '2040-01-01T00:00:00+01:00',
                    },
                }
            }],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it'.format(userid),
            [{'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              "validity": {
                  'from': '2002-02-14T00:00:00+01:00',
                  'to': '2020-01-01T00:00:00+01:00'},
              },
             {'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              "validity": {
                  'from': '2016-01-01T00:00:00+01:00',
                  'to': '2040-01-01T00:00:00+01:00'
              },
              }],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it?validity=past'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/it?validity=future'.format(userid),
            [],
        )


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Reading(util.LoRATestCase):
    def test_reading(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/it/',
            [

                {
                    'type': None,
                    'user_key': 'LoRa',
                    'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
                    'name': 'Lokal Rammearkitektur',
                },
                {
                    'type': None,
                    'user_key': 'AD',
                    'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
                    'name': 'Active Directory',
                }
            ],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it',
            [{'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              "validity": {
                  'from': '2002-02-14T00:00:00+01:00',
                  'to': None},
              },
             {'name': 'Lokal Rammearkitektur',
              'user_name': 'Fedtmule',
              'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
              "validity": {
                  'from': '2016-01-01T00:00:00+01:00',
                  'to': '2018-01-01T00:00:00+01:00'
              },
              }],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?validity=past',
            [],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?validity=future',
            [],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?at=2018-06-01',
            [{'name': 'Active Directory',
              'user_name': 'Fedtmule',
              'uuid': '59c135c9-2b15-41cc-97c8-b5dff7180beb',
              "validity": {
                  'from': '2002-02-14T00:00:00+01:00',
                  'to': None
              },
              }],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?at=2018-06-01&validity=past',
            [{'name': 'Lokal Rammearkitektur',
              'user_name': 'Fedtmule',
              'uuid': '0872fb72-926d-4c5c-a063-ff800b8ee697',
              "validity": {
                  'from': '2016-01-01T00:00:00+01:00',
                  'to': '2018-01-01T00:00:00+01:00'
              },
              }],
        )

        self.assertRequestResponse(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/details/it'
            '?at=2018-06-01&validity=future',
            [],
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a/details/it',
            [],
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/details/it',
            [],
        )
