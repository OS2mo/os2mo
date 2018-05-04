#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy
import logging
import unittest.mock

import freezegun

from mora import lora
from tests import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@util.mock('dawa-addresses.json', allow_mox=True)
class Writing(util.LoRATestCase):
    maxDiff = None

    def test_employee_address(self, mock):
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
                        'from': '1934-06-09 00:00:00+01',
                        'from_included': True,
                    },
                },
            ],
            'tilknyttedepersoner': [
                {
                    'virkning': {
                        'to_included': False,
                        'to': 'infinity',
                        'from': '1934-06-09 00:00:00+01',
                        'from_included': True,
                    },
                    'urn': 'urn:dk:cpr:person:0906340000',
                },
            ],
            'brugertyper': [
                {
                    'virkning': {
                        'to_included': False,
                        'to': 'infinity',
                        'from': '1934-06-09 00:00:00+01',
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
                        'from': '1934-06-09 00:00:00+01',
                        'from_included': True,
                    },
                    'urn': 'urn:mailto:bruger@example.com',
                    'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
            ],
        }

        original = c.bruger.get(userid)

        address_class = {
            'example': '<UUID>',
            'name': 'Adresse',
            'scope': 'DAR',
            'user_key': 'Adresse',
            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
        }

        ean_class = {
            'example': '5712345000014',
            'name': 'EAN',
            'scope': 'EAN',
            'user_key': 'EAN',
            'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
        }

        email_class = {
            'example': 'test@example.com',
            'name': 'Emailadresse',
            'scope': 'EMAIL',
            'user_key': 'Email',
            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
        }

        phone_class = {
            'example': '20304060',
            'name': 'Telefonnummer',
            'scope': 'PHONE',
            'user_key': 'Telefon',
            'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
        }

        addresses = [
            {
                'address_type': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'href': 'mailto:bruger@example.com',
                'name': 'bruger@example.com',
                'urn': 'urn:mailto:bruger@example.com',
                'validity': {
                    'from': '1934-06-09T00:00:00+01:00',
                    'to': None,
                },
            }
        ]

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/f/address_type/',
                {'data': {
                    'offset': 0, 'total': 4,
                    'items': [phone_class, address_class,
                              email_class, ean_class]},
                    'name': 'address_type',
                 'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                         '/f/address_type/',
                 'user_key': 'Adressetype',
                 'uuid': 'e337bab4-635f-49ce-aa31-b44047a43aa1'}
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address?validity=past'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address'.format(userid),
                addresses,
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address?validity=future'.format(userid),
                [],
            )

            self.assertEqual(original['relationer'], relations)

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            userid,
            json=[
                {
                    "type": "address",
                    "address_type": ean_class,
                    "value": '1234567890',
                    "validity": {
                        "from": "2013-01-01T00:00:00+01:00",
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

        new_relations['adresser'][:0] = [
            {
                'urn': 'urn:magenta.dk:ean:1234567890',
                'objekttype': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                'virkning': {
                    'from': '2013-01-01 00:00:00+01',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False,
                },
            },
        ]

        addresses += [
            {
                'address_type': {
                    'example': '5712345000014',
                    'name': 'EAN',
                    'scope': 'EAN',
                    'user_key': 'EAN',
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'href': None,
                'name': '1234567890',
                'urn': 'urn:magenta.dk:ean:1234567890',
                'validity': {
                    'from': '2013-01-01T00:00:00+01:00',
                    'to': None,
                },
            },
        ]

        self.assertEqual(new_relations, edited['relationer'])

        with self.subTest('sanity check'):
            self.assertRequestResponse(
                '/service/e/{}/details/address?validity=past'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address'.format(userid),
                addresses,
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address?validity=future'.format(userid),
                [],
            )

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            userid,
            json=[
                {
                    "type": "address",
                    "address_type": email_class,
                    "value": "hest@example.com",
                    "validity": {
                        "from": "2014-01-01T00:00:00+01",
                    },
                },
                {
                    "type": "address",
                    "address_type": address_class,
                    "uuid": "ae95777c-7ec1-4039-8025-e2ecce5099fb",
                    "validity": {
                        "from": "2015-01-01T00:00:00+01",
                    },
                },
                {
                    "type": "address",
                    "address_type": phone_class,
                    "value": '3336 9696',
                    "validity": {
                        "from": "2016-01-01T00:00:00+01",
                    },
                },
            ],
        )

        addresses += [
            {
                'address_type': email_class,
                'href': 'mailto:hest@example.com',
                'name': 'hest@example.com',
                'urn': 'urn:mailto:hest@example.com',
                'validity': {
                    'from': '2014-01-01T00:00:00+01:00', 'to': None,
                },
            },
            {
                'address_type': address_class,
                'href': 'https://www.openstreetmap.org/'
                '?mlon=10.20320628&mlat=56.15263055&zoom=16',
                'name': 'Rådhuspladsen 2, 4., 8000 Aarhus C',
                'uuid': 'ae95777c-7ec1-4039-8025-e2ecce5099fb',
                'validity': {
                    'from': '2015-01-01T00:00:00+01:00', 'to': None,
                },
            },
            {
                'address_type': phone_class,
                'href': 'tel:+4533369696',
                'name': '3336 9696',
                'urn': 'urn:magenta.dk:telefon:+4533369696',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                },
            },
        ]

        with self.subTest('resulting addresses'):
            self.assertRequestResponse(
                '/service/e/{}/details/address?validity=past'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address?validity=future'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address'.format(userid),
                addresses,
            )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            addresses,
        )

        with self.subTest('underlying storage'):
            edited = c.bruger.get(userid)

            self.assertEqual(len(edited['relationer']['adresser']),
                             len(addresses))

            self.assertEqual(
                [
                    {
                        'uuid': 'ae95777c-7ec1-4039-8025-e2ecce5099fb',
                        'virkning': {
                            'to_included': False,
                            'to': 'infinity',
                            'from_included': True, 'from':
                            '2015-01-01 00:00:00+01',
                        },
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                    {
                        'virkning': {
                            'to_included': False,
                            'to': 'infinity',
                            'from_included': True,
                            'from': '2014-01-01 00:00:00+01',
                        },
                        'urn': 'urn:mailto:hest@example.com',
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    {
                        'virkning': {
                            'to_included': False,
                            'to': 'infinity',
                            'from_included': True,
                            'from': '2016-01-01 00:00:00+01',
                        },
                        'urn': 'urn:magenta.dk:telefon:+4533369696',
                        'objekttype':
                        '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                    },
                    {
                        'virkning': {
                            'to_included': False,
                            'to': 'infinity',
                            'from_included': True,
                            'from': '1934-06-09 00:00:00+01',
                        },
                        'urn': 'urn:mailto:bruger@example.com',
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    {
                        'virkning': {
                            'to_included': False,
                            'to': 'infinity',
                            'from_included': True,
                            'from': '2013-01-01 00:00:00+01',
                        },
                        'urn': 'urn:magenta.dk:ean:1234567890',
                        'objekttype': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                    },
                ],
                edited['relationer']['adresser'])

    def test_employee_add_first_address(self, mock):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        address_class = {
            'example': '<UUID>',
            'name': 'Adresse',
            'scope': 'DAR',
            'user_key': 'Adresse',
            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
        }

        userid = util.load_fixture('organisation/bruger',
                                   'create_bruger_fætterguf.json')

        original = c.bruger.get(userid)

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/e/{}/details/address?validity=past'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/address?validity=future'.format(userid),
                [],
            )

            self.assertNotIn('adresser', original['relationer'])

        self.assertRequestResponse(
            '/service/e/{}/create'.format(userid),
            userid,
            json=[
                {
                    "type": "address",
                    "address_type": address_class,
                    "uuid": '606cf42e-9dc2-4477-bf70-594830fcbdec',
                    "validity": {
                        "from": "2013-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ])

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [
                {
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 1., 8200 Aarhus N',
                    'address_type': {
                        'scope': 'DAR',
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'user_key': 'Adresse',
                    },
                    'validity': {
                        'to': None,
                        'from': '2013-01-01T00:00:00+01:00',
                    },
                    'uuid': '606cf42e-9dc2-4477-bf70-594830fcbdec',
                }
            ],
        )

    def test_edit_address(self, mock):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        email_class = {
            'example': 'test@example.com',
            'name': 'Emailadresse',
            'scope': 'EMAIL',
            'user_key': 'Email',
            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
        }

        address_class = {
            'example': '<UUID>',
            'name': 'Adresse',
            'scope': 'DAR',
            'user_key': 'Adresse',
            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
        }

        address_classes = self.client.get(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
            '/f/address_type/',
        ).json

        self.assertIn(email_class, address_classes['data']['items'])
        self.assertIn(address_class, address_classes['data']['items'])

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [
                {
                    'address_type': email_class,
                    'href': 'mailto:bruger@example.com',
                    'name': 'bruger@example.com',
                    'urn': 'urn:mailto:bruger@example.com',
                    'validity': {
                        'from': '1934-06-09T00:00:00+01:00',
                        'to': None,
                    },
                },
            ],
        )

        with self.subTest('bad edits'):
            self.assertRequestResponse(
                '/service/e/{}/edit'.format(userid),
                {
                    'error': True,
                    'cause': 'validation',
                    'description':
                    "invalid 'original', expected dict, got: null",
                    'status': 400,
                },
                status_code=400,
                json=[{
                    "type": "address",
                    # NB: no original!
                    "original": None,
                    "data": {
                        "validity": {
                            'to': '2010-01-01T00:00:00+01:00',
                        },
                    }
                }],
            )

            self.assertRequestResponse(
                '/service/e/{}/edit'.format(userid),
                {
                    'error': True,
                    'cause': 'validation',
                    'description': 'original entry not found!',
                    'status': 400,
                },
                status_code=400,
                json=[{
                    "type": "address",
                    "original": {
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        # wrong!
                        'href': 'mailto:user@example.com',
                        'name': 'user@example.com',
                        'urn': 'urn:mailto:user@example.com',
                        'validity': {
                            'from': '1934-06-09T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    "data": {
                        "validity": {
                            'to': '2010-01-01T00:00:00+01:00',
                        },
                    }
                }],
            )

        # first, test editing the value & the end time
        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid,
            json=[{
                "type": "address",
                "original": {
                    'address_type': {
                        'example': 'test@example.com',
                        'name': 'Emailadresse',
                        'scope': 'EMAIL',
                        'user_key': 'Email',
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    'href': 'mailto:bruger@example.com',
                    'name': 'bruger@example.com',
                    'urn': 'urn:mailto:bruger@example.com',
                    'validity': {
                        'from': '1934-06-09T00:00:00+01:00',
                        'to': None,
                    },
                },
                "data": {
                    'value': 'user@example.com',
                    "validity": {
                        'to': '2010-01-01T00:00:00+01:00',
                    },
                }
            }],
        )

        # verify our edit
        self.assertRequestResponse(
            '/service/e/{}/details/address?validity=past'.format(userid),
            [
                {
                    'address_type': email_class,
                    'href': 'mailto:user@example.com',
                    'name': 'user@example.com',
                    'urn': 'urn:mailto:user@example.com',
                    'validity': {
                        'from': '1934-06-09T00:00:00+01:00',
                        'to': '2010-01-01T00:00:00+01:00',
                    },
                },
            ],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address?validity=future'.format(userid),
            [],
        )

        # second, test editing type, value, and removing the end date
        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid,
            json=[{
                "type": "address",
                "original": {
                    'address_type': {
                        'example': 'test@example.com',
                        'name': 'Emailadresse',
                        'scope': 'EMAIL',
                        'user_key': 'Email',
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    'href': 'mailto:user@example.com',
                    'name': 'user@example.com',
                    'urn': 'urn:mailto:user@example.com',
                    'validity': {
                        'from': '1934-06-09T00:00:00+01:00',
                        'to': '2010-01-01T00:00:00+01:00',
                    },
                },
                "data": {
                    'address_type': address_class,
                    'uuid': '0a3f50a0-23c9-32b8-e044-0003ba298018',
                    'validity': {
                        'to': None,
                    },
                }
            }],
        )

        # verify the result
        self.assertRequestResponse(
            '/service/e/{}/details/address?validity=past'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [
                {
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'Adresse',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=12.57924839&mlat=55.68113676&zoom=16',
                    'name': 'Pilestræde 43, 3., 1112 København K',
                    'uuid': '0a3f50a0-23c9-32b8-e044-0003ba298018',
                    'validity': {
                        'from': '1934-06-09T00:00:00+01:00',
                        'to': None,
                    },
                },
            ],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address?validity=future'.format(userid),
            [],
        )

    def test_edit_untyped_address(self, mock):
        self.load_sample_structures()

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        email_class = {
            'example': 'test@example.com',
            'name': 'Emailadresse',
            'scope': 'EMAIL',
            'user_key': 'Email',
            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
        }

        address_class = {
            'example': '<UUID>',
            'name': 'Adresse',
            'scope': 'DAR',
            'user_key': 'Adresse',
            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
        }

        address_classes = self.client.get(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
            '/f/address_type/',
        ).json

        self.assertIn(email_class, address_classes['data']['items'])
        self.assertIn(address_class, address_classes['data']['items'])

        addresses = [
            {
                "address_type": {
                    "scope": "DAR"
                },
                "href": "https://www.openstreetmap.org/"
                "?mlon=12.58176945&mlat=55.67563739&zoom=16",
                "name": "Christiansborg Slotsplads 1, 1218 K\u00f8benhavn K",
                "uuid": "bae093df-3b06-4f23-90a8-92eabedb3622",
                "validity": {
                    "from": "1932-05-12T00:00:00+01:00",
                    "to": None
                }
            },
            {
                "address_type": email_class,
                "href": "mailto:goofy@example.com",
                "name": "goofy@example.com",
                "urn": "urn:mailto:goofy@example.com",
                "validity": {
                    "from": "1932-05-12T00:00:00+01:00",
                    "to": None
                }
            },
            {
                "address_type": email_class,
                "href": "mailto:goofy@example.com",
                "name": "goofy@example.com",
                "urn": "urn:mailto:goofy@example.com",
                "validity": {
                    "from": "1932-05-12T00:00:00+01:00",
                    "to": None
                }
            }
        ]

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            addresses,
        )

        # first, test editing the value only
        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid,
            json=[{
                "type": "address",
                "original": addresses[0],
                "data": {
                    'uuid': 'ae95777c-7ec1-4039-8025-e2ecce5099fb',
                }
            }],
        )

        addresses[0].update(
            uuid='ae95777c-7ec1-4039-8025-e2ecce5099fb',
            href='https://www.openstreetmap.org/'
            '?mlon=10.20320628&mlat=56.15263055&zoom=16',
            name='Rådhuspladsen 2, 4., 8000 Aarhus C',
        )

        # verify our edit
        self.assertRequestResponse(
            '/service/e/{}/details/address?validity=past'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            addresses,
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address?validity=future'.format(userid),
            [],
        )

        # second, test editing type
        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid,
            json=[{
                "type": "address",
                "original": addresses[0],
                "data": {
                    'address_type': address_class,
                }
            }],
        )

        addresses[0].update(
            address_type=address_class,
        )

        # verify the result
        self.assertRequestResponse(
            '/service/e/{}/details/address?validity=past'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            addresses,
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address?validity=future'.format(userid),
            [],
        )

    def test_create_unit_address(self, mock):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

        address_rels = [
            {
                'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False,
                },
            },
            {
                'objekttype': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                'urn': 'urn:magenta.dk:ean:5798000420229',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False,
                },
            },
            {
                'objekttype': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                'urn': 'urn:magenta.dk:telefon:+4587150000',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'from_included': True,
                    'to': 'infinity',
                    'to_included': False,

                },
            },
        ]

        addresses = [
            {
                'address_type': {
                    'example': '5712345000014',
                    'name': 'EAN',
                    'scope': 'EAN',
                    'user_key': 'EAN',
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'href': None,
                'name': '5798000420229',
                'urn': 'urn:magenta.dk:ean:5798000420229',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                },
            },
            {
                'address_type': {
                    'example': '20304060',
                    'name': 'Telefonnummer',
                    'scope': 'PHONE',
                    'user_key': 'Telefon',
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                'href': 'tel:+4587150000',
                'name': '8715 0000',
                'urn': 'urn:magenta.dk:telefon:+4587150000',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                },
            },
            {
                'address_type': {
                    'example': '<UUID>',
                    'name': 'Adresse',
                    'scope': 'DAR',
                    'user_key': 'Adresse',
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                },
                'href': 'https://www.openstreetmap.org/'
                '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                },
            },
        ]

        email_class = {
            'example': 'test@example.com',
            'name': 'Emailadresse',
            'scope': 'EMAIL',
            'user_key': 'Email',
            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
        }

        address_class = {
            'example': '<UUID>',
            'name': 'Adresse',
            'scope': 'DAR',
            'user_key': 'Adresse',
            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
        }

        original = c.organisationenhed.get(unitid)

        # PRECONDITIONS
        self.assertIn(
            email_class,
            self.client.get(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/f/address_type/',
            ).json['data']['items'],
        )

        self.assertIn(
            address_class,
            self.client.get(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/f/address_type/',
            ).json['data']['items'],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address?validity=past'.format(unitid),
            [],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            addresses,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address?validity=future'.format(unitid),
            [],
        )

        self.assertEqual(address_rels, original['relationer']['adresser'])

        # ERROR CHECKING

        with self.subTest('errors'):
            self.assertRequestResponse(
                '/service/ou/{}/create'.format(unitid),
                {
                    'error': True,
                    'cause': 'validation',
                    'description': "missing 'value'",
                    'status': 400,
                },
                status_code=400,
                json=[
                    {
                        "type": "address",
                        "address_type": email_class,
                        # NB: no value
                        "validity": {
                            "from": "2013-01-01T00:00:00+01:00",
                            "to": None,
                        },
                    },
                ],
            )

        with self.subTest('errors II'):
            self.assertRequestResponse(
                '/service/ou/{}/create'.format(unitid),
                {
                    'error': True,
                    'cause': 'validation',
                    'description': (
                        "invalid 'address_type', expected dict, got: null"
                    ),
                    'status': 400,
                },
                status_code=400,
                json=[
                    {
                        "type": "address",
                        # NB: no type!
                        "address_type": None,
                        "value": "hallo@exmaple.com",
                        "validity": {
                            "from": "2013-01-01T00:00:00+01:00",
                            "to": None,
                        },
                    },
                ],
            )

        with self.subTest('errors III'):
            self.assertRequestResponse(
                '/service/ou/{}/create'.format(unitid),
                {
                    'error': True,
                    'cause': 'validation',
                    'description': "missing 'uuid'",
                    'status': 400,
                },
                status_code=400,
                json=[
                    {
                        "type": "address",
                        "address_type": address_class,
                        # NB: wrong key!
                        "value": "hallo@exmaple.com",
                        "validity": {
                            "from": "2013-01-01T00:00:00+01:00",
                            "to": None,
                        },
                    },
                ],
            )

        with self.subTest('errors IV'):
            self.assertRequestResponse(
                '/service/ou/{}/create'.format(unitid),
                {
                    'error': True,
                    'cause': 'validation',
                    'description': (
                        "invalid uuid for 'uuid': 'hallo@exmaple.com'"
                    ),
                    'status': 400,
                },
                status_code=400,
                json=[
                    {
                        "type": "address",
                        "address_type": address_class,
                        # NB: not a UUID!
                        "uuid": "hallo@exmaple.com",
                        "validity": {
                            "from": "2013-01-01T00:00:00+01:00",
                            "to": None,
                        },
                    },
                ],
            )

        # NOW CREATE IT

        self.assertRequestResponse(
            '/service/ou/{}/create'.format(unitid),
            unitid,
            json=[
                {
                    "type": "address",
                    "address_type": email_class,
                    "value": "hallo@exmaple.com",
                    "validity": {
                        "from": "2013-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ])

        address_rels.append({
            'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
            'urn': 'urn:mailto:hallo@exmaple.com',
            'virkning': {
                'from': '2013-01-01 00:00:00+01',
                'from_included': True,
                'to': 'infinity',
                'to_included': False,
            },
        })

        original = c.organisationenhed.get(unitid)

        self.assertEqual(address_rels, original['relationer']['adresser'])

    @unittest.mock.patch('uuid.uuid4',
                         new=lambda: '00000000-0000-0000-0000-000000000000')
    def test_create_org_unit(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        payload = {
            "name": "Fake Corp",
            "parent": {
                'uuid': "2874e1dc-85e6-4269-823a-e1125484dfd3"
            },
            "org_unit_type": {
                'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
            },
            "addresses": [
                {
                    "address_type": {
                        "example": "20304060",
                        "name": "Telefonnummer",
                        "scope": "PHONE",
                        "user_key": "Telefon",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                    },
                    "value": "11 22 33 44",
                    "validity": {
                        "from": "2015-02-04T00:00:00+01",
                        "to": "2017-10-22T00:00:00+02",
                    }
                },
                {
                    "address_type": {
                        "example": "<UUID>",
                        "name": "Adresse",
                        "scope": "DAR",
                        "user_key": "Adresse",
                        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                    },
                    "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
            ],
            "validity": {
                "from": "2010-02-04T00:00:00+01",
                "to": "2017-10-22T00:00:00+02",
            }
        }

        r = self._perform_request('/service/ou/create', json=payload)
        unitid = r.json

        address_rels = [
            {
                'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                'virkning': {
                    'from': '2010-02-04 00:00:00+01',
                    'to_included': False,
                    'to': '2017-10-22 00:00:00+02',
                    'from_included': True,
                },
            },
            {
                'virkning': {
                    'from': '2015-02-04 00:00:00+01',
                    'to_included': False,
                    'to': '2017-10-22 00:00:00+02',
                    'from_included': True,
                },
                'objekttype': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                'urn': 'urn:magenta.dk:telefon:+4511223344',
            },
        ]

        self.assertEqual(
            address_rels,
            c.organisationenhed.get(unitid)['relationer']['adresser'],
        )

        self.assertRequestResponse(
            '/service/ou/{}/'.format(unitid),
            {
                'name': 'Fake Corp',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'org_unit_type': {
                    'example': None,
                    'name': 'Institut',
                    'scope': None,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'parent': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                },
                'user_key': 'Fake Corp 00000000-0000-0000-0000-000000000000',
                'uuid': unitid,
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/'.format(unitid),
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

        self.assertRequestResponse(
            '/service/ou/{}/details/address?validity=past'.format(unitid),
            [],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            [
                {
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'Adresse',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'validity': {
                        'from': '2010-02-04T00:00:00+01:00',
                        'to': '2017-10-22T00:00:00+02:00',
                    },
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                },
                {
                    'address_type': {
                        'example': '20304060',
                        'name': 'Telefonnummer',
                        'scope': 'PHONE',
                        'user_key': 'Telefon',
                        'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                    },
                    'href': 'tel:+4511223344',
                    'name': '1122 3344',
                    'validity': {
                        'from': '2015-02-04T00:00:00+01:00',
                        'to': '2017-10-22T00:00:00+02:00',
                    },
                    'urn': 'urn:magenta.dk:telefon:+4511223344',
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address?validity=future'.format(unitid),
            [],
        )

        self.assertEqual(
            address_rels,
            c.organisationenhed.get(unitid)['relationer']['adresser'],
        )

    def test_edit_org_unit_overwrite(self, mock):
        self.load_sample_structures()

        unitid = '04c78fc2-72d2-4d02-b55f-807af19eac48'

        orig_address = {
            "href": "https://www.openstreetmap.org/"
            "?mlon=10.19938084&mlat=56.17102843&zoom=16",
            "name": "Nordre Ringgade 1, 8000 Aarhus C",
            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
            "address_type": {
                "example": "<UUID>",
                "name": "Adresse",
                "scope": "DAR",
                "user_key": "Adresse",
                "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
            },
            "validity": {
                "from": "2016-01-01T00:00:00+01:00",
                "to": "2019-01-01T00:00:00+01:00",
            },
        }

        new_address_type = {
            'example': '20304060',
            'name': 'Telefonnummer',
            'scope': 'PHONE',
            'user_key': 'Telefon',
            'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
        }

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            [orig_address],
        )

        with self.subTest('errors'):
            self.assertRequestResponse(
                '/service/ou/{}/edit'.format(unitid),
                {
                    'error': True,
                    'cause': 'validation',
                    'description': "missing 'value'",
                    'status': 400,
                },
                status_code=400,
                json=[
                    {
                        "type": "address",
                        "original": orig_address,
                        "data": {
                            "address_type": new_address_type,
                            # NB: no value
                        },
                    },
                ],
            )

        self.assertRequestResponse(
            '/service/ou/{}/edit'.format(unitid),
            unitid,
            json=[
                {
                    "type": "address",
                    "original": orig_address,
                    "data": {
                        "address_type": new_address_type,
                        'value': '87150000',
                    },
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            [{
                'address_type': new_address_type,
                'href': 'tel:+4587150000',
                'name': '8715 0000',
                'urn': 'urn:magenta.dk:telefon:+4587150000',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00',
                    'to': '2019-01-01T00:00:00+01:00',
                },
            }],
        )

    def test_add_org_unit_address(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = '2874e1dc-85e6-4269-823a-e1125484dfd3'

        address_rels = [
            {
                'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'to': 'infinity',
                    'from_included': True,
                    'to_included': False,
                },
            },
            {
                'objekttype': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                'urn': 'urn:magenta.dk:ean:5798000420229',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'to': 'infinity',
                    'from_included': True,
                    'to_included': False,
                },
            },
            {
                'objekttype': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                'urn': 'urn:magenta.dk:telefon:+4587150000',
                'virkning': {
                    'from': '2016-01-01 00:00:00+01',
                    'to': 'infinity',
                    'from_included': True,
                    'to_included': False,
                },
            },
        ]

        addresses = [
            {
                'address_type': {
                    'example': '5712345000014',
                    'name': 'EAN',
                    'scope': 'EAN',
                    'user_key': 'EAN',
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'href': None,
                'name': '5798000420229',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                },
                'urn': 'urn:magenta.dk:ean:5798000420229',
            },
            {
                'address_type': {
                    'example': '20304060',
                    'name': 'Telefonnummer',
                    'scope': 'PHONE',
                    'user_key': 'Telefon',
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                'href': 'tel:+4587150000',
                'name': '8715 0000',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                },
                'urn': 'urn:magenta.dk:telefon:+4587150000',
            },
            {
                'address_type': {
                    'example': '<UUID>',
                    'name': 'Adresse',
                    'scope': 'DAR',
                    'user_key': 'Adresse',
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                },
                'href': 'https://www.openstreetmap.org/'
                '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                'validity': {
                    'from': '2016-01-01T00:00:00+01:00', 'to': None,
                },
                'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
            },
        ]

        with self.subTest('sanity check'):
            self.assertRequestResponse(
                '/service/ou/{}/details/address'
                '?validity=past'.format(unitid),
                [],
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/address'.format(unitid),
                addresses,
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/address'
                '?validity=future'.format(unitid),
                [],
            )

            self.assertEqual(
                address_rels,
                c.organisationenhed.get(unitid)['relationer']['adresser'],
            )

        self.assertRequestResponse(
            '/service/ou/{}/create'.format(unitid),
            unitid,
            json=[
                {
                    "type": "address",
                    'address_type': {
                        'example': 'test@example.com',
                        'name': 'Emailadresse',
                        'scope': 'EMAIL',
                        'user_key': 'Email',
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    'value': 'root@example.com',
                    "validity": {
                        "from": "2017-01-01T00:00:00+01",
                    },
                },
            ],
        )

        address_rels.append({
            'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
            'urn': 'urn:mailto:root@example.com',
            'virkning': {
                'from': '2017-01-01 00:00:00+01',
                'to': 'infinity',
                'from_included': True,
                'to_included': False,
            },
        })

        addresses.append({
            'address_type': {
                'example': 'test@example.com',
                'name': 'Emailadresse',
                'scope': 'EMAIL',
                'user_key': 'Email',
                'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
            },
            'href': 'mailto:root@example.com',
            'name': 'root@example.com',
            'validity': {
                'from': '2017-01-01T00:00:00+01:00',
                'to': None,
            },
            'urn': 'urn:mailto:root@example.com',
        })

        self.assertEqual(
            address_rels,
            c.organisationenhed.get(unitid)['relationer']['adresser'],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            addresses,
        )

    def test_edit_org_unit_address_overwrite(self, mock):
        self.load_sample_structures()

        unitid = '85715fc7-925d-401b-822d-467eb4b163b6'

        addresses = [
            {
                "address_type": {
                    "example": "20304060",
                    "name": "Telefonnummer",
                    "scope": "PHONE",
                    "user_key": "Telefon",
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
                },
                "href": "tel:+4587150000",
                "name": "8715 0000",
                "validity": {
                    "from": "2016-01-01T00:00:00+01:00",
                    "to": None
                },
                "urn": "urn:magenta.dk:telefon:+4587150000"
            },
            {
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "Adresse",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                },
                "href": "https://www.openstreetmap.org/"
                "?mlon=10.19938084&mlat=56.17102843&zoom=16",
                "name": "Nordre Ringgade 1, 8000 Aarhus C",
                "validity": {
                    "from": "2016-01-01T00:00:00+01:00",
                    "to": None
                },
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197"
            }
        ]

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/ou/{}/details/address'.format(unitid),
                addresses,
            )

        req = [
            {
                "type": "address",
                "original": addresses[1],
                "data": {
                    "uuid": "d901ff7e-8ad9-4581-84c7-5759aaa82f7b",
                    "validity": {
                        'from': '2016-06-01',
                    },
                }
            },
        ]

        self.assertRequestResponse(
            '/service/ou/{}/edit'.format(unitid),
            unitid, json=req)

        addresses[1]['validity']['from'] = '2016-06-01T00:00:00+02:00'
        addresses[1].update(
            name='Nordre Ringgade 2, 8000 Aarhus C',
            uuid='d901ff7e-8ad9-4581-84c7-5759aaa82f7b',
            href=(
                'https://www.openstreetmap.org/'
                '?mlon=10.20019416&mlat=56.17063452&zoom=16'
            ),
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            addresses,
        )

    def test_edit_org_unit_address(self, mock):
        self.load_sample_structures()

        unitid = '85715fc7-925d-401b-822d-467eb4b163b6'

        addresses = [
            {
                "address_type": {
                    "example": "20304060",
                    "name": "Telefonnummer",
                    "scope": "PHONE",
                    "user_key": "Telefon",
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
                },
                "href": "tel:+4587150000",
                "name": "8715 0000",
                "validity": {
                    "from": "2016-01-01T00:00:00+01:00",
                    "to": None
                },
                "urn": "urn:magenta.dk:telefon:+4587150000"
            },
            {
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "Adresse",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                },
                "href": "https://www.openstreetmap.org/"
                "?mlon=10.19938084&mlat=56.17102843&zoom=16",
                "name": "Nordre Ringgade 1, 8000 Aarhus C",
                "validity": {
                    "from": "2016-01-01T00:00:00+01:00",
                    "to": None
                },
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197"
            }
        ]

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/ou/{}/details/address'.format(unitid),
                addresses,
            )

        req = [
            {
                "type": "address",
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "Adresse",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                },
                "uuid": "d901ff7e-8ad9-4581-84c7-5759aaa82f7b",
                "validity": {
                    'from': '2016-06-01',
                },
            },
        ]

        self.assertRequestResponse(
            '/service/ou/{}/create'.format(unitid),
            unitid, json=req)

        addresses.append({
            'address_type': {
                'example': '<UUID>',
                'name': 'Adresse',
                'scope': 'DAR',
                'user_key': 'Adresse',
                'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
            },
            'href': 'https://www.openstreetmap.org/'
            '?mlon=10.20019416&mlat=56.17063452&zoom=16',
            'name': 'Nordre Ringgade 2, 8000 Aarhus C',
            'validity': {'from': '2016-06-01T00:00:00+02:00', 'to': None},
            'uuid': 'd901ff7e-8ad9-4581-84c7-5759aaa82f7b',
        })

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            addresses,
        )


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@util.mock('dawa-addresses.json', allow_mox=True)
class Reading(util.LoRATestCase):

    def test_reading(self, mock):
        self.load_sample_structures(minimal=True)

        with self.subTest('missing classes'):
            with self.assertLogs(self.app.logger, logging.ERROR) as log_res:
                self.assertRequestResponse(
                    '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                    '/details/address',
                    [],
                )

            self.assertRegex(log_res.output[0],
                             r"^ERROR:mora.app:AN ERROR OCCURRED in '[^']*': "
                             "invalid address relation")

        self.load_sample_structures(minimal=False)

        with self.subTest('present I'):
            self.assertRequestResponse(
                '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
                '/details/address?validity=present',
                [
                    {
                        'address_type': {
                            'scope': 'DAR',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=12.58176945&mlat=55.67563739&zoom=16',
                        'name':
                        'Christiansborg Slotsplads 1, 1218 København K',
                        'uuid': 'bae093df-3b06-4f23-90a8-92eabedb3622',
                        'validity': {
                            'from': '1932-05-12T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'href': 'mailto:goofy@example.com',
                        'name': 'goofy@example.com',
                        'urn': 'urn:mailto:goofy@example.com',
                        'validity': {
                            'from': '1932-05-12T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'href': 'mailto:goofy@example.com',
                        'name': 'goofy@example.com',
                        'urn': 'urn:mailto:goofy@example.com',
                        'validity': {
                            'from': '1932-05-12T00:00:00+01:00',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('present II'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/address?validity=present',
                [
                    {
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'href': 'mailto:bruger@example.com',
                        'name': 'bruger@example.com',
                        'urn': 'urn:mailto:bruger@example.com',
                        'validity': {
                            'from': '1934-06-09T00:00:00+01:00',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('present III'):
            self.assertRequestResponse(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
                '/details/address?validity=present',
                [
                    {
                        'address_type': {
                            'example': '5712345000014',
                            'name': 'EAN',
                            'scope': 'EAN',
                            'user_key': 'EAN',
                            'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                        },
                        'href': None,
                        'name': '5798000420229',
                        'urn': 'urn:magenta.dk:ean:5798000420229',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': '20304060',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                        },
                        'href': 'tel:+4587150000',
                        'name': '8715 0000',
                        'urn': 'urn:magenta.dk:telefon:+4587150000',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': None,
                        }
                    },
                ],
            )

        with self.subTest('present IV'):
            self.assertRequestResponse(
                '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
                '/details/address?validity=present',
                [
                    {
                        'address_type': {
                            'example': '20304060',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                        },
                        'href': 'tel:+4587150000',
                        'name': '8715 0000',
                        'urn': 'urn:magenta.dk:telefon:+4587150000',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('present V'):
            self.assertRequestResponse(
                '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
                '/details/address?validity=present',
                [
                    {
                        'address_type': {
                            'example': '20304060',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                        },
                        'href': 'tel:+4587150000',
                        'name': '8715 0000',
                        'urn': 'urn:magenta.dk:telefon:+4587150000',
                        'validity': {
                            'from': '2017-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'validity': {
                            'from': '2017-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('present VI'):
            self.assertRequestResponse(
                '/service/ou/85715fc7-925d-401b-822d-467eb4b163b6'
                '/details/address?validity=present',
                [
                    {
                        'address_type': {
                            'example': '20304060',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                        },
                        'href': 'tel:+4587150000',
                        'name': '8715 0000',
                        'urn': 'urn:magenta.dk:telefon:+4587150000',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('present VII'):
            self.assertRequestResponse(
                '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/details/address?validity=present',
                [
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'validity': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': '2019-01-01T00:00:00+01:00',
                        },
                    },
                ],
            )

        with self.subTest('past I'):
            self.assertRequestResponse(
                '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
                '/details/address?validity=past',
                [],
            )

        with self.subTest('past II'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/address?validity=past',
                [],
            )

        with self.subTest('past III'):
            self.assertRequestResponse(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
                '/details/address?validity=past',
                [],
            )

        with self.subTest('past IV'):
            self.assertRequestResponse(
                '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
                '/details/address?validity=past',
                [],
            )

        with self.subTest('past V'):
            self.assertRequestResponse(
                '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
                '/details/address?validity=past',
                [],
            )

        with self.subTest('past VI'):
            self.assertRequestResponse(
                '/service/ou/85715fc7-925d-401b-822d-467eb4b163b6'
                '/details/address?validity=past',
                [],
            )

        with self.subTest('past VII'):
            self.assertRequestResponse(
                '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/details/address?validity=past',
                [],
            )

        with self.subTest('future I'):
            self.assertRequestResponse(
                '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
                '/details/address?validity=future',
                [],
            )

        with self.subTest('future II'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/address?validity=future',
                [],
            )

        with self.subTest('future III'):
            self.assertRequestResponse(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
                '/details/address?validity=future',
                [],
            )

        with self.subTest('future IV'):
            self.assertRequestResponse(
                '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
                '/details/address?validity=future',
                [],
            )

        with self.subTest('future V'):
            self.assertRequestResponse(
                '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
                '/details/address?validity=future',
                [],
            )

        with self.subTest('future VI'):
            self.assertRequestResponse(
                '/service/ou/85715fc7-925d-401b-822d-467eb4b163b6'
                '/details/address?validity=future',
                [],
            )

        with self.subTest('future VII'):
            self.assertRequestResponse(
                '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/details/address?validity=future',
                [],
            )

        with self.subTest('proper past'):
            with freezegun.freeze_time('2020-01-01'):
                self.assertRequestResponse(
                    '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
                    '/details/address?validity=past',
                    [
                        {
                            'address_type': {
                                'example': '<UUID>',
                                'name': 'Adresse',
                                'scope': 'DAR',
                                'user_key': 'Adresse',
                                'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                            },
                            'href': 'https://www.openstreetmap.org/'
                            '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                            'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                            'uuid':
                            'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                            'validity': {
                                'from': '2016-01-01T00:00:00+01:00',
                                'to': '2019-01-01T00:00:00+01:00',
                            },
                        },
                    ],
                )
