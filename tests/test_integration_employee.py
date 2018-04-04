#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
from unittest.mock import patch

import freezegun

from mora import lora, settings
from mora.service import employee, orgunit
from . import util

mock_uuid = 'f494ad89-039d-478e-91f2-a63566554bd6'


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@patch('mora.service.employee.uuid4', new=lambda: mock_uuid)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_employee(self):
        self.load_sample_structures()

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        payload = {
            "name": "Torkild Testperson",
            "cpr_no": "1234567890",
            "org": {
                'uuid': "456362c4-0ee4-4e5e-a72c-751239745e62"
            }
        }

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
                            "from": "2017-01-01 01:00:00+01"
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
                            "from": "2017-01-01 01:00:00+01"
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
                            "from": "2017-01-01 01:00:00+01"
                        },
                        "urn": "urn:dk:cpr:person:1234567890"
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
                            "from": "2017-01-01 01:00:00+01"
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
                'cpr_no': '1234567890',
                'uuid': userid,
            },
        )

    def test_cpr_lookup_prod_mode_false(self):
        # Arrange
        settings.PROD_MODE = False

        cpr = "1234567890"

        expected = {
            'name': 'Sarah Kristensen',
            'cpr_no': cpr
        }

        # Act
        self.assertRequestResponse('/service/e/cpr_lookup/{}/'.format(cpr),
                                   expected)

    def test_cpr_lookup_raises_on_wrong_length(self):
        # Arrange

        # Act
        self.assertRequestFails('/service/e/cpr_lookup/1234/', 400)
        self.assertRequestFails('/service/e/cpr_lookup/1234567890123/', 400)
