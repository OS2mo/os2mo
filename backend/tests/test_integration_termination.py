#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
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

        self.assertRequestResponse('/service/e/{}/terminate'.format(userid),
                                   userid, json=payload)

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
            "terminate_all": True
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

        self.assertRequestResponse('/service/e/{}/terminate'.format(userid),
                                   userid, json=payload)

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
