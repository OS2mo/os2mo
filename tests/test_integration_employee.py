#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun
import notsouid

from mora import lora
from . import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_employee(self):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        payload = {
            "name": "Torkild Testperson",
            "cpr_no": "0101501234",
            "org": {
                'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
            }
        }

        mock_uuid = "b6c268d2-4671-4609-8441-6029077d8efc"

        with notsouid.freeze_uuid(mock_uuid):
            r = self._perform_request('/service/e/create', json=payload)
        userid = r.json

        expected = {
            "livscykluskode": "Opstaaet",
            "note": "Oprettet i MO",
            "attributter": {
                "brugeregenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "1950-01-01 00:00:00+01"
                        },
                        "brugervendtnoegle": mock_uuid,
                        "brugernavn": "Torkild Testperson"
                    }
                ]
            },
            "relationer": {
                "tilhoerer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "1950-01-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedepersoner": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "1950-01-01 00:00:00+01"
                        },
                        "urn": "urn:dk:cpr:person:0101501234"
                    }
                ],
            },
            "tilstande": {
                "brugergyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "1950-01-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
        }

        actual = c.bruger.get(userid)

        self.assertRegistrationsEqual(expected, actual)

        self.assertRequestResponse(
            '/service/e/{}/'.format(userid),
            {
                'name': 'Torkild Testperson',
                'org': {
                    'name': 'Aarhus Universitet',
                    'user_key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'cpr_no': '0101501234',
                'uuid': userid,
            },
        )

    def test_create_employee_fails_on_empty_payload(self):
        self.load_sample_structures()

        payload = {}

        self.assertRequestFails(
            '/service/e/create', 400,
            json=payload)

    def test_cpr_lookup_prod_mode_false(self):
        # Arrange
        cpr = "0101501234"

        expected = {
            'name': 'Merle Mortensen',
            'cpr_no': cpr
        }

        # Act
        with util.override_settings(PROD_MODE=False):
            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q={}'.format(cpr),
                expected)

    def test_cpr_lookup_raises_on_wrong_length(self):
        # Arrange

        # Act
        self.assertRequestFails('/service/e/cpr_lookup/?q=1234/', 400)
        self.assertRequestFails('/service/e/cpr_lookup/?q=1234567890123/',
                                400)
