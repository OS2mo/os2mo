#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from mora.service.employee import create_engagement_payload


class TestCreateRole(unittest.TestCase):
    maxDiff = None

    def test_should_create_engagement_correctly(self):
        employee_uuid = '0b745aa2-6cf8-44a7-a7bc-9b7f75ce0ad6'

        req = {
            "type": "engagement",
            "org_unit_uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec",
            "org_uuid": "f494ad89-039d-478e-91f2-a63566554bd6",
            "job_title_uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
            "engagement_type_uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
            "valid_from": "2016-01-01T00:00:00+00:00",
            "valid_to": "2018-01-01T00:00:00+00:00",
        }

        output_org_funk = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'funktionsnavn': 'Engagement',
                    'brugervendtnoegle': '0b745aa2-6cf8-44a7-a7bc-'
                                         '9b7f75ce0ad6 a30f5f68-9c0d-44e9-'
                                         'afc9-04e58f52dfec',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'from': '2016-01-01T00:00:00+00:00',
                        'to': '2018-01-01T00:00:00+00:00'
                    }
                }]
            },
            'note': 'Oprettet i MO',
            'relationer': {
                'tilknyttedeenheder': [{
                    'uuid': 'a30f5f68-9c0d-44e9-afc9-04e58f52dfec',
                    'virkning': {
                        'to_included': False, 'from_included': True,
                        'from': '2016-01-01T00:00:00+00:00',
                        'to': '2018-01-01T00:00:00+00:00'
                    }
                }],
                'tilknyttedebrugere': [{
                    'uuid': '0b745aa2-6cf8-44a7-a7bc-9b7f75ce0ad6',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'from': '2016-01-01T00:00:00+00:00',
                        'to': '2018-01-01T00:00:00+00:00'
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': '62ec821f-4179-4758-bfdf-134529d186e9',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'from': '2016-01-01T00:00:00+00:00',
                        'to': '2018-01-01T00:00:00+00:00'
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': 'f494ad89-039d-478e-91f2-a63566554bd6',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'from': '2016-01-01T00:00:00+00:00',
                        'to': '2018-01-01T00:00:00+00:00'
                    }
                }],
                'opgaver': [{
                    'uuid': '3ef81e52-0deb-487d-9d0e-a69bbe0277d8',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'from': '2016-01-01T00:00:00+00:00',
                        'to': '2018-01-01T00:00:00+00:00'
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'from': '2016-01-01T00:00:00+00:00',
                        'to': '2018-01-01T00:00:00+00:00'
                    },
                    'gyldighed': 'Aktiv'
                }]
            }
        }

        self.assertDictEqual(create_engagement_payload(employee_uuid, req),
                             output_org_funk,
                             'Org funktion not created correctly from FE req')
