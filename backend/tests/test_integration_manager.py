#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy
import unittest

from unittest.mock import patch

import freezegun

from mora import lora
from mora import util as mora_util
from tests import util

mock_uuid = '1eb680cd-d8ec-4fd2-8ca0-dce2d03f59a5'


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@patch('uuid.uuid4', new=lambda: mock_uuid)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_manager_missing_unit(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        payload = {
            "type": "manager",
            "validity": {
                "from": "2017-12-01",
                "to": "2017-12-01",
            },
        }

        self.assertRequestResponse(
            '/service/details/create',
            {
                'description': 'Missing org_unit',
                'error': True,
                'error_key': 'V_MISSING_REQUIRED_VALUE',
                'key': 'org_unit',
                'obj': payload,
                'status': 400,
            },
            json=payload,
            status_code=400,
        )

    @util.mock('aabogade.json', allow_mox=True)
    def test_create_manager(self, m):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {'uuid': userid},
                'address': [{
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                }],
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
            }
        ]

        managerid, = self.assertRequest('/service/details/create',
                                        json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'virkning': {
                            'from': '2017-12-01 00:00:00+01',
                            'from_included': True,
                            'to': '2017-12-02 00:00:00+01',
                            'to_included': False,
                        },
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    },
                    {
                        "objekttype": "lederniveau",
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Leder"
                    }
                ]
            }
        }

        actual_manager = c.organisationfunktion.get(managerid)

        self.assertRegistrationsEqual(actual_manager, expected)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': [{
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                }],
                'manager_level': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
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
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': [{
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': managerid,
                'validity': {
                    'from': '2017-12-01',
                    'to': '2017-12-01',
                },
            }],
        )

    def test_create_vacant_manager(self):
        self.load_sample_structures()

        unit_id = "da77153e-30f3-4dc2-a611-ee912a28d8aa"

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/ou/{}/details/manager'.format(unit_id),
                [],
            )

        payload = [
            {
                "type": "manager",
                "org_unit": {
                    "uuid": unit_id,
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
                    "from": "2016-12-01",
                    "to": "2017-12-02",
                },
            }
        ]

        function_id, = self.assertRequest(
            '/service/details/create',
            json=payload,
        )

        self.assertRequestResponse(
            '/service/ou/{}/details/manager'.format(unit_id),
            [{
                'address': [],
                'manager_level': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                },
                'org_unit': {
                    'name': 'Historisk Institut',
                    'user_key': 'hist',
                    'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
                },
                'person': None,
                'responsibility': [{
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': function_id,
                'validity': {'from': '2016-12-01', 'to': '2017-12-02'},
            }],
        )

    def test_edit_manager_on_unit(self):
        self.load_sample_structures()

        unit_id = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
        user_id = "6ee24785-ee9a-4502-81c2-7697009c9053"

        with self.subTest('preconditions'):
            self.assertRequestResponse(
                '/service/ou/{}/details/manager'.format(unit_id),
                [],
            )

        # first create a manager on the unit
        expected = {
            'address': [],
            'manager_level': {
                'example': 'test@example.com',
                'name': 'Emailadresse',
                'scope': 'EMAIL',
                'user_key': 'Email',
                'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
            },
            'manager_type': {
                'example': None,
                'name': 'Medlem',
                'scope': None,
                'user_key': 'medl',
                'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
            },
            'org_unit': {
                'name': 'Historisk Institut',
                'user_key': 'hist',
                'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                'validity': {'from': '2016-01-01', 'to': '2018-12-31'},
            },
            'person': {
                'name': 'Fedtmule',
                'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
            },
            'responsibility': [{
                'example': None,
                'name': 'Medlem',
                'scope': None,
                'user_key': 'medl',
                'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
            }],
            'validity': {'from': '2016-12-01', 'to': '2017-12-02'},
        }

        function_id, = self.assertRequest(
            '/service/details/create',
            json=[{
                "type": "manager",
                "org_unit": {
                    "uuid": unit_id,
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
                "person": {
                    "uuid": user_id,
                },
                "validity": {
                    "from": "2016-12-01",
                    "to": "2017-12-02",
                },
            }],
        )

        with self.subTest('results'):
            expected['uuid'] = function_id

            self.assertRequestResponse(
                '/service/ou/{}/details/manager?validity=past'.format(unit_id),
                [],
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/manager'.format(unit_id),
                [expected],
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/manager'
                '?validity=future'.format(unit_id),
                [],
            )

        with self.subTest('change to vacant'):
            self.assertRequestResponse(
                '/service/details/edit',
                [function_id],
                json=[{
                    "type": "manager",
                    "uuid": function_id,
                    "data": {
                        "person": None,
                        "validity": {
                            "from": "2017-12-03",
                            "to": "2017-12-20",
                        },
                    },
                }],
            )

            future = expected.copy()
            future['person'] = None
            future['validity'] = {
                "from": "2017-12-03",
                "to": "2017-12-20",
            }

            self.assertRequestResponse(
                '/service/ou/{}/details/manager'.format(unit_id),
                [expected],
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/manager'
                '?validity=future'.format(unit_id),
                [future],
            )

        with self.subTest('change back'):
            self.assertRequestResponse(
                '/service/details/edit',
                [function_id],
                json=[{
                    "type": "manager",
                    "uuid": function_id,
                    "data": {
                        "person": {
                            "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        },
                        "validity": {
                            "from": "2017-12-21",
                            "to": "2017-12-31",
                        },
                    },
                }],
            )

            far_future = future.copy()
            far_future['person'] = {
                'name': 'Anders And',
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
            }
            far_future['validity'] = {
                "from": "2017-12-21",
                "to": "2017-12-31",
            }

            self.assertRequestResponse(
                '/service/ou/{}/details/manager'.format(unit_id),
                [expected],
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/manager'
                '?validity=future'.format(unit_id),
                [future, far_future],
            )

    def test_create_manager_no_valid_to(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {'uuid': userid},
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
                },
            }
        ]

        managerid, = self.assertRequest('/service/details/create',
                                        json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                    },
                    {
                        "objekttype": "lederniveau",
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Leder"
                    }
                ]
            }
        }

        actual_manager = c.organisationfunktion.get(managerid)

        self.assertRegistrationsEqual(actual_manager, expected)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': [],
                'manager_level': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
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
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': [{
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': managerid,
                'validity': {
                    'from': '2017-12-01', 'to': None,
                },
            }],
        )

    def test_create_manager_minimal(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {'uuid': userid},
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        managerid, = self.assertRequest('/service/details/create',
                                        json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Leder"
                    }
                ]
            }
        }

        actual_manager = c.organisationfunktion.get(managerid)

        self.assertRegistrationsEqual(actual_manager, expected)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=past'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': [],
                'manager_level': None,
                'manager_type': None,
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
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': [],
                'uuid': managerid,
                'validity': {
                    'from': '2017-12-01',
                    'to': '2017-12-01',
                },
            }],
        )

    @util.mock('aabogade.json', allow_mox=True)
    def test_create_manager_multiple_responsibilities(self, m):
        '''Can we create a manager with more than one responsibility?'''
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {'uuid': userid},
                'address': [{
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                }],
                "responsibility": [
                    {'uuid': "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"},
                    {'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"},
                ],
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
            }
        ]

        managerid, = self.assertRequest('/service/details/create',
                                        json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'virkning': {
                            'from': '2017-12-01 00:00:00+01',
                            'from_included': True,
                            'to': '2017-12-02 00:00:00+01',
                            'to_included': False,
                        },
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
                    },
                    {
                        "objekttype": "lederansvar",
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                    },
                    {
                        "objekttype": "lederniveau",
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ],
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "funktionsnavn": "Leder"
                    }
                ]
            }
        }

        actual_manager = c.organisationfunktion.get(managerid)

        self.assertRegistrationsEqual(actual_manager, expected)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': [{
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                }],
                'manager_level': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
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
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': [
                    {
                        'example': None,
                        'name': 'Fakultet',
                        'scope': None,
                        'user_key': 'fak',
                        'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                    },
                    {
                        'example': None,
                        'name': 'Institut',
                        'scope': None,
                        'user_key': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                    },
                ],
                'uuid': managerid,
                'validity': {
                    'from': '2017-12-01',
                    'to': '2017-12-01',
                },
            }],
        )

    def test_edit_manager_no_overwrite(self):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        req = [{
            "type": "manager",
            "uuid": manager_uuid,
            "data": {
                "org_unit": {
                    'uuid': "85715fc7-925d-401b-822d-467eb4b163b6"
                },
                "person": {
                    'uuid': userid,
                },
                "responsibility": [{
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                }],
                "manager_level": {
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
                },
                "manager_type": {
                    'uuid': "e34d4426-9845-4c72-b31e-709be85d6fa2"
                },
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }]

        self.assertRequestResponse('/service/details/edit',
                                   [manager_uuid], json=req)

        expected_manager = {
            "note": "Rediger leder",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederniveau",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "objekttype": "lederansvar",
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02",
                        }
                    },
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity",
                        }
                    },
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager, actual_manager)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [{
                'address': [{
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
                }],
                'manager_level': {
                    'example': None,
                    'name': 'Institut',
                    'scope': None,
                    'user_key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Afdeling',
                    'scope': None,
                    'user_key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
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
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': [{
                    'example': None,
                    'name': 'Fakultet',
                    'scope': None,
                    'user_key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                }],
                'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                'validity': {
                    'from': '2017-01-01',
                    'to': '2018-03-31',
                },
            }],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': [{
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
                }],
                'manager_level': {
                    'example': '20304060',
                    'name': 'Telefonnummer',
                    'scope': 'PHONE',
                    'user_key': 'Telefon',
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                'manager_type': {
                    'example': '5712345000014',
                    'name': 'EAN',
                    'scope': 'EAN',
                    'user_key': 'EAN',
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'org_unit': {
                    'name': 'Filosofisk Institut',
                    'user_key': 'fil',
                    'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                    'validity': {
                        'from': '2016-01-01', 'to': None,
                    },
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': [{
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': manager_uuid,
                'validity': {
                    'from': '2018-04-01', 'to': None,
                },
            }],
        )

    @util.mock('dawa-addresses.json', allow_mox=True)
    def test_edit_manager_overwrite(self, m):
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        req = [{
            "type": "manager",
            "uuid": manager_uuid,
            "original": {
                "org_unit": {
                    'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                },
                "person": {
                    "uuid": userid,
                },
                "responsibility": [{
                    'uuid': "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
                }],
                "manager_level": {
                    "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
                },
                "manager_type": {
                    'uuid': "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "validity": {
                    "from": "2017-01-01",
                    "to": None,
                },
            },
            "data": {
                "address": [
                    {
                        "address_type": {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'AdressePost',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        "uuid": "44c532e1-f617-4174-b144-d37ce9fda2bd",
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'AdressePost',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        },
                        'uuid': '606cf42e-9dc2-4477-bf70-594830fcbdec',
                    },
                ],
                "org_unit": {
                    'uuid': "85715fc7-925d-401b-822d-467eb4b163b6"
                },
                "responsibility": [{
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                }],
                "manager_level": {
                    "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec"
                },
                "manager_type": {
                    'uuid': "e34d4426-9845-4c72-b31e-709be85d6fa2"
                },
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }]

        self.assertRequestResponse('/service/details/edit',
                                   [manager_uuid], json=req)

        expected_manager = {
            "note": "Rediger leder",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': "2018-04-01 00:00:00+02",
                            'to_included': False,
                        },
                    },
                    {
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'uuid': '606cf42e-9dc2-4477-bf70-594830fcbdec',
                        'virkning': {
                            'from': '2018-04-01 00:00:00+02',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                    {
                        'objekttype': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'virkning': {
                            'from': "2018-04-01 00:00:00+02",
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager, actual_manager)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': [
                    {
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                        'name': 'Åbogade 15, 8200 Aarhus N',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Adresse',
                            'scope': 'DAR',
                            'user_key': 'AdressePost',
                            'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
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
                        '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                        'name': 'Åbogade 15, 1., 8200 Aarhus N',
                        'uuid': '606cf42e-9dc2-4477-bf70-594830fcbdec',
                    },
                ],
                'manager_level': {
                    'example': '20304060',
                    'name': 'Telefonnummer',
                    'scope': 'PHONE',
                    'user_key': 'Telefon',
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                'manager_type': {
                    'example': '5712345000014',
                    'name': 'EAN',
                    'scope': 'EAN',
                    'user_key': 'EAN',
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'org_unit': {
                    'name': 'Filosofisk Institut',
                    'user_key': 'fil',
                    'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                    'validity': {
                        'from': '2016-01-01',
                        'to': None,
                    },
                },
                'person': {
                    'name': 'Anders And',
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': [{
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                'validity': {
                    'from': '2018-04-01', 'to': None,
                },
            }],
        )

    @unittest.expectedFailure
    def test_edit_manager_handles_adapted_zero_to_many_field(self):
        """Edits of parts of the object should handle adapted zero-to-many
        fields correctly, i.e. multiple fields sharing the same
        relation should remain intact when only one of the
        fields are updated"""
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        req = [{
            "type": "manager",
            "uuid": manager_uuid,
            "data": {
                "responsibility": [{
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                }],
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }]

        self.assertRequestResponse('/service/details/edit',
                                   [manager_uuid], json=req)

        expected_manager = {
            "note": "Rediger leder",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "objekttype": "lederansvar",
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager, actual_manager)

    def test_terminate_manager(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "validity": {
                "to": "2017-11-30"
            }
        }

        self.assertRequestResponse('/service/e/{}/terminate'.format(userid),
                                   userid, json=payload)

        expected = {
            "note": "Afslut medarbejder",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-12-01 00:00:00+01"
                        }
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-12-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected, actual_manager)

        expected = {
            'address': [{
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
            }],
            'manager_level': {
                'example': None,
                'name': 'Institut',
                'scope': None,
                'user_key': 'inst',
                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
            },
            'manager_type': {
                'example': None,
                'name': 'Afdeling',
                'scope': None,
                'user_key': 'afd',
                'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
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
                'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
            },
            'responsibility': [{
                'example': None,
                'name': 'Fakultet',
                'scope': None,
                'user_key': 'fak',
                'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
            }],
            'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
            'validity': {
                'from': '2017-01-01',
                'to': '2017-11-30',
            },
        }

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [expected],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                **expected,
                'person': None,
                'validity': {'from': '2017-12-01', 'to': None},
            }],
        )

    def test_edit_manager_minimal(self):
        self.load_sample_structures()

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        expected_lora = {
            "note": "Automatisk indlæsning",
            "relationer": {
                'adresser': [
                    {
                        'objekttype': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        'urn': 'urn:mailto:ceo@example.com',
                        'virkning': {
                            'from': '2017-01-01 00:00:00+01',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                    },
                ],
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                    {
                        "objekttype": "lederniveau",
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
            },
            "livscykluskode": "Importeret",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                                             "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        expected_mora = [{
            'address': [{
                'address_type': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0'
                },
                'href': 'mailto:ceo@example.com',
                'name': 'ceo@example.com',
                'urn': 'urn:mailto:ceo@example.com'}],
            'manager_level': {'example': None,
                              'name': 'Institut',
                              'scope': None,
                              'user_key': 'inst',
                              'uuid': 'ca76a441-6226-404f-'
                              '88a9-31e02e420e52'},
            'manager_type': {'example': None,
                             'name': 'Afdeling',
                             'scope': None,
                             'user_key': 'afd',
                             'uuid': '32547559-cfc1-4d97-'
                             '94c6-70b192eff825'},
            'org_unit': {'name': 'Humanistisk fakultet',
                         'user_key': 'hum',
                         'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                         'validity': {'from': '2016-01-01',
                                      'to': None}},
            'person': {'name': 'Anders And',
                       'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a'},
            'responsibility': [{
                'example': None,
                'name': 'Fakultet',
                'scope': None,
                'user_key': 'fak',
                'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
            }],
            'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
            'validity': {'from': '2017-01-01',
                         'to': None}
        }]

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        with self.subTest('preconditions'):
            self.assertRegistrationsEqual(
                c.organisationfunktion.get(manager_uuid),
                expected_lora,
            )

            self.assertRequestResponse(
                '/service/e/{}/details/manager'.format(userid),
                expected_mora,
            )

            self.assertRequestResponse(
                '/service/e/{}/details/manager?validity=past'.format(userid),
                [],
            )

            self.assertRequestResponse(
                '/service/e/{}/details/manager?validity=future'.format(userid),
                [],
            )

        # perform the operation
        self.assertRequestResponse(
            '/service/details/edit',
            manager_uuid,
            json={
                "type": "manager",
                "uuid": manager_uuid,
                "data": {
                    "manager_type": {
                        'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"
                    },
                    "validity": {
                        "from": "2017-01-01",
                    },
                },
            },
        )

        # adjust the data as expected
        expected_changed_lora = copy.deepcopy(expected_lora)
        expected_changed_lora['note'] = 'Rediger leder'
        expected_changed_lora['livscykluskode'] = 'Rettet'
        expected_changed_lora['relationer']['organisatoriskfunktionstype'][0][
            'uuid'] = "ca76a441-6226-404f-88a9-31e02e420e52"

        for g, f in (
                ('attributter', 'organisationfunktionegenskaber'),
                ('relationer', 'adresser'),
                ('relationer', 'opgaver'),
                ('relationer', 'organisatoriskfunktionstype'),
                ('relationer', 'tilknyttedebrugere'),
                ('relationer', 'tilknyttedeenheder'),
                ('relationer', 'tilknyttedeorganisationer'),
                ('tilstande', 'organisationfunktiongyldighed'),
        ):
            for m in expected_changed_lora[g][f]:
                m['virkning']['from'] = '2017-01-01 00:00:00+01'

        expected_mora[0]['validity']['from'] = '2017-01-01'
        expected_mora[0]['manager_type'] = {
            'example': None,
            'name': 'Institut',
            'scope': None,
            'user_key': 'inst',
            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
        }

        # compare them!
        actual_lora = c.organisationfunktion.get(manager_uuid)

        with self.subTest('LoRA'):
            self.assertRegistrationsNotEqual(actual_lora, expected_lora,
                                             "the edit didn't take :(")
            self.assertRegistrationsEqual(expected_changed_lora, actual_lora,
                                          "wrong results!")

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            expected_mora,
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager?validity=past'.format(userid),
            [],
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager?validity=future'.format(userid),
            [],
        )

    def test_read_manager_multiple_responsibilities(self):
        '''Test reading a manager with multiple responsibilities, all valid'''
        self.load_sample_structures()

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        # inject multiple responsibilities
        c = lora.Connector()

        overwritten_responsibilities = [
            {
                "objekttype": "lederansvar",
                "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                "virkning": {
                    "from": "2017-01-01 00:00:00+01",
                    "from_included": True,
                    "to": "infinity",
                    "to_included": False,
                }
            },
            {
                "objekttype": "lederansvar",
                "uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
                "virkning": {
                    "from": "2017-01-01 00:00:00+01",
                    "from_included": True,
                    "to": "infinity",
                    "to_included": False,
                }
            },
            {
                "objekttype": "lederniveau",
                "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                "virkning": {
                    "from": "2017-01-01 00:00:00+01",
                    "from_included": True,
                    "to": "infinity",
                    "to_included": False,
                }
            },
        ]

        c.organisationfunktion.update(
            {
                'relationer': {
                    'opgaver': overwritten_responsibilities,
                }
            },
            manager_uuid,
        )

        with self.subTest('verify assumption about relation in LoRA'):
            self.assertEqual(
                sorted(
                    c.organisationfunktion.get(manager_uuid)
                    ['relationer']['opgaver'],
                    key=mora_util.get_uuid,
                ),
                overwritten_responsibilities,
            )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [
                {
                    'address': [{
                        'address_type': {
                            'example': 'test@example.com',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                        },
                        'href': 'mailto:ceo@example.com',
                        'name': 'ceo@example.com',
                        'urn': 'urn:mailto:ceo@example.com',
                    }],
                    'manager_level': {
                        'example': None,
                        'name': 'Institut',
                        'scope': None,
                        'user_key': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                    },
                    'manager_type': {
                        'example': None,
                        'name': 'Afdeling',
                        'scope': None,
                        'user_key': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
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
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    'responsibility': [
                        {
                            'example': None,
                            'name': 'Medlem',
                            'scope': None,
                            'user_key': 'medl',
                            'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                        },
                        {
                            'example': None,
                            'name': 'Fakultet',
                            'scope': None,
                            'user_key': 'fak',
                            'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                        },
                    ],
                    'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                    'validity': {
                        'from': '2017-01-01',
                        'to': None,
                    },
                },
            ],
        )

    @util.mock(allow_mox=True)
    def test_create_manager_offline(self, m):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {'uuid': userid},
                'address': [{
                    'href': 'https://www.openstreetmap.org/'
                    '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                    'name': 'Åbogade 15, 8200 Aarhus N',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                }],
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
            }
        ]

        managerid, = self.assertRequest('/service/details/create',
                                        json=payload)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                'address': [{
                    'href': None,
                    'name': 'Fejl',
                    'error': 'No mock address: '
                    'GET https://dawa.aws.dk/adresser'
                    '?id=44c532e1-f617-4174-b144-d37ce9fda2bd'
                    '&noformat=1&struktur=mini',
                    'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                    'address_type': {
                        'example': '<UUID>',
                        'name': 'Adresse',
                        'scope': 'DAR',
                        'user_key': 'AdressePost',
                        'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed',
                    },
                }],
                'manager_level': {
                    'example': 'test@example.com',
                    'name': 'Emailadresse',
                    'scope': 'EMAIL',
                    'user_key': 'Email',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
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
                    'name': 'Fedtmule',
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': [{
                    'example': None,
                    'name': 'Medlem',
                    'scope': None,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': managerid,
                'validity': {
                    'from': '2017-12-01',
                    'to': '2017-12-01',
                },
            }],
        )
