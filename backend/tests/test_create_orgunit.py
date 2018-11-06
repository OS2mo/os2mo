#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from mora.common import (create_organisationsenhed_payload)


class TestCreateOrgFunk(unittest.TestCase):
    maxDiff = None

    def test_create_organisationenhed(self):
        output_org_unit = {
            'attributter': {
                'organisationenhedegenskaber': [{
                    'enhedsnavn': 'enhedsnavn',
                    'brugervendtnoegle': 'brugervendtnoegle',
                    'integrationsdata':'',
                    'virkning': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': '2018-01-01T00:00:00+01:00'
                    }
                }]
            },
            'note': 'Oprettet i MO',
            'relationer': {
                'adresser': [
                    {
                        "uuid": "3491846c-ca4f-4339-a447-526fb0bfce55",
                        'virkning': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': '2018-01-01T00:00:00+01:00'
                        }
                    },
                    {
                        "uuid": "aff9cef9-52be-46a0-9db7-14b4bb259cce",
                        'virkning': {
                            'from': '2016-01-01T00:00:00+01:00',
                            'to': '2018-01-01T00:00:00+01:00'
                        }
                    }
                ],
                'overordnet': [{
                    'uuid': '47145ce1-c702-42c2-a88e-011eb09d250f',
                    'virkning': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': '2018-01-01T00:00:00+01:00'
                    }
                }],
                'tilhoerer': [{
                    'uuid': 'e0f7a6f7-2a76-45dc-b326-d49b4bb2c2b9',
                    'virkning': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': '2018-01-01T00:00:00+01:00'
                    }
                }],
                'enhedstype': [{
                    'uuid': '28d3c9f6-cce0-4649-bf73-ccbb78dc04e4',
                    'virkning': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': '2018-01-01T00:00:00+01:00'
                    }
                }],
            },
            'tilstande': {
                'organisationenhedgyldighed': [{
                    'virkning': {
                        'from': '2016-01-01T00:00:00+01:00',
                        'to': '2018-01-01T00:00:00+01:00'
                    },
                    'gyldighed': 'Aktiv'
                }]
            }
        }

        enhedsnavn = "enhedsnavn"
        valid_from = "2016-01-01T00:00:00+01:00"
        valid_to = "2018-01-01T00:00:00+01:00"
        brugervendtnoegle = "brugervendtnoegle"
        adresser = [
            {
                "uuid": "3491846c-ca4f-4339-a447-526fb0bfce55",
            },
            {
                "uuid": "aff9cef9-52be-46a0-9db7-14b4bb259cce"
            }
        ]
        tilhoerer = "e0f7a6f7-2a76-45dc-b326-d49b4bb2c2b9"
        enhedstype = "28d3c9f6-cce0-4649-bf73-ccbb78dc04e4"
        overordnet = "47145ce1-c702-42c2-a88e-011eb09d250f"

        self.assertEqual(
            create_organisationsenhed_payload(
                enhedsnavn=enhedsnavn,
                valid_from=valid_from,
                valid_to=valid_to,
                brugervendtnoegle=brugervendtnoegle,
                adresser=adresser,
                tilhoerer=tilhoerer,
                enhedstype=enhedstype,
                overordnet=overordnet
            ),
            output_org_unit)
