# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import unittest

import freezegun
import notsouid
from unittest.mock import patch

from mora import lora
from mora import util as mora_util
from tests import util

mock_uuid = '1eb680cd-d8ec-4fd2-8ca0-dce2d03f59a5'


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@patch('uuid.uuid4', new=lambda: mock_uuid)
@patch('mora.conf_db.get_configuration',
       new=lambda *x: {})
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_manager_missing_unit(self):
        self.load_sample_structures()

        # Check the POST request
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

    @notsouid.freeze_uuid('11111111-1111-1111-1111-111111111111',
                          auto_increment=True)
    def test_create_manager(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "manager",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "person": {'uuid': userid},
                "responsibility": [
                    {'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                    {'uuid': "ca76a441-6226-404f-88a9-31e02e420e52"},
                ],
                "manager_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                "manager_level": {
                    "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
                },
                "user_key": "1234",
                "validity": {
                    "from": "2017-12-01",
                    "to": "2017-12-01",
                },
            }
        ]

        managerid, = self.assertRequest(
            '/service/details/create',
            json=payload,
            amqp_topics={
                'employee.manager.create': 1,
                'org_unit.manager.create': 1,
            },
        )

        expected = {
            "livscykluskode": "Importeret",
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
                "opgaver": [
                    {
                        "objekttype": "lederansvar",
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "ca76a441-6226-404f-88a9-31e02e420e52",
                    },
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
                        "brugervendtnoegle": "1234",
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
            amqp_topics={
                'employee.manager.create': 1,
                'org_unit.manager.create': 1,
            },
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future&only_primary_uuid=1'.format(userid),
            [{
                'address': [],
                'manager_level': {
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                },
                'org_unit': {
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                },
                'person': {
                    'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
                },
                'responsibility': [
                    {
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                    },
                    {
                        'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                    },
                ],
                'uuid': managerid,
                'user_key': '1234',
                'validity': {
                    'from': '2017-12-01',
                    'to': '2017-12-01',
                },
            }],
            amqp_topics={
                'employee.manager.create': 1,
                'org_unit.manager.create': 1,
            },
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
            amqp_topics={'org_unit.manager.create': 1},
        )

        employee_address_type_facet = {
            'description': '',
            'user_key': 'employee_address_type',
            'uuid': 'baddc4eb-406e-4c6b-8229-17e4a21d3550'
        }
        association_type_facet = {
            'description': '',
            'user_key': 'association_type',
            'uuid': 'ef71fe9c-7901-48e2-86d8-84116e210202'
        }

        self.assertRequestResponse(
            '/service/ou/{}/details/manager'.format(unit_id),
            [{
                'address': [],
                'manager_level': {
                    'example': 'test@example.com',
                    'facet': employee_address_type_facet,
                    'full_name': 'Email',
                    'name': 'Email',
                    'scope': 'EMAIL',
                    'top_level_facet': employee_address_type_facet,
                    'user_key': 'BrugerEmail',
                    'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
                },
                'manager_type': {
                    'example': None,
                    'facet': association_type_facet,
                    'full_name': 'Medlem',
                    'name': 'Medlem',
                    'scope': None,
                    'top_level_facet': association_type_facet,
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
                    'facet': association_type_facet,
                    'full_name': 'Medlem',
                    'name': 'Medlem',
                    'scope': None,
                    'top_level_facet': association_type_facet,
                    'user_key': 'medl',
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': function_id,
                'user_key': mock_uuid,
                'validity': {'from': '2016-12-01', 'to': '2017-12-02'},
            }],
            amqp_topics={'org_unit.manager.create': 1},
        )

    def test_edit_manager_on_unit(self):
        self.load_sample_structures()

        unit_id = "da77153e-30f3-4dc2-a611-ee912a28d8aa"
        user_id = "6ee24785-ee9a-4502-81c2-7697009c9053"

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
            amqp_topics={
                'org_unit.manager.create': 1,
                'employee.manager.create': 1,
            },
        )

        expected = {
            'user_key': mock_uuid,
            'address': [],
            'manager_level': {
                'uuid': 'c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0',
            },
            'manager_type': {
                'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
            },
            'org_unit': {
                'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
            },
            'person': {
                'uuid': '6ee24785-ee9a-4502-81c2-7697009c9053',
            },
            'responsibility': [{
                'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
            }],
            'validity': {'from': '2016-12-01', 'to': '2017-12-02'},
        }

        with self.subTest('results'):
            expected['uuid'] = function_id

            self.assertRequestResponse(
                '/service/ou/{}/details/manager?only_primary_uuid=1'.format(unit_id),
                [expected],
                amqp_topics={
                    'org_unit.manager.create': 1,
                    'employee.manager.create': 1,
                },
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
                amqp_topics={
                    'org_unit.manager.create': 1,
                    'employee.manager.create': 1,
                    'org_unit.manager.update': 1,
                    'employee.manager.update': 1,
                },
            )

            future = expected.copy()
            future['person'] = None
            future['validity'] = {
                "from": "2017-12-03",
                "to": "2017-12-20",
            }

            self.assertRequestResponse(
                '/service/ou/{}/details/manager?only_primary_uuid=1'.format(unit_id),
                [expected],
                amqp_topics={
                    'org_unit.manager.create': 1,
                    'employee.manager.create': 1,
                    'org_unit.manager.update': 1,
                    'employee.manager.update': 1,
                },
            )

            self.assertRequestResponse(
                '/service/ou/{}/details/manager?only_primary_uuid=1'
                '&validity=future'.format(unit_id),
                [future],
                amqp_topics={
                    'org_unit.manager.create': 1,
                    'employee.manager.create': 1,
                    'org_unit.manager.update': 1,
                    'employee.manager.update': 1,
                },
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
                "user_key": "kaflaflibob",
                "validity": {
                    "from": "2018-04-01",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/details/edit',
            [manager_uuid],
            json=req,
            amqp_topics={
                'org_unit.manager.update': 1,
                'employee.manager.update': 1,
            },
        )

        expected_manager = {
            "note": "Rediger leder",
            "relationer": {
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
                'tilknyttedefunktioner': [{
                    'uuid': '414044e0-fe5f-4f82-be20-1e107ad50e80',
                    'virkning': {
                        'from': '2017-01-01 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
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
                            "to": "2018-04-01 00:00:00+02",
                        },
                        "brugervendtnoegle": "be736ee5-5c44-4ed9-"
                        "b4a4-15ffa19e2848",
                        "funktionsnavn": "Leder"
                    },
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "kaflaflibob",
                        "funktionsnavn": "Leder"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager, actual_manager)

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future&only_primary_uuid=1'.format(userid),
            [{
                'address': [{
                    'address_type': {'uuid': '28d71012-2919-4b67-a2f0-7b59ed52561e'},
                    'href': 'https://www.openstreetmap.org/?mlon=10.19938084'
                            '&mlat=56.17102843&zoom=16',
                    'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                    'uuid': '414044e0-fe5f-4f82-be20-1e107ad50e80',
                    'value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197'
                }],
                'manager_level': {
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                'manager_type': {
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'org_unit': {
                    'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                },
                'person': {
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': [{
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': manager_uuid,
                'user_key': 'kaflaflibob',
                'validity': {
                    'from': '2018-04-01', 'to': None,
                },
            }],
            amqp_topics={
                'org_unit.manager.update': 1,
                'employee.manager.update': 1,
            },
        )

    def test_edit_manager_overwrite(self):
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

        self.assertRequestResponse(
            '/service/details/edit',
            [manager_uuid],
            json=req,
            amqp_topics={
                'org_unit.manager.update': 1,
                'employee.manager.update': 1,
            },
        )

        expected_manager = {
            "note": "Rediger leder",
            "relationer": {
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
                'tilknyttedefunktioner': [{
                    'uuid': '414044e0-fe5f-4f82-be20-1e107ad50e80',
                    'virkning': {
                        'from': '2017-01-01 00:00:00+01',
                        'from_included': True,
                        'to': 'infinity',
                        'to_included': False
                    }
                }],
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
            '/service/e/{}/details/manager'
            '?validity=future&only_primary_uuid=1'.format(userid),
            [{
                'address': [{
                    'address_type': {'uuid': '28d71012-2919-4b67-a2f0-7b59ed52561e'},
                    'href': 'https://www.openstreetmap.org/?mlon=10.19938084'
                            '&mlat=56.17102843&zoom=16',
                    'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                    'uuid': '414044e0-fe5f-4f82-be20-1e107ad50e80',
                    'value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197'
                }],
                'manager_level': {
                    'uuid': '1d1d3711-5af4-4084-99b3-df2b8752fdec',
                },
                'manager_type': {
                    'uuid': 'e34d4426-9845-4c72-b31e-709be85d6fa2',
                },
                'org_unit': {
                    'uuid': '85715fc7-925d-401b-822d-467eb4b163b6',
                },
                'person': {
                    'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                },
                'responsibility': [{
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                }],
                'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                'user_key': 'be736ee5-5c44-4ed9-b4a4-15ffa19e2848',
                'validity': {
                    'from': '2018-04-01', 'to': None,
                },
            }],
            amqp_topics={
                'org_unit.manager.update': 1,
                'employee.manager.update': 1,
            },
        )

    @unittest.expectedFailure
    def test_edit_manager_handles_adapted_zero_to_many_field(self):
        """Edits of parts of the object should handle adapted zero-to-many
        fields correctly, i.e. multiple fields sharing the same
        relation should remain intact when only one of the
        fields are updated"""
        self.load_sample_structures()

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

        self.assertRequestResponse(
            '/service/details/edit',
            [manager_uuid],
            json=req,
            amqp_topics={
                'org_unit.manager.update': 1,
                'employee.manager.update': 1,
            },
        )

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
            '/service/e/{}/details/manager?only_primary_uuid=1'.format(userid),
            [
                {
                    'address': [{
                        'address_type': {
                            'uuid': '28d71012-2919-4b67-a2f0-7b59ed52561e'
                        },
                        'href': 'https://www.openstreetmap.org/?mlon=10.19938084'
                                '&mlat=56.17102843&zoom=16',
                        'name': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'uuid': '414044e0-fe5f-4f82-be20-1e107ad50e80',
                        'value': 'b1f1817d-5f02-4331-b8b3-97330a5d3197'
                    }],
                    'manager_level': {
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                    },
                    'manager_type': {
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'org_unit': {
                        'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    },
                    'person': {
                        'uuid': '53181ed2-f1de-4c4a-a8fd-ab358c2c454a',
                    },
                    'responsibility': [
                        {
                            'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                        },
                        {
                            'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                        },
                    ],
                    'uuid': '05609702-977f-4869-9fb4-50ad74c6999a',
                    'user_key': 'be736ee5-5c44-4ed9-b4a4-15ffa19e2848',
                    'validity': {
                        'from': '2017-01-01',
                        'to': None,
                    },
                },
            ],
        )

    def test_read_no_inherit_manager(self):
        self.load_sample_structures()
        # Anders And is manager at humfak
        filins = '85715fc7-925d-401b-822d-467eb4b163b6'
        # We are NOT allowed to inherit Anders And
        inherited_managers = self.assertRequest(
            '/service/ou/{}/details/manager'.format(filins)
        )
        self.assertEqual(inherited_managers, [])

    def test_read_inherit_manager_one_level(self):
        self.load_sample_structures()
        # Anders And is manager at humfak
        humfak = '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
        # There is no manager at filins
        filins = '85715fc7-925d-401b-822d-467eb4b163b6'
        # We must inherit Anders And
        inherited_managers = self.assertRequest(
            '/service/ou/{}/details/manager?inherit_manager=1'.format(
                filins
            )
        )
        self.assertEqual(len(inherited_managers), 1)
        self.assertEqual(inherited_managers[0]["org_unit"]["uuid"], humfak)

    def test_read_inherit_manager_none_found_all_the_way_up(self):
        self.load_sample_structures()
        # There is no manager at samfak
        samfak = 'b688513d-11f7-4efc-b679-ab082a2055d0'
        # We must not find no managers
        inherited_managers = self.assertRequest(
            '/service/ou/{}/details/manager?inherit_manager=1'.format(samfak)
        )
        self.assertEqual(inherited_managers, [])
