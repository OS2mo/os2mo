#
# Copyright (c) 2017-2019, Magenta ApS
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
                    "org": {
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
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
                    'description': 'Must supply exactly one org unit UUID, '
                                   'employee UUID or manager UUID',
                    'error': True,
                    'error_key': 'E_INVALID_INPUT',
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
                    "org": {
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
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
                    'description': 'Must supply exactly one org unit UUID, '
                                   'employee UUID or manager UUID',
                    'error': True,
                    'error_key': 'E_INVALID_INPUT',
                    'obj': req[0],
                    'status': 400,
                },
                json=req,
                status_code=400,
            )

        with self.subTest('no address'):
            req = [
                {
                    "type": "address",
                    "address_type": email_class,
                    "org_unit": {"uuid": unitid},
                    "org": {
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    },
                    # NB: no value
                    "validity": {
                        "from": "2017-01-01",
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
                    "value": "hallo@exmaple.com",
                    "org": {
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
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

        with self.subTest('unit not found'):
            req = [{
                "type": "address",
                "address_type": address_class,
                "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "org_unit": {"uuid": nothingid},
                "org": {
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
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
                    'org_unit_uuid': nothingid,
                },
                status_code=404,
                json=req,
            )

        with self.subTest('employee not found'):
            req = [{
                "type": "address",
                "address_type": address_class,
                "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "person": {"uuid": nothingid},
                "org": {
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
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
                    'employee_uuid': nothingid,
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

        with self.subTest('both failing'):
            req = [
                {
                    "type": "address",
                    "data": {
                        "person": {"uuid": userid},
                        "org_unit": {"uuid": unitid},
                        "address_type": phone_class,
                        "value": "11223344",
                        "validity": {
                            "from": "2017-01-01",
                            "to": "2018-12-31",
                        },
                    },
                    "uuid": "fba61e38-b553-47cc-94bf-8c7c3c2a6887"
                },
            ]

            self.assertRequestResponse(
                '/service/details/edit',
                {
                    'description': 'Must supply at most one org unit UUID, '
                                   'employee UUID or manager UUID',
                    'error': True,
                    'error_key': 'E_INVALID_INPUT',
                    'obj': req[0],
                    'status': 400,
                },
                status_code=400,
                json=req,
            )

    def test_add_org_unit_address(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unitid = '2874e1dc-85e6-4269-823a-e1125484dfd3'

        addr_id, = self.assertRequest(
            '/service/details/create',
            json=[
                {
                    "type": "address",
                    'address_type': {
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    'value': 'root@example.com',
                    "org_unit": {
                        "uuid": unitid
                    },
                    "org": {
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    },
                    "validity": {
                        "from": "2017-01-02",
                    },
                },
            ],
        )

        expected = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'brugervendtnoegle': 'root@example.com',
                    'funktionsnavn': 'Adresse',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'livscykluskode': 'Opstaaet',
            'note': 'Oprettet i MO',
            'relationer': {
                'adresser': [{
                    'objekttype': 'EMAIL',
                    'urn': 'urn:mailto:root@example.com',
                    'virkning': {
                        'from': '2017-01-02 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeenheder': [{
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'gyldighed': 'Aktiv',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            }
        }

        self.assertRegistrationsEqual(
            expected,
            c.organisationfunktion.get(addr_id)
        )

    def test_add_employee_address(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        employee_id = '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'

        addr_id, = self.assertRequest(
            '/service/details/create',
            json=[
                {
                    "type": "address",
                    'address_type': {
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    'value': 'root@example.com',
                    "person": {
                        "uuid": employee_id
                    },
                    "org": {
                        'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    },
                    "validity": {
                        "from": "2017-01-02",
                    },
                },
            ],
        )

        expected = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'brugervendtnoegle': 'root@example.com',
                    'funktionsnavn': 'Adresse',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'livscykluskode': 'Opstaaet',
            'note': 'Oprettet i MO',
            'relationer': {
                'adresser': [{
                    'objekttype': 'EMAIL',
                    'urn': 'urn:mailto:root@example.com',
                    'virkning': {
                        'from': '2017-01-02 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedebrugere': [{
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'gyldighed': 'Aktiv',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            }
        }

        self.assertRegistrationsEqual(
            expected,
            c.organisationfunktion.get(addr_id)
        )

    def test_create_employee_with_address(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        user_id = self.assertRequest(
            '/service/e/create',
            json={
                "name": "Torkild Testperson",
                "cpr_no": "0101501234",
                "org": {
                    'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
                },
                "details": [
                    {
                        "type": "address",
                        'address_type': {
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'value': 'root@example.com',
                        "validity": {
                            "from": "2017-01-02",
                        },
                        "org": {
                            'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
                        },
                    },
                ]
            }
        )

        expected = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'brugervendtnoegle': 'root@example.com',
                    'funktionsnavn': 'Adresse',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'livscykluskode': 'Opstaaet',
            'note': 'Oprettet i MO',
            'relationer': {
                'adresser': [{
                    'objekttype': 'EMAIL',
                    'urn': 'urn:mailto:root@example.com',
                    'virkning': {
                        'from': '2017-01-02 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedebrugere': [{
                    'uuid': user_id,
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'gyldighed': 'Aktiv',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            }
        }

        addr_id = c.organisationfunktion.fetch(tilknyttedebrugere=user_id)
        assert len(addr_id) == 1
        addr_id = addr_id[0]

        self.assertRegistrationsEqual(
            expected,
            c.organisationfunktion.get(addr_id)
        )

    def test_create_manager_with_address(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        func_id, = self.assertRequest(
            '/service/details/create',
            json=[{
                "type": "manager",
                "org_unit": {
                    'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                },
                "person": {
                    'uuid': userid
                },
                "responsibility": [{
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9",
                }],
                "manager_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                "manager_level": {
                    "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                },
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
                "address": [{
                    "type": "address",
                    'address_type': {
                        'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    },
                    'value': 'root@example.com',
                    "validity": {
                        "from": "2017-01-02",
                    },
                    "org": {
                        'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
                    },
                }],
            }]
        )

        expected = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'brugervendtnoegle': 'root@example.com',
                    'funktionsnavn': 'Adresse',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'livscykluskode': 'Importeret',
            'note': 'Oprettet i MO',
            'relationer': {
                'adresser': [{
                    'objekttype': 'EMAIL',
                    'urn': 'urn:mailto:root@example.com',
                    'virkning': {
                        'from': '2017-01-02 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedefunktioner': [{
                    'uuid': func_id,
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'gyldighed': 'Aktiv',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            }
        }

        addr_id = c.organisationfunktion.fetch(tilknyttedefunktioner=func_id)
        assert len(addr_id) == 1
        addr_id = addr_id[0]

        self.assertRegistrationsEqual(
            expected,
            c.organisationfunktion.get(addr_id)
        )

    def test_create_org_unit_with_address(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        unit_id = self.assertRequest(
            '/service/ou/create',
            json={
                "name": "Fake Corp",
                "integration_data": {"fakekey": 42},
                "parent": {
                    'uuid': "2874e1dc-85e6-4269-823a-e1125484dfd3"
                },
                "org_unit_type": {
                    'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
                },
                "validity": {
                    "from": "2016-02-04",
                },
                "details": [
                    {
                        "type": "address",
                        'address_type': {
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'value': 'root@example.com',
                        "validity": {
                            "from": "2017-01-02",
                        },
                        "org": {
                            'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
                        },
                    },
                ]
            }
        )

        expected = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'brugervendtnoegle': 'root@example.com',
                    'funktionsnavn': 'Adresse',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'livscykluskode': 'Opstaaet',
            'note': 'Oprettet i MO',
            'relationer': {
                'adresser': [{
                    'objekttype': 'EMAIL',
                    'urn': 'urn:mailto:root@example.com',
                    'virkning': {
                        'from': '2017-01-02 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeenheder': [{
                    'uuid': unit_id,
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'gyldighed': 'Aktiv',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            }
        }

        addr_id = c.organisationfunktion.fetch(tilknyttedeenheder=unit_id)
        assert len(addr_id) == 1
        addr_id = addr_id[0]

        self.assertRegistrationsEqual(
            expected,
            c.organisationfunktion.get(addr_id)
        )

    def test_edit_address(self, mock):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        addr_id = '414044e0-fe5f-4f82-be20-1e107ad50e80'

        self.assertRequest(
            '/service/details/edit',
            json=[
                {
                    "type": "address",
                    "uuid": addr_id,
                    "data": {
                        'address_type': {
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'value': 'root@example.com',
                        "validity": {
                            "from": "2017-01-02",
                        },
                    },
                }
            ]
        )

        expected = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'brugervendtnoegle': 'Nordre '
                                         'Ringgade '
                                         '1, '
                                         '8000 '
                                         'Aarhus '
                                         'C',
                    'funktionsnavn': 'Adresse',
                    'virkning': {
                        'from': '2016-01-01 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'livscykluskode': 'Rettet',
            'note': 'Rediger Adresse',
            'relationer': {
                'adresser': [{
                    'objekttype': 'DAR',
                    'urn': 'urn:dar:b1f1817d-5f02-4331-b8b3-97330a5d3197',
                    'virkning': {
                        'from': '2016-01-01 00:00:00+01',
                        'from_included': True,
                        'to': '2017-01-02 00:00:00+01',
                        'to_included': False
                    }
                }, {
                    'objekttype': 'EMAIL',
                    'urn': 'urn:mailto:root@example.com',
                    'virkning': {
                        'from': '2017-01-02 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    'virkning': {
                        'from': '2016-01-01 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': '2017-01-02 '
                              '00:00:00+01',
                        'to_included': False
                    }
                }, {
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeenheder': [{
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'virkning': {
                        'from': '2016-01-01 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'from': '2016-01-01 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'gyldighed': 'Aktiv',
                    'virkning': {
                        'from': '2016-01-01 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': '2017-01-02 '
                              '00:00:00+01',
                        'to_included': False
                    }
                }, {
                    'gyldighed': 'Aktiv',
                    'virkning': {
                        'from': '2017-01-02 '
                                '00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }]
            }
        }

        actual = c.organisationfunktion.get(addr_id)

        self.assertRegistrationsEqual(expected, actual)


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@util.mock('dawa-addresses.json', allow_mox=True)
class Reading(util.LoRATestCase):

    def test_missing_class(self, mock):
        self.load_sample_structures(minimal=True)

        functionid = util.load_fixture(
            'organisation/organisationfunktion',
            'create_organisationfunktion_email_andersand.json',
        )

        self.assertRequestResponse(
            '/service/e/53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
            '/details/address',
            [{
                'href': 'mailto:bruger@example.com',
                'name': 'bruger@example.com',
                'value': 'bruger@example.com',
                'address_type': None,
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'
                },
                'uuid': functionid,
                'validity': {'from': '1934-06-09', 'to': None}
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
                        'href': 'mailto:goofy@example.com',
                        'name': 'goofy@example.com',
                        'value': 'goofy@example.com',
                        'person': {
                            'name': 'Fedtmule',
                            'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                        },
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
                        'href': 'https://www.openstreetmap.org/?mlon='
                                '10.19938084&mlat=56.17102843&zoom=16',
                        'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'person': {
                            'name': 'Fedtmule',
                            'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                        },
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
                        'href': 'mailto:bruger@example.com',
                        'name': 'bruger@example.com',
                        'value': 'bruger@example.com',
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

        with self.subTest('present III'):
            self.assertRequestResponse(
                '/service/ou/2874e1dc-85e6-4269-823a-e1125484dfd3'
                '/details/address?validity=present',
                [
                    {
                        "href": "https://www.openstreetmap.org/"
                        "?mlon=10.19938084&mlat=56.17102843&zoom=16",
                        "name": "Nordre Ringgade 1, 8000 Aarhus C",
                        "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
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
                        "href": "tel:+4587150000",
                        "name": "+4587150000",
                        "value": "87150000",
                        "address_type": {
                            "example": "20304060",
                            "name": "Telefonnummer",
                            "scope": "PHONE",
                            "user_key": "Telefon",
                            "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
                        },
                        "visibility": {
                            'example': '20304060',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
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
                        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None
                        },
                    },
                    {
                        "href": None,
                        "name": "5798000420526",
                        "value": "5798000420526",
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
                        "uuid": "a0fe7d43-1e0d-4232-a220-87098024b34d",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None
                        }
                    },
                    {
                        "href": "https://www.openstreetmap.org/"
                        "?mlon=10.19938084&mlat=56.17102843&zoom=16",
                        "name": "Nordre Ringgade 1, 8000 Aarhus C",
                        "value": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
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
                            'urn': "urn:dar:{}".format(addrid),
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
                'name': 'Ukendt',
                'value': addrid,
                'error': 'no such address {!r}'.format(addrid),
                'href': None,
                'org_unit': {
                    'name': 'Overordnet Enhed',
                    'user_key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'validity': {
                        'from': '2016-01-01', 'to': None,
                    },
                },
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
                            'urn': "urn:dar:{}".format(addrid),
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
                    'error': '500 Server Error: None for url: '
                    'https://dawa.aws.dk/adresser'
                    '?id={}&noformat=1&struktur=mini'.format(addrid),
                    'href': None,
                    'name': 'Ukendt',
                    'value': addrid,
                    'address_type': address_class,
                    'org_unit': {
                        'name': 'Overordnet Enhed',
                        'user_key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'validity': {
                            'from': '2016-01-01', 'to': None,
                        },
                    },
                    'uuid': functionid,
                    'validity': {
                        'from': '2016-01-01', 'to': '2019-12-31',
                    },
                }],
            )

            self.assertRegex(log_res.output[0],
                             "ADDRESS LOOKUP FAILED")
