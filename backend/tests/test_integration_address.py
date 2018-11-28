#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy
import logging
import re
import unittest.mock

import freezegun

from mora import lora
from tests import util

address_class = {
    'example': '<UUID>',
    'name': 'Adresse',
    'scope': 'DAR',
    'user_key': 'AdressePost',
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


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@util.mock('dawa-addresses.json', allow_mox=True)
class Writing(util.LoRATestCase):
    maxDiff = None

    def test_new_ean_address(self, mock):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"

        functionid, = self.assertRequest(
            '/service/details/create',
            json=[
                {
                    "type": "address",
                    "address_type": ean_class,
                    "address": {
                        "value": '1234567890',
                    },
                    "person": {'uuid': userid},
                    "validity": {
                        "from": "2013-01-01",
                        "to": None,
                    },
                },
            ])

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        self.assertRegistrationsEqual(
            {
                "livscykluskode": "Opstaaet",
                "note": "Oprettet i MO",
                "attributter": {
                    "organisationfunktionegenskaber": [{
                        "brugervendtnoegle": "1234567890",
                        "funktionsnavn": "Adresse",
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        },
                    }],
                },
                "relationer": {
                    "adresser": [{
                        'objekttype': 'EAN',
                        'urn': 'urn:magenta.dk:ean:1234567890',
                        'virkning': {
                            'from': '2013-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    }],
                    "organisatoriskfunktionstype": [{
                        "uuid": ean_class['uuid'],
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        },
                    }],
                    "tilknyttedebrugere": [{
                        "uuid": userid,
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        },
                    }],
                    "tilknyttedeorganisationer": [{
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'virkning': {
                            'from': '2013-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    }],
                },
                "tilstande": {
                    "organisationfunktiongyldighed": [{
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        },
                    }],
                },
            },
            c.organisationfunktion.get(functionid),
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [
                {
                    'address': {
                        'href': None,
                        'name': '1234567890',
                        'urn': 'urn:magenta.dk:ean:1234567890',
                    },
                    'address_type': {
                        'example': '5712345000014',
                        'name': 'EAN',
                        'scope': 'EAN',
                        'user_key': 'EAN',
                        'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                    },
                    'org_unit': None,
                    'person': {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    'uuid': functionid,
                    'validity': {'from': '2013-01-01', 'to': None},
                },
            ],
        )

    def test_new_dar_address(self, mock):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"

        functionid, = self.assertRequest(
            '/service/details/create',
            json=[
                {
                    "type": "address",
                    "address_type": address_class,
                    "address": {
                        "uuid": '0a3f50a0-23c9-32b8-e044-0003ba298018',
                    },
                    "person": {'uuid': userid},
                    "validity": {
                        "from": "2013-01-01",
                        "to": None,
                    },
                },
            ])

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        self.assertRegistrationsEqual(
            {
                "livscykluskode": "Opstaaet",
                "note": "Oprettet i MO",
                "attributter": {
                    "organisationfunktionegenskaber": [{
                        "brugervendtnoegle":
                        "Pilestræde 43, 3., 1112 København K",
                        "funktionsnavn": "Adresse",
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }]
                },
                "relationer": {
                    "adresser": [{
                        "objekttype": "DAR",
                        "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }],
                    "organisatoriskfunktionstype": [{
                        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }],
                    "tilknyttedebrugere": [{
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }],
                    "tilknyttedeorganisationer": [{
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }]
                },
                "tilstande": {
                    "organisationfunktiongyldighed": [{
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "2013-01-01 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }]
                }
            },
            c.organisationfunktion.get(functionid),
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [{
                "address": {
                    "href": "https://www.openstreetmap.org/"
                    "?mlon=12.57924839&mlat=55.68113676&zoom=16",
                    "name": "Pilestræde 43, 3., 1112 København K",
                    "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018"
                },
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "AdressePost",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                },
                "org_unit": None,
                "person": {
                    "name": "Anders And",
                    "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
                },
                "uuid": functionid,
                "validity": {
                    "from": "2013-01-01",
                    "to": None
                }
            }],
        )

    def test_create_errors(self, mock):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"

        nothingid = "00000000-0000-0000-0000-000000000000"

        with self.subTest('neither failing'):
            req = [
                {
                    "type": "address",
                    "address_type": ean_class,
                    "value": '1234567890',
                    "validity": {
                        "from": "2013-01-01",
                        "to": None,
                    },
                },
            ]

            self.assertRequestResponse(
                '/service/details/create',
                {
                    'description':
                    'must specify only one of person and org_unit!',
                    'error': True,
                    'error_key': 'E_INVALID_INPUT',
                    'employee_uuid': None,
                    'org_unit_uuid': None,
                    'obj': req[0],
                    'status': 400,
                },
                json=req,
                status_code=400,
            )

        with self.subTest('both failing'):
            req = [
                {
                    "type": "address",
                    "address_type": ean_class,
                    "value": '1234567890',
                    "person": {
                        'uuid': userid,
                    },
                    "org_unit": {
                        'uuid': unitid,
                    },
                    "validity": {
                        "from": "2013-01-01",
                        "to": None,
                    },
                },
            ]

            self.assertRequestResponse(
                '/service/details/create',
                {
                    'description':
                    'must specify only one of person and org_unit!',
                    'error': True,
                    'error_key': 'E_INVALID_INPUT',
                    'employee_uuid': userid,
                    'org_unit_uuid': unitid,
                    'obj': req[0],
                    'status': 400,
                },
                json=req,
                status_code=400,
            )

        with self.subTest('no value'):
            req = [
                {
                    "type": "address",
                    "address_type": email_class,
                    "org_unit": {"uuid": unitid},
                    # NB: no value
                    "validity": {
                        "from": "2013-01-01",
                        "to": None,
                    },
                },
            ]

            self.assertRequestResponse(
                '/service/details/create',
                {
                    'error': True,
                    'error_key': 'V_MISSING_REQUIRED_VALUE',
                    'description': "Missing value",
                    'key': 'value',
                    'status': 400,
                    'obj': req[0],
                },
                status_code=400,
                json=req,
            )

        with self.subTest('no type'):
            req = [
                {
                    "type": "address",
                    # NB: no type!
                    "address_type": None,
                    "address": {
                        "value": "hallo@exmaple.com",
                    },
                    "org_unit": {"uuid": unitid},
                    "validity": {
                        "from": "2013-01-01",
                        "to": None,
                    },
                },
            ]

            self.assertRequestResponse(
                '/service/details/create',
                {
                    'error': True,
                    'error_key': 'E_INVALID_TYPE',
                    'description': (
                        "Invalid 'address_type', expected dict, got: null"
                    ),
                    'key': 'address_type',
                    'expected': 'dict',
                    'actual': None,
                    'status': 400,
                    "obj": req[0],
                },
                status_code=400,
                json=req,
            )

        with self.subTest('wrong key'):
            req = [
                {
                    "type": "address",
                    "address_type": address_class,
                    # NB: wrong key!
                    "address": {
                        "value": "hallo@exmaple.com",
                    },
                    "org_unit": {"uuid": unitid},
                    "validity": {
                        "from": "2013-01-01",
                        "to": None,
                    },
                },
            ]

            self.assertRequestResponse(
                '/service/details/create',
                {
                    'error': True,
                    'error_key': 'V_MISSING_REQUIRED_VALUE',
                    'description': "Missing uuid",
                    'key': 'uuid',
                    'status': 400,
                    'obj': req[0],
                },
                status_code=400,
                json=req,
            )

        with self.subTest('not a UUID'):
            req = [{
                "type": "address",
                "address_type": address_class,
                # NB: not a UUID!
                "address": {
                    "uuid": "hallo@exmaple.com",
                },
                "org_unit": {"uuid": unitid},
                "validity": {
                    "from": "2013-01-01",
                    "to": None,
                },
            }]

            self.assertRequestResponse(
                '/service/details/create',
                {
                    'error': True,
                    'error_key': 'E_INVALID_UUID',
                    'description': (
                        "Invalid uuid for 'uuid': 'hallo@exmaple.com'"
                    ),
                    'status': 400,
                    'obj': req[0],
                },
                status_code=400,
                json=req,
            )

        with self.subTest('unit not found'):
            req = [{
                "type": "address",
                "address_type": address_class,
                "address": {
                    "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                },
                "org_unit": {"uuid": nothingid},
                "validity": {
                    "from": "2013-01-01",
                    "to": None,
                },
            }]

            self.assertRequestResponse(
                '/service/details/create',
                {
                    'description': 'Org unit not found.',
                    'error': True,
                    'error_key': 'E_ORG_UNIT_NOT_FOUND',
                    'status': 404,
                    'uuid': nothingid,
                },
                status_code=404,
                json=req,
            )

        with self.subTest('employee not found'):
            req = [{
                "type": "address",
                "address_type": address_class,
                "address": {
                    "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                },
                "person": {"uuid": nothingid},
                "validity": {
                    "from": "2013-01-01",
                    "to": None,
                },
            }]

            self.assertRequestResponse(
                '/service/details/create',
                {
                    'description': 'User not found.',
                    'error': True,
                    'error_key': 'E_USER_NOT_FOUND',
                    'status': 404,
                    'uuid': nothingid,
                },
                status_code=404,
                json=req,
            )

    def test_edit_errors(self, mock):
        self.load_sample_structures()

        other_userid = util.load_fixture('organisation/bruger',
                                         'create_bruger_fætterguf.json')
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"

        nothingid = "00000000-0000-0000-0000-000000000000"

        orig_address = {
            "href": "https://www.openstreetmap.org/"
            "?mlon=10.19938084&mlat=56.17102843&zoom=16",
            "name": "Nordre Ringgade 1, 8000 Aarhus C",
            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
            "address_type": address_class,
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31",
            },
        }

        with self.subTest('neither failing'):
            req = [
                {
                    "type": "address",
                    "original": orig_address,
                    "data": {
                        "address_type": phone_class,
                        "address": {
                            "value": "11223344",
                        },
                    },
                },
            ]

            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description':
                    'must specify only one of person and org_unit!',
                    'error': True,
                    'error_key': 'E_INVALID_INPUT',
                    'employee_uuid': None,
                    'org_unit_uuid': None,
                    'obj': req[0]['original'],
                    'status': 400,
                },
                status_code=400,
                json=req,
            )

        with self.subTest('both failing'):
            req = [
                {
                    "type": "address",
                    "original": {
                        "address": orig_address,
                        "person": {"uuid": userid},
                        "org_unit": {"uuid": unitid},
                    },
                    "data": {
                        "address_type": phone_class,
                        "value": "11223344",
                    },
                },
            ]

            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description':
                    'must specify only one of person and org_unit!',
                    'error': True,
                    'error_key': 'E_INVALID_INPUT',
                    'employee_uuid': userid,
                    'org_unit_uuid': unitid,
                    'obj': req[0]['original'],
                    'status': 400,
                },
                status_code=400,
                json=req,
            )

        with self.subTest('missing edit value'):
            req = [
                {
                    "type": "address",
                    "original": {
                        "address": orig_address,
                        "person": {"uuid": userid},
                    },
                    "data": {
                        "address_type": phone_class,
                        # NB: no value
                    },
                },
            ]

            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'error': True,
                    'error_key': 'V_MISSING_REQUIRED_VALUE',
                    'description': 'Missing value',
                    'key': 'value',
                    'status': 400,
                    'obj': req[0]['data'],
                },
                status_code=400,
                json=req,
            )

        with self.subTest('missing original'):
            req = [{
                "type": "address",
                # NB: no original!
                "data": {
                    "validity": {
                        'to': '2009-12-31',
                    },
                }
            }]

            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description': 'Missing original',
                    'error': True,
                    'error_key': 'V_MISSING_REQUIRED_VALUE',
                    'key': 'original',
                    'obj': req[0],
                    'status': 400,
                },
                status_code=400,
                json=req,
            )

        with self.subTest('invalid original'):
            req = [{
                "type": "address",
                # NB: no original!
                "original": None,
                "data": {
                    "validity": {
                        'to': '2009-12-31',
                    },
                }
            }]

            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'error': True,
                    'error_key': 'E_INVALID_TYPE',
                    'description':
                    "Invalid 'original', expected dict, got: null",
                    'actual': None,
                    'key': 'original',
                    'expected': 'dict',
                    'status': 400,
                    'obj': req[0],
                },
                status_code=400,
                json=req,
            )

        with self.subTest('wrong original'):
            req = [{
                "type": "address",
                "original": {
                    'address_type': email_class,
                    # wrong!
                    'href': 'mailto:user@example.com',
                    'name': 'user@example.com',
                    'urn': 'urn:mailto:user@example.com',
                    "person": {"uuid": userid},
                    'validity': {
                        'from': '1934-06-09',
                        'to': None,
                    },
                },
                "data": {
                    "validity": {
                        'to': '2009-12-31',
                    },
                }
            }]

            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'error': True,
                    'error_key': 'E_ORIGINAL_ENTRY_NOT_FOUND',
                    'description': 'Original entry not found.',
                    'status': 400,
                },
                status_code=400,
                json=req,
            )

        with self.subTest('wrong original'):
            req = [{
                "type": "address",
                "original": {
                    'address_type': email_class,
                    'href': 'mailto:user@example.com',
                    'name': 'user@example.com',
                    'urn': 'urn:mailto:user@example.com',
                    "person": {"uuid": other_userid},
                    'validity': {
                        'from': '1934-06-09',
                        'to': None,
                    },
                },
                "data": {
                    "validity": {
                        'to': '2009-12-31',
                    },
                }
            }]

            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description': 'no addresses to edit!',
                    'error': True,
                    'error_key': 'E_INVALID_INPUT',
                    'status': 400,
                },
                status_code=400,
                json=req,
            )

    def test_employee_address(self, mock):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        user = {
            'name': 'Anders And',
            'uuid': userid,
        }

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
                'person': user,
                'validity': {
                    'from': '1934-06-09',
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
                 'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                         '/f/address_type/',
                 'user_key': 'address_type',
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
            '/service/details/create',
            [userid],
            json=[
                {
                    "type": "address",
                    "address_type": ean_class,
                    "value": '1234567890',
                    "person": {'uuid': userid},
                    "validity": {
                        "from": "2013-01-01",
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

        addresses += [
            {
                'address_type': ean_class,
                'href': None,
                'name': '1234567890',
                'urn': 'urn:magenta.dk:ean:1234567890',
                'person': user,
                'validity': {
                    'from': '2013-01-01',
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
            '/service/details/create',
            [userid, userid, userid],
            json=[
                {
                    "type": "address",
                    "address_type": email_class,
                    "value": "hest@example.com",
                    "person": {'uuid': userid},
                    "validity": {
                        "from": "2014-01-01",
                    },
                },
                {
                    "type": "address",
                    "address_type": address_class,
                    "uuid": "ae95777c-7ec1-4039-8025-e2ecce5099fb",
                    "person": {'uuid': userid},
                    "validity": {
                        "from": "2015-01-01",
                    },
                },
                {
                    "type": "address",
                    "address_type": phone_class,
                    "value": '3336 9696',
                    "person": {'uuid': userid},
                    "validity": {
                        "from": "2016-01-01",
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
                'person': user,
                'validity': {
                    'from': '2014-01-01', 'to': None,
                },
            },
            {
                'address_type': address_class,
                'href': 'https://www.openstreetmap.org/'
                '?mlon=10.20320628&mlat=56.15263055&zoom=16',
                'name': 'Rådhuspladsen 2, 4., 8000 Aarhus C',
                'uuid': 'ae95777c-7ec1-4039-8025-e2ecce5099fb',
                'person': user,
                'validity': {
                    'from': '2015-01-01', 'to': None,
                },
            },
            {
                'address_type': phone_class,
                'href': 'tel:+4533369696',
                'name': '33369696',
                'urn': 'urn:magenta.dk:telefon:+4533369696',
                'person': user,
                'validity': {
                    'from': '2016-01-01', 'to': None,
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

        userid = util.load_fixture('organisation/bruger',
                                   'create_bruger_fætterguf.json')
        user = {
            'name': 'Fætter Guf',
            'uuid': userid,
        }

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

        functionid, = self.assertRequest(
            '/service/details/create',
            json=[
                {
                    "type": "address",
                    "address_type": address_class,
                    "address": {
                        "uuid": '606cf42e-9dc2-4477-bf70-594830fcbdec',
                    },
                    "person": user,
                    "validity": {
                        "from": "2013-01-01",
                        "to": "2019-12-31",
                    },
                },
            ])

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [
                {
                    "address": {
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                        'name': 'Åbogade 15, 1., 8200 Aarhus N',
                        'uuid': '606cf42e-9dc2-4477-bf70-594830fcbdec',
                    },
                    'address_type': {
                        'scope': 'DAR',
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'user_key': 'AdressePost',
                    },
                    "uuid": functionid,
                    "person": user,
                    "org_unit": None,
                    'validity': {
                        "to": "2019-12-31",
                        'from': '2013-01-01',
                    },
                }
            ],
        )

    def test_edit_address(self, mock):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

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
                    'person': {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    'validity': {
                        'from': '1934-06-09',
                        'to': None,
                    },
                },
            ],
        )

        # first, test editing the value & the end time
        self.assertRequestResponse(
            '/service/details/edit',
            [userid],
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
                        'from': '1934-06-09',
                        'to': None,
                    },
                    'person': {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                },
                "data": {
                    'value': 'user@example.com',
                    "validity": {
                        'to': '2009-12-31',
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
                    'person': {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    'validity': {
                        'from': '1934-06-09',
                        'to': '2009-12-31',
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
            '/service/details/edit',
            [userid],
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
                    "person": {"uuid": userid},
                    'validity': {
                        'from': '1934-06-09',
                        'to': '2009-12-31',
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
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=12.57924839&mlat=55.68113676&zoom=16',
                    'name': 'Pilestræde 43, 3., 1112 København K',
                    'uuid': '0a3f50a0-23c9-32b8-e044-0003ba298018',
                    'person': {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    'validity': {
                        'from': '1934-06-09',
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
        user = {
            'name': 'Fedtmule',
            'uuid': userid,
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
                "person": user,
                "validity": {
                    "from": "1932-05-12",
                    "to": None
                }
            },
            {
                "address_type": email_class,
                "href": "mailto:goofy@example.com",
                "name": "goofy@example.com",
                "urn": "urn:mailto:goofy@example.com",
                "person": user,
                "validity": {
                    "from": "1932-05-12",
                    "to": None
                }
            },
            {
                "address_type": email_class,
                "href": "mailto:goofy@example.com",
                "name": "goofy@example.com",
                "urn": "urn:mailto:goofy@example.com",
                "person": user,
                "validity": {
                    "from": "1932-05-12",
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
            '/service/details/edit',
            [userid],
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
            '/service/details/edit',
            [userid],
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

    def test_edit_web_address(self, mock):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        user = {
            'name': 'Anders And',
            'uuid': userid,
        }

        old_addr = {
            'address_type': email_class,
            'href': 'mailto:bruger@example.com',
            'name': 'bruger@example.com',
            'urn': 'urn:mailto:bruger@example.com',
            'person': user,
            'validity': {
                'from': '1934-06-09',
                'to': None,
            },
        }

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [old_addr],
        )

        self.assertRequestResponse(
            '/service/details/edit',
            [userid],
            json=[
                {
                    'type': 'address',
                    'original': old_addr,
                    'data': {
                        "address": dict(**old_addr, value='hest@example.com'),
                    },
                },
            ],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [
                {
                    'address_type': {
                        'example': 'test@example.com',
                        'name': 'Emailadresse',
                        'scope': 'EMAIL',
                        'user_key': 'Email',
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    'href': 'mailto:hest@example.com',
                    'name': 'hest@example.com',
                    'urn': 'urn:mailto:hest@example.com',
                    'person': user,
                    'validity': {
                        'from': '1934-06-09',
                        'to': None,
                    },
                }
            ],
        )

    def test_edit_ean_address(self, mock):
        self.load_sample_structures()

        unitid = "04c78fc2-72d2-4d02-b55f-807af19eac48"
        unit = {
            'name': 'Afdeling for Samtidshistorik',
            'user_key': 'frem',
            'uuid': unitid,
            'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
        }

        self.assertIn(ean_class, self.client.get(
            '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
            '/f/address_type/',
        ).json['data']['items'])

        old_addr = {
            "address_type": {
                "example": "<UUID>",
                "name": "Adresse",
                "scope": "DAR",
                "user_key": "AdressePost",
                "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
            },
            "href": "https://www.openstreetmap.org/"
                    "?mlon=10.19938084&mlat=56.17102843&zoom=16",
            "name": "Nordre Ringgade 1, 8000 Aarhus C",
            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
            'org_unit': unit,
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31"
            }
        }

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            [old_addr],
        )

        self.assertRequestResponse(
            '/service/details/edit',
            [unitid],
            json=[
                {
                    'type': 'address',
                    'original': old_addr,
                    'data': {
                        "address": old_addr,
                        'value': '1234567890',
                        'address_type': ean_class,
                    },
                },
            ],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            [{
                'address_type': ean_class,
                'href': None,
                'name': '1234567890',
                'urn': 'urn:magenta.dk:ean:1234567890',
                'org_unit': unit,
                'validity': {
                    'from': '2016-01-01',
                    'to': '2018-12-31',
                },
            }],
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            [{
                'address_type': ean_class,
                'href': None,
                'name': '1234567890',
                'urn': 'urn:magenta.dk:ean:1234567890',
                'org_unit': unit,
                'validity': {
                    'from': '2016-01-01',
                    'to': '2018-12-31',
                },
            }],
        )

    def test_edit_text_address(self, mock):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        user = {
            'name': 'Anders And',
            'uuid': userid,
        }

        classid = util.load_fixture(
            'klassifikation/klasse', 'create_klasse.json',
            '0bf0daec-9d83-4783-a2cf-5e628fe70e51',
            description=None,
            example="…",
            name='Kommentar',
            scope="TEXT",
            user_key='Comment',
            facetid="e337bab4-635f-49ce-aa31-b44047a43aa1",
        )

        comment_class = {
            'example': '…',
            'name': "Kommentar",
            'scope': 'TEXT',
            'user_key': 'Comment',
            'uuid': classid,
        }

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/f/address_type/',
                {
                    'data': {
                        'offset': 0, 'total': 5,
                        'items': [
                            comment_class,
                            phone_class,
                            address_class,
                            email_class,
                            ean_class,
                        ],
                    },
                    'path': '/service/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                    '/f/address_type/',
                    'user_key': 'address_type',
                    'uuid': 'e337bab4-635f-49ce-aa31-b44047a43aa1'}
            )

        old_addr = {
            'address_type': email_class,
            'href': 'mailto:bruger@example.com',
            'name': 'bruger@example.com',
            'urn': 'urn:mailto:bruger@example.com',
            'person': user,
            'validity': {
                'from': '1934-06-09',
                'to': None,
            },
        }

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [old_addr],
        )

        self.assertRequestResponse(
            '/service/details/edit',
            [userid],
            json=[
                {
                    'type': 'address',
                    'original': old_addr,
                    'data': {
                        "address": old_addr,
                        'address_type': comment_class,
                        'value': 'kaflibob',
                    },
                },
            ],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/address'.format(userid),
            [
                {
                    'address_type': comment_class,
                    'href': None,
                    'name': 'kaflibob',
                    'urn': 'urn:text:kaflibob',
                    'person': user,
                    'validity': {
                        'from': '1934-06-09',
                        'to': None,
                    },
                }
            ],
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
                'org_unit': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': unitid,
                    'validity': {'from': '2016-01-01', 'to': None},
                },
                'validity': {
                    'from': '2016-01-01', 'to': None,
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
                'name': '87150000',
                'urn': 'urn:magenta.dk:telefon:+4587150000',
                'org_unit': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': unitid,
                    'validity': {'from': '2016-01-01', 'to': None},
                },
                'validity': {
                    'from': '2016-01-01', 'to': None,
                },
            },
            {
                'address_type': {
                    'example': '<UUID>',
                    'name': 'Adresse',
                    'scope': 'DAR',
                    'user_key': 'AdressePost',
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                },
                'href': 'https://www.openstreetmap.org/'
                '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                'org_unit': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': unitid,
                    'validity': {'from': '2016-01-01', 'to': None},
                },
                'validity': {
                    'from': '2016-01-01', 'to': None,
                },
            },
        ]

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

        # NOW CREATE IT

        self.assertRequestResponse(
            '/service/details/create',
            [unitid],
            json=[
                {
                    "type": "address",
                    "address_type": email_class,
                    "value": "hallo@exmaple.com",
                    "org_unit": {"uuid": unitid},
                    "validity": {
                        "from": "2013-01-01",
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
                        "from": "2015-02-04",
                        "to": "2017-10-21",
                    }
                },
                {
                    "address_type": {
                        "example": "<UUID>",
                        "name": "Adresse",
                        "scope": "DAR",
                        "user_key": "AdressePost",
                        "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                    },
                    "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                },
            ],
            "validity": {
                "from": "2016-02-04",
                "to": "2017-10-21",
            }
        }

        r = self.request('/service/ou/create', json=payload)
        unitid = r.json

        address_rels = [
            {
                'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                'virkning': {
                    'from': '2016-02-04 00:00:00+01',
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
                "location": "Overordnet Enhed",
                "name": "Fake Corp",
                "org": {
                    "name": "Aarhus Universitet",
                    "user_key": "AU",
                    "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                },
                "org_unit_type": {
                    "example": None,
                    "name": "Institut",
                    "scope": None,
                    "user_key": "inst",
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                },
                "parent": {
                    "location": "",
                    "name": "Overordnet Enhed",
                    "org": {
                        "name": "Aarhus Universitet",
                        "user_key": "AU",
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                    "org_unit_type": {
                        "example": None,
                        "name": "Afdeling",
                        "scope": None,
                        "user_key": "afd",
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
                    },
                    "parent": None,
                    "user_key": "root",
                    "user_settings": {
                        "orgunit": {
                            "show_location": True,
                            "show_roles": True,
                            "show_user_key": False
                        }
                    },
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "validity": {
                        "from": "2016-01-01",
                        "to": None
                    }
                },
                "user_key": "Fake Corp 00000000-0000-0000-0000-000000000000",
                "user_settings": {
                    "orgunit": {
                        "show_location": True,
                        "show_roles": True,
                        "show_user_key": False
                    }
                },
                "uuid": unitid,
                "validity": {
                    "from": "2016-02-04",
                    "to": "2017-10-21"
                }
            },
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/'.format(unitid),
            {
                'address': True,
                'association': False,
                'engagement': False,
                'it': False,
                'leave': False,
                'manager': False,
                'org_unit': True,
                'role': False,
                'related_unit': False,
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
                        'example': '20304060',
                        'name': 'Telefonnummer',
                        'scope': 'PHONE',
                        'user_key': 'Telefon',
                        'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                    },
                    'org_unit': {
                        'name': 'Fake Corp',
                        'user_key':
                        'Fake Corp 00000000-0000-0000-0000-000000000000',
                        'uuid': unitid,
                        'validity': {'from': '2016-02-04', 'to': '2017-10-21'},
                    },
                    'href': 'tel:+4511223344',
                    'name': '11223344',
                    'validity': {
                        'from': '2015-02-04',
                        'to': '2017-10-21',
                    },
                    'urn': 'urn:magenta.dk:telefon:+4511223344',
                },
                {
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                    'org_unit': {
                        'name': 'Fake Corp',
                        'user_key':
                        'Fake Corp 00000000-0000-0000-0000-000000000000',
                        'uuid': unitid,
                        'validity': {'from': '2016-02-04', 'to': '2017-10-21'},
                    },
                    'href': 'https://www.openstreetmap.org/'
                            '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'validity': {
                        'from': '2016-02-04',
                        'to': '2017-10-21',
                    },
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
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
        unit = {
            'name': 'Afdeling for Samtidshistorik',
            'user_key': 'frem',
            'uuid': unitid,
            'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
        }

        orig_address = {
            "href": "https://www.openstreetmap.org/"
            "?mlon=10.19938084&mlat=56.17102843&zoom=16",
            "name": "Nordre Ringgade 1, 8000 Aarhus C",
            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
            "address_type": address_class,
            "org_unit": unit,
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31",
            },
        }

        new_address_type = phone_class

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            [orig_address],
        )

        self.assertRequestResponse(
            '/service/details/edit',
            [unitid],
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
                'name': '87150000',
                'urn': 'urn:magenta.dk:telefon:+4587150000',
                'org_unit': unit,
                'validity': {
                    'from': '2016-01-01',
                    'to': '2018-12-31',
                },
            }],
        )

    def test_add_org_unit_address(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = '2874e1dc-85e6-4269-823a-e1125484dfd3'
        unit = {
            'name': 'Overordnet Enhed',
            'user_key': 'root',
            'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
            'validity': {'from': '2016-01-01', 'to': None},
        }

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
                'org_unit': unit,
                'validity': {
                    'from': '2016-01-01', 'to': None,
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
                'name': '87150000',
                'org_unit': unit,
                'validity': {
                    'from': '2016-01-01', 'to': None,
                },
                'urn': 'urn:magenta.dk:telefon:+4587150000',
            },
            {
                'address_type': {
                    'example': '<UUID>',
                    'name': 'Adresse',
                    'scope': 'DAR',
                    'user_key': 'AdressePost',
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                },
                'href': 'https://www.openstreetmap.org/'
                '?mlon=10.19938084&mlat=56.17102843&zoom=16',
                'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                'org_unit': unit,
                'validity': {
                    'from': '2016-01-01', 'to': None,
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
            '/service/details/create',
            [unitid],
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
                    "org_unit": {"uuid": unitid},
                    "validity": {
                        "from": "2017-01-02",
                    },
                },
            ],
        )

        address_rels.append({
            'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
            'urn': 'urn:mailto:root@example.com',
            'virkning': {
                'from': '2017-01-02 00:00:00+01',
                'to': 'infinity',
                'from_included': True,
                'to_included': False,
            },
        })

        addresses.append({
            'address_type': email_class,
            'href': 'mailto:root@example.com',
            'name': 'root@example.com',
            'org_unit': unit,
            'validity': {
                'from': '2017-01-02',
                'to': None,
            },
            'urn': 'urn:mailto:root@example.com',
        })

        self.assertEqual(
            address_rels,
            c.organisationenhed.get(unitid)['relationer']['adresser'],
        )

        # it's in the future, so not written yet
        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            addresses[:-1],
        )

        with freezegun.freeze_time('2017-01-02', tz_offset=1):
            self.assertRequestResponse(
                '/service/ou/{}/details/address'.format(unitid),
                addresses,
            )

    def test_edit_org_unit_address_overwrite(self, mock):
        self.load_sample_structures()

        unitid = '85715fc7-925d-401b-822d-467eb4b163b6'
        unit = {
            'name': 'Filosofisk Institut',
            'user_key': 'fil',
            'uuid': unitid,
            'validity': {'from': '2016-01-01', 'to': None},
        }

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
                "name": "87150000",
                "org_unit": unit,
                "validity": {
                    "from": "2016-01-01",
                    "to": None
                },
                "urn": "urn:magenta.dk:telefon:+4587150000"
            },
            {
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "AdressePost",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                },
                "href": "https://www.openstreetmap.org/"
                "?mlon=10.19938084&mlat=56.17102843&zoom=16",
                "name": "Nordre Ringgade 1, 8000 Aarhus C",
                "org_unit": unit,
                "validity": {
                    "from": "2016-01-01",
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
            '/service/details/edit',
            [unitid], json=req)

        addresses[1]['validity']['from'] = '2016-06-01'
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
        unit = {
            'name': 'Filosofisk Institut',
            'user_key': 'fil',
            'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
            'validity': {'from': '2016-01-01', 'to': None},
        }

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
                "name": "87150000",
                'org_unit': unit,
                "validity": {
                    "from": "2016-01-01",
                    "to": None
                },
                "urn": "urn:magenta.dk:telefon:+4587150000"
            },
            {
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "AdressePost",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                },
                "href": "https://www.openstreetmap.org/"
                "?mlon=10.19938084&mlat=56.17102843&zoom=16",
                "name": "Nordre Ringgade 1, 8000 Aarhus C",
                'org_unit': unit,
                "validity": {
                    "from": "2016-01-01",
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
                "org_unit": {"uuid": unitid},
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "AdressePost",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                },
                "uuid": "d901ff7e-8ad9-4581-84c7-5759aaa82f7b",
                "validity": {
                    'from': '2016-06-01',
                },
            },
        ]

        self.assertRequestResponse(
            '/service/details/create',
            [unitid], json=req)

        addresses.append({
            'address_type': {
                'example': '<UUID>',
                'name': 'Adresse',
                'scope': 'DAR',
                'user_key': 'AdressePost',
                'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
            },
            'href': 'https://www.openstreetmap.org/'
            '?mlon=10.20019416&mlat=56.17063452&zoom=16',
            'name': 'Nordre Ringgade 2, 8000 Aarhus C',
            'org_unit': unit,
            'validity': {'from': '2016-06-01', 'to': None},
            'uuid': 'd901ff7e-8ad9-4581-84c7-5759aaa82f7b',
        })

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            addresses,
        )


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@util.mock('dawa-addresses.json', allow_mox=True)
class Reading(util.LoRATestCase):

    def test_missing_class(self, mock):
        self.load_sample_structures(minimal=True)

        functionid = util.load_fixture(
            'organisation/organisationfunktion',
            'create_organisationfunktion_email_andersand.json',
        )

        with self.subTest('missing classes'):
            self.assertRequestResponse(
                '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                '/details/address',
                [{
                    'uuid': functionid,
                    'address': {
                        'href': 'mailto:bruger@example.com',
                        'name': 'bruger@example.com',
                        'urn': 'urn:mailto:bruger@example.com',
                    },
                    # TODO: should we do more?
                    'address_type': None,
                    'org_unit': None,
                    'person': {
                        'name': 'Anders And',
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    'validity': {'from': '1934-06-09', 'to': None},
                }],
            )

    def test_reading(self, mock):
        self.load_sample_structures()

        with self.subTest('present I'):
            self.assertRequestResponse(
                '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053'
                '/details/address?validity=present',
                [
                    {
                        'uuid': '64ea02e2-8469-4c54-a523-3d46729e86a7',
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'address': {
                            'href': 'mailto:goofy@example.com',
                            'name': 'goofy@example.com',
                            'urn': 'urn:mailto:goofy@example.com',
                        },
                        'person': {
                            'name': 'Fedtmule',
                            'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                        },
                        'org_unit': None,
                        'validity': {
                            'from': '1932-05-12',
                            'to': None,
                        },
                    },
                    {
                        'uuid': 'cd6008bc-1ad2-4272-bc1c-d349ef733f52',
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'AdressePost',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'address': {
                            'href': 'https://www.openstreetmap.org/'
                            '?mlon=12.58176945&mlat=55.67563739&zoom=16',
                            'name':
                            'Christiansborg Slotsplads 1, 1218 København K',
                            'uuid': 'bae093df-3b06-4f23-90a8-92eabedb3622',
                        },
                        'person': {
                            'name': 'Fedtmule',
                            'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                        },
                        'org_unit': None,
                        'validity': {
                            'from': '1932-05-12',
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
                        'uuid': 'fba61e38-b553-47cc-94bf-8c7c3c2a6887',
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'address': {
                            'href': 'mailto:bruger@example.com',
                            'name': 'bruger@example.com',
                            'urn': 'urn:mailto:bruger@example.com',
                        },
                        'person': {
                            'name': 'Anders And',
                            'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                        },
                        'org_unit': None,
                        'validity': {
                            'from': '1934-06-09',
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
                        "address": {
                            "href": "https://www.openstreetmap.org/"
                            "?mlon=10.19938084&mlat=56.17102843&zoom=16",
                            "name": "Nordre Ringgade 1, 8000 Aarhus C",
                            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197"
                        },
                        "address_type": {
                            "example": "<UUID>",
                            "name": "Adresse",
                            "scope": "DAR",
                            "user_key": "AdressePost",
                            "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                        },
                        "org_unit": {
                            "name": "Overordnet Enhed",
                            "user_key": "root",
                            "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                            "validity": {
                                "from": "2016-01-01",
                                "to": None
                            }
                        },
                        "person": None,
                        "uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None
                        }
                    }
                ],
            )

        with self.subTest('present IV'):
            self.assertRequestResponse(
                '/service/ou/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
                '/details/address?validity=present',
                [
                    {
                        "address": {
                            "href": "tel:+4587150000",
                            "name": "87150000",
                            "urn": "urn:magenta.dk:telefon:+4587150000"
                        },
                        "address_type": {
                            "example": "20304060",
                            "name": "Telefonnummer",
                            "scope": "PHONE",
                            "user_key": "Telefon",
                            "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
                        },
                        "org_unit": {
                            "name": "Humanistisk fakultet",
                            "user_key": "hum",
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "validity": {
                                "from": "2016-01-01",
                                "to": None
                            }
                        },
                        "person": None,
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None
                        }
                    },
                    {
                        "address": {
                            "href": None,
                            "name": "5798000420526",
                            "urn": "urn:magenta.dk:ean:5798000420526"
                        },
                        "address_type": {
                            "example": "5712345000014",
                            "name": "EAN",
                            "scope": "EAN",
                            "user_key": "EAN",
                            "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"
                        },
                        "org_unit": {
                            "name": "Humanistisk fakultet",
                            "user_key": "hum",
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "validity": {
                                "from": "2016-01-01",
                                "to": None
                            }
                        },
                        "person": None,
                        "uuid": "a0fe7d43-1e0d-4232-a220-87098024b34d",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None
                        }
                    },
                    {
                        "address": {
                            "href": "https://www.openstreetmap.org/"
                            "?mlon=10.19938084&mlat=56.17102843&zoom=16",
                            "name": "Nordre Ringgade 1, 8000 Aarhus C",
                            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197"
                        },
                        "address_type": {
                            "example": "<UUID>",
                            "name": "Adresse",
                            "scope": "DAR",
                            "user_key": "AdressePost",
                            "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                        },
                        "org_unit": {
                            "name": "Humanistisk fakultet",
                            "user_key": "hum",
                            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                            "validity": {
                                "from": "2016-01-01",
                                "to": None
                            }
                        },
                        "person": None,
                        "uuid": "e1a9cede-8c9b-4367-b628-113834361871",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None
                        }
                    }
                ],
            )

        with self.subTest('present V'):
            self.assertRequestResponse(
                '/service/ou/b688513d-11f7-4efc-b679-ab082a2055d0'
                '/details/address?validity=present',
                [],
            )

        with self.subTest('present VI'):
            self.assertRequestResponse(
                '/service/ou/85715fc7-925d-401b-822d-467eb4b163b6'
                '/details/address?validity=present',
                [],
            )

        with self.subTest('present VII'):
            self.assertRequestResponse(
                '/service/ou/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/details/address?validity=present',
                [],
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

    def test_missing_address(self, mock):
        self.load_sample_structures()

        unitid = "2874e1dc-85e6-4269-823a-e1125484dfd3"
        addrid = "bd7e5317-4a9e-437b-8923-11156406b117"
        functionid = "414044e0-fe5f-4f82-be20-1e107ad50e80"

        for t in ('adresser', 'adgangsadresser',
                  'historik/adresser', 'historik/adgangsadresser'):
            mock.get(
                'https://dawa.aws.dk/' + t,
                json=[],
            )

        lora.Connector().organisationfunktion.update(
            {
                'relationer': {
                    'adresser': [
                        {
                            'objekttype': "DAR",
                            'uuid': addrid,
                            'virkning': {
                                'from': '2016-01-01',
                                'to': '2020-01-01',
                            },
                        },
                    ],
                },
            },
            functionid,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/address'.format(unitid),
            [{
                'address_type': address_class,
                'address': {
                    'name': 'Ukendt',
                    'uuid': addrid,
                    'error': 'no such address {!r}'.format(addrid),
                    'href': None,
                },
                'org_unit': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'validity': {
                        'from': '2016-01-01', 'to': None,
                    },
                },
                'person': None,
                'uuid': functionid,
                'validity': {
                    'from': '2016-01-01', 'to': '2019-12-31',
                },
            }],
        )

    def test_missing_error(self, mock):
        self.load_sample_structures()

        unitid = "2874e1dc-85e6-4269-823a-e1125484dfd3"
        addrid = "bd7e5317-4a9e-437b-8923-11156406b117"
        functionid = "414044e0-fe5f-4f82-be20-1e107ad50e80"

        mock.get(
            'https://dawa.aws.dk/adresser',
            json={
                "type": "ResourceNotFoundError",
                "title": "The resource was not found",
                "details": {
                    "id": "bd7e5317-4a9e-437b-8923-11156406b117",
                },
            },
            status_code=500,
        )

        lora.Connector().organisationfunktion.update(
            {
                'relationer': {
                    'adresser': [
                        {
                            'objekttype': 'DAR',
                            'uuid': addrid,
                            'virkning': {
                                'from': '2016-01-01',
                                'to': '2020-01-01',
                            },
                        },
                    ],
                },
            },
            functionid,
        )

        with self.assertLogs(self.app.logger, logging.WARNING) as log_res:
            self.assertRequestResponse(
                '/service/ou/{}/details/address'.format(unitid),
                [{
                    'address': {
                        'error': '500 Server Error: None for url: '
                        'https://dawa.aws.dk/adresser'
                        '?id={}&noformat=1&struktur=mini'.format(addrid),
                        'href': None,
                        'name': 'Ukendt',
                        'uuid': addrid,
                    },
                    'address_type': address_class,
                    'org_unit': {
                        'name': 'Overordnet Enhed',
                        'user_key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'validity': {
                            'from': '2016-01-01', 'to': None,
                        },
                    },
                    'person': None,
                    'uuid': functionid,
                    'validity': {
                        'from': '2016-01-01', 'to': '2019-12-31',
                    },
                }],
            )

            self.assertRegex(log_res.output[0],
                             "ADDRESS LOOKUP FAILED")

    def test_offline(self, mock):
        self.load_sample_structures()

        unitid = "2874e1dc-85e6-4269-823a-e1125484dfd3"
        expected = [
            {
                "address": {
                    "error": "No mock address: "
                    "GET https://dawa.aws.dk/adresser"
                    "?id=bd7e5317-4a9e-437b-8923-11156406b117"
                    "&noformat=1&struktur=mini",
                    "href": None,
                    "name": "Ukendt",
                    "uuid": "bd7e5317-4a9e-437b-8923-11156406b117"
                },
                "address_type": {
                    "example": "<UUID>",
                    "name": "Adresse",
                    "scope": "DAR",
                    "user_key": "AdressePost",
                    "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                },
                "org_unit": {
                    "name": "Overordnet Enhed",
                    "user_key": "root",
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "validity": {
                        "from": "2016-01-01",
                        "to": None
                    }
                },
                "person": None,
                "uuid": "414044e0-fe5f-4f82-be20-1e107ad50e80",
                "validity": {
                    "from": "2016-01-01",
                    "to": "2019-12-31"
                }
            }
        ]

        with self.assertLogs(self.app.logger, logging.WARNING) as log_res:
            self.assertRequestResponse(
                '/service/ou/{}/details/address'.format(unitid),
                expected,
            )

            self.assertRegex(log_res.output[0],
                             "ADDRESS LOOKUP FAILED in '[^']*':\n")
