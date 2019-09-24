#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy

import freezegun

from mora import lora

from . import util


class Tests(util.LoRATestCase):
    @freezegun.freeze_time('2000-12-01')
    def test_terminate_employee(self):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "vacate": True,
            "validity": {
                "to": "2000-12-01"
            }
        }

        # None of these should be activate at this point in time,
        # and should therefore remain unaffected by the termination request

        engagement_uuid = 'd000591f-8705-4324-897a-075e3623f37b'
        association_uuid = 'c2153d5d-4a2b-492d-a18c-c498f7bb6221'
        role_uuid = '1b20d0b9-96a0-42a6-b196-293bb86e62e8'
        leave_uuid = 'b807628c-030c-4f5f-a438-de41c1f26ba5'
        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        def get_expected(id, is_manager=False):
            o = c.organisationfunktion.get(id)

            o.update(
                livscykluskode='Rettet',
                note='Afsluttet',
            )

            if is_manager:
                del o['relationer']['tilknyttedebrugere'][0]['uuid']
            else:
                v = o['tilstande']['organisationfunktiongyldighed']
                v[0]['gyldighed'] = 'Inaktiv'

            return o

        expected_engagement = get_expected(engagement_uuid)
        expected_association = get_expected(association_uuid)
        expected_role = get_expected(role_uuid)
        expected_leave = get_expected(leave_uuid)
        expected_manager = get_expected(manager_uuid, True)

        self.assertRequestResponse(
            '/service/e/{}/terminate'.format(userid),
            userid,
            json=payload,
            amqp_topics={
                'employee.address.delete': 1,
                'employee.association.delete': 1,
                'employee.engagement.delete': 1,
                'employee.employee.delete': 1,
                'employee.leave.delete': 1,
                'employee.manager.delete': 1,
                'employee.it.delete': 1,
                'employee.role.delete': 1,
                'org_unit.association.delete': 1,
                'org_unit.engagement.delete': 1,
                'org_unit.manager.delete': 1,
                'org_unit.role.delete': 1,
            },
        )

        actual_engagement = c.organisationfunktion.get(engagement_uuid)
        actual_association = c.organisationfunktion.get(association_uuid)
        actual_role = c.organisationfunktion.get(role_uuid)
        actual_leave = c.organisationfunktion.get(leave_uuid)
        actual_manager = c.organisationfunktion.get(manager_uuid)

        with self.subTest('engagement'):
            self.assertRegistrationsEqual(expected_engagement,
                                          actual_engagement)

        with self.subTest('association'):
            self.assertRegistrationsEqual(expected_association,
                                          actual_association)

        with self.subTest('role'):
            self.assertRegistrationsEqual(expected_role,
                                          actual_role)

        with self.subTest('leave'):
            self.assertRegistrationsEqual(expected_leave,
                                          actual_leave)

        with self.subTest('manager'):
            self.assertRegistrationsEqual(expected_manager,
                                          actual_manager)

    @freezegun.freeze_time('2018-01-01')
    def test_terminate_employee_in_the_past_fails(self):
        """Terminating employees in the past should fail"""
        self.load_sample_structures()

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "validity": {
                "to": "2000-12-01"
            }
        }

        self.assertRequestResponse(
            '/service/e/{}/terminate'.format(userid),
            {
                'date': '2000-12-02T00:00:00+01:00',
                'description': 'Cannot perform changes before current date',
                'error': True,
                'error_key': 'V_CHANGING_THE_PAST',
                'status': 400
            },
            status_code=400,
            json=payload)

    @freezegun.freeze_time('2000-12-01')
    def test_terminate_employee_manager_full(self):
        """Ensure that managers are terminated as well, when run with 'full'"""
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "validity": {
                "to": "2000-12-01"
            },
            "vacate": False,
        }

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        def get_expected(id, is_manager=False):
            o = c.organisationfunktion.get(id)

            o.update(
                livscykluskode='Rettet',
                note='Afsluttet',
            )

            v = o['tilstande']['organisationfunktiongyldighed']
            v[0]['gyldighed'] = 'Inaktiv'

            return o

        expected_manager = get_expected(manager_uuid, True)

        self.assertRequestResponse(
            '/service/e/{}/terminate'.format(userid),
            userid,
            json=payload,
            amqp_topics={
                'employee.address.delete': 1,
                'employee.association.delete': 1,
                'employee.employee.delete': 1,
                'employee.engagement.delete': 1,
                'employee.leave.delete': 1,
                'employee.manager.delete': 1,
                'employee.it.delete': 1,
                'employee.role.delete': 1,
                'org_unit.association.delete': 1,
                'org_unit.engagement.delete': 1,
                'org_unit.manager.delete': 1,
                'org_unit.role.delete': 1,
            },
        )

        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager,
                                      actual_manager)

    @freezegun.freeze_time('2018-01-01')
    def test_validation_missing_validity(self):
        self.load_sample_structures()

        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        for req in (
                {
                    "type": "manager",
                    "uuid": manager_uuid,
                },
                {
                    "type": "manager",
                    "uuid": manager_uuid,
                    "validity": {},
                },
                {
                    "type": "manager",
                    "uuid": manager_uuid,
                    "validity": {
                        "from": "2000-12-01",
                    },
                },
        ):
            with self.subTest(req):
                self.assertRequestResponse(
                    '/service/details/terminate',
                    {
                        'description': 'Missing validity',
                        'error': True,
                        'error_key': 'V_MISSING_REQUIRED_VALUE',
                        'key': 'validity',
                        'obj': req,
                        'status': 400,
                    },
                    status_code=400,
                    json=req,
                )

        with self.subTest('invalid type'):
            self.assertRequestFails(
                '/service/details/terminate',
                404,
                json={
                    "type": "association",
                    "uuid": manager_uuid,
                    "validity": {
                        "to": "2018-01-01",
                    },
                },
            )

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_terminate_manager_via_user(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        payload = {
            "vacate": True,
            "validity": {
                "to": "2017-11-30"
            }
        }
        self.assertRequestResponse(
            '/service/e/{}/terminate'.format(userid),
            userid,
            json=payload,
            amqp_topics={
                'employee.address.delete': 1,
                'employee.association.delete': 1,
                'employee.engagement.delete': 1,
                'employee.employee.delete': 1,
                'employee.leave.delete': 1,
                'employee.manager.delete': 1,
                'employee.it.delete': 1,
                'employee.role.delete': 1,
                'org_unit.association.delete': 1,
                'org_unit.engagement.delete': 1,
                'org_unit.manager.delete': 1,
                'org_unit.role.delete': 1,
            },
        )

        expected_manager = {
            **c.organisationfunktion.get(manager_uuid),

            "note": "Afsluttet",
            "livscykluskode": "Rettet",
        }

        expected_manager['relationer']['tilknyttedebrugere'] = [
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
        ]

        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager, actual_manager)

        expected = {
            'address': [{
                'address_type': {
                    'example': '<UUID>',
                    'name': 'Adresse',
                    'scope': 'DAR',
                    'user_key': 'AdressePost',
                    'uuid': '4e337d8e-1fd2-4449-8110-e0c8a22958ed'
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
                'givenname': 'Anders',
                'surname': 'And',
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
            'user_key': 'be736ee5-5c44-4ed9-b4a4-15ffa19e2848',
            'validity': {
                'from': '2017-01-01',
                'to': '2017-11-30',
            },
        }

        self.assertRequestResponse(
            '/service/e/{}/details/manager'.format(userid),
            [expected],
            amqp_topics={
                'employee.address.delete': 1,
                'employee.association.delete': 1,
                'employee.employee.delete': 1,
                'employee.engagement.delete': 1,
                'employee.leave.delete': 1,
                'employee.manager.delete': 1,
                'employee.it.delete': 1,
                'employee.role.delete': 1,
                'org_unit.association.delete': 1,
                'org_unit.engagement.delete': 1,
                'org_unit.manager.delete': 1,
                'org_unit.role.delete': 1,
            },
        )

        self.assertRequestResponse(
            '/service/e/{}/details/manager'
            '?validity=future'.format(userid),
            [{
                **expected,
                'person': None,
                'validity': {'from': '2017-12-01', 'to': None},
            }],
            amqp_topics={
                'employee.address.delete': 1,
                'employee.association.delete': 1,
                'employee.employee.delete': 1,
                'employee.engagement.delete': 1,
                'employee.leave.delete': 1,
                'employee.manager.delete': 1,
                'employee.it.delete': 1,
                'employee.role.delete': 1,
                'org_unit.association.delete': 1,
                'org_unit.engagement.delete': 1,
                'org_unit.manager.delete': 1,
                'org_unit.role.delete': 1,
            },
        )

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_terminate_manager_properly_via_user(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        payload = {
            "vacate": False,
            "validity": {
                "to": "2017-11-30"
            }
        }

        self.assertRequestResponse(
            '/service/e/{}/terminate'.format(userid),
            userid,
            json=payload,
            amqp_topics={
                'employee.address.delete': 1,
                'employee.association.delete': 1,
                'employee.employee.delete': 1,
                'employee.engagement.delete': 1,
                'employee.leave.delete': 1,
                'employee.manager.delete': 1,
                'employee.it.delete': 1,
                'employee.role.delete': 1,
                'org_unit.association.delete': 1,
                'org_unit.engagement.delete': 1,
                'org_unit.manager.delete': 1,
                'org_unit.role.delete': 1,
            },
        )

        expected_manager = {
            **c.organisationfunktion.get(manager_uuid),

            "note": "Afsluttet",
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-12-01 00:00:00+01"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-12-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },

        }

        actual_manager = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected_manager, actual_manager)

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_terminate_manager_directly(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
        manager_uuid = '05609702-977f-4869-9fb4-50ad74c6999a'

        original_manager = self.assertRequest(
            '/service/e/{}/details/manager'.format(userid),
        )

        original = c.organisationfunktion.get(manager_uuid)

        self.assertRequestResponse(
            '/service/details/terminate',
            manager_uuid,
            json={
                "type": "manager",
                "uuid": manager_uuid,
                "validity": {
                    "to": "2017-11-30"
                }
            },
            amqp_topics={
                'employee.manager.delete': 1,
                'org_unit.manager.delete': 1,
            },
        )

        expected = copy.deepcopy(original)
        expected.update(
            livscykluskode="Rettet",
            note="Afsluttet",
            tilstande={
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-12-01 00:00:00+01"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-12-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
        )

        actual = c.organisationfunktion.get(manager_uuid)

        self.assertRegistrationsEqual(expected, actual)

        with self.subTest('current'):
            current = copy.deepcopy(original_manager)
            current[0]['validity']['to'] = '2017-11-30'

            self.assertRequestResponse(
                '/service/e/{}/details/manager'.format(userid),
                current,
                amqp_topics={
                    'employee.manager.delete': 1,
                    'org_unit.manager.delete': 1,
                },
            )

        with self.subTest('future'):
            self.assertRequestResponse(
                '/service/e/{}/details/manager'
                '?validity=future'.format(userid),
                [],
                amqp_topics={
                    'employee.manager.delete': 1,
                    'org_unit.manager.delete': 1,
                },
            )
