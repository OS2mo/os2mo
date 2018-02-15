#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest
import copy

import freezegun

from mora import lora
from tests import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Writing(util.LoRATestCase):
    maxDiff = None

    def test_employee_address(self):
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
                'from': '2002-02-14T00:00:00+01:00',
                'href': 'mailto:bruger@example.com',
                'pretty_value': 'bruger@example.com',
                'raw_value': 'urn:mailto:bruger@example.com',
                'to': None,
            }
        ]

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/f/address_type/',
                [address_class, ean_class, email_class, phone_class]
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
                    "address": 1234567890,
                    "validity": {
                        "from": "2013-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ])

        edited = c.bruger.get(userid)

        self.assertNotEqual(original, edited)

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

        addresses[:0] = [
            {
                'address_type': {
                    'example': '5712345000014',
                    'name': 'EAN',
                    'scope': 'EAN',
                    'user_key': 'EAN',
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'from': '2013-01-01T00:00:00+01:00',
                'href': None,
                'pretty_value': '1234567890',
                'raw_value': 'urn:magenta.dk:ean:1234567890',
                'to': None,
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
                    "address": "hest@example.com",
                    "validity": {
                        "from": "2014-01-01T00:00:00+01",
                    },
                },
                {
                    "type": "address",
                    "address_type": address_class,
                    "address": "ae95777c-7ec1-4039-8025-e2ecce5099fb",
                    "validity": {
                        "from": "2015-01-01T00:00:00+01",
                    },
                },
                {
                    "type": "address",
                    "address_type": phone_class,
                    "address": 33369696,
                    "validity": {
                        "from": "2016-01-01T00:00:00+01",
                    },
                },
            ],
        )

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
                [
                    {
                        'address_type': {
                            'example': '5712345000014',
                            'name': 'EAN',
                            'scope': 'EAN',
                            'user_key': 'EAN',
                            'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                        },
                        'from': '2013-01-01T00:00:00+01:00',
                        'href': None,
                        'pretty_value': '1234567890',
                        'raw_value': 'urn:magenta.dk:ean:1234567890',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': '20304060',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                        },
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': 'tel:+4533369696',
                        'pretty_value': 33369696,
                        'raw_value': 'urn:magenta.dk:telefon:+4533369696',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'from': '2015-01-01T00:00:00+01:00',
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.20320628&mlat=56.15263055&zoom=16',
                        'pretty_value': 'Rådhuspladsen 2, 4., 8000 Aarhus C',
                        'raw_value': 'ae95777c-7ec1-4039-8025-e2ecce5099fb',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'from': '2002-02-14T00:00:00+01:00',
                        'href': 'mailto:bruger@example.com',
                        'pretty_value': 'bruger@example.com',
                        'raw_value': 'urn:mailto:bruger@example.com',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'from': '2014-01-01T00:00:00+01:00',
                        'href': 'mailto:hest@example.com',
                        'pretty_value': 'hest@example.com',
                        'raw_value': 'urn:mailto:hest@example.com',
                        'to': None,
                    },
                ],
            )

        with self.subTest('underlying storage'):
            edited = c.bruger.get(userid)

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
                            'from': '2002-02-14 00:00:00+01',
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

    @unittest.expectedFailure
    def test_create_unit_address(self):
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
                'pretty_value': '5798000420229',
                'raw_value': 'urn:magenta.dk:ean:5798000420229',
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
                'pretty_value': 87150000,
                'raw_value': 'urn:magenta.dk:telefon:+4587150000',
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
                'pretty_value': 'Nordre Ringgade 1, 8000 Aarhus C',
                'raw_value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
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

        original = c.organisationenhed.get(unitid)

        # PRECONDITIONS
        self.assertIn(
            email_class,
            self.client.get(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/f/address_type/',
            ).json,
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

        self.assertEqual(original['relationer']['adresser'], address_rels)

        # NOW CREATE IT

        self.assertRequestResponse(
            '/service/ou/{}/create'.format(unitid),
            unitid,
            json=[
                {
                    "type": "address",
                    "address_type": email_class,
                    "address": "hallo@exmaple.com",
                    "validity": {
                        "from": "2013-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ])

        original = c.organisationenhed.get(unitid)

        self.assertEqual(original['relationer']['adresser'], address_rels)

@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Reading(util.LoRATestCase):

    def test_reading_present(self):
        self.load_sample_structures()

        with self.subTest('present I'):
            self.assertRequestResponse(
                '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
                '/details/address?validity=present',
                [
                    {
                        'address_type': {
                            'scope': 'DAR',
                        },
                        'from': '2002-02-14T00:00:00+01:00',
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=12.58176945&mlat=55.67563739&zoom=16',
                        'pretty_value':
                        'Christiansborg Slotsplads 1, 1218 København K',
                        'raw_value': 'bae093df-3b06-4f23-90a8-92eabedb3622',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'from': '2002-02-14T00:00:00+01:00',
                        'href': 'mailto:goofy@example.com',
                        'pretty_value': 'goofy@example.com',
                        'raw_value': 'urn:mailto:goofy@example.com',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'from': '2002-02-14T00:00:00+01:00',
                        'href': 'mailto:goofy@example.com',
                        'pretty_value': 'goofy@example.com',
                        'raw_value': 'urn:mailto:goofy@example.com',
                        'to': None,
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
                        'from': '2002-02-14T00:00:00+01:00',
                        'href': 'mailto:bruger@example.com',
                        'pretty_value': 'bruger@example.com',
                        'raw_value': 'urn:mailto:bruger@example.com',
                        'to': None,
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
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': None,
                        'pretty_value': '5798000420229',
                        'raw_value': 'urn:magenta.dk:ean:5798000420229',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': '20304060',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                        },
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': 'tel:+4587150000',
                        'pretty_value': 87150000,
                        'raw_value': 'urn:magenta.dk:telefon:+4587150000',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'pretty_value': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'raw_value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'to': None,
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
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': 'tel:+4587150000',
                        'pretty_value': 87150000,
                        'raw_value': 'urn:magenta.dk:telefon:+4587150000',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'pretty_value': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'raw_value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'to': None,
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
                        'from': '2017-01-01T00:00:00+01:00',
                        'href': 'tel:+4587150000',
                        'pretty_value': 87150000,
                        'raw_value': 'urn:magenta.dk:telefon:+4587150000',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'from': '2017-01-01T00:00:00+01:00',
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'pretty_value': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'raw_value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'to': None,
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
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': 'tel:+4587150000',
                        'pretty_value': 87150000,
                        'raw_value': 'urn:magenta.dk:telefon:+4587150000',
                        'to': None,
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'Adresse',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'pretty_value': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'raw_value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'to': None,
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
                        'from': '2016-01-01T00:00:00+01:00',
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                        'pretty_value': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'raw_value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'to': '2019-01-01T00:00:00+01:00',
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
                            'from': '2016-01-01T00:00:00+01:00',
                            'href': 'https://www.openstreetmap.org/'
                            '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                            'pretty_value': 'Nordre Ringgade 1, 8000 Aarhus C',
                            'raw_value':
                            'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                            'to': '2019-01-01T00:00:00+01:00',
                        },
                    ],
                )
