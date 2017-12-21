#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from mora.converters import writing


class TestCreateOrgFunktion(unittest.TestCase):
    maxDiff = None

    def test_should_create_org_funktion_correctly(self):
        frontend_req = {
            "valid-from": "01-12-2017",
            "valid-to": "22-12-2017",
            "org-unit": {
                "children": [],
                "hasChildren": False,
                "name": "New Org Funk",
                "org": "456362c4-0ee4-4e5e-a72c-751239745e62",
                "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "type": {
                    "name": "Fakultet"
                },
                "user-key": "samf",
                "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                "valid-from": "2016-12-31T23:00:00+00:00",
                "valid-to": "infinity"
            },
            "job-title": {
                "name": "job-title 1",
                "uuid": "11111111-1111-1111-1111-111111111111"
            },
            "type": {
                "name": "type 1",
                "uuid": "ffffffff-ffff-ffff-ffff-ffffffffffff"
            },
            "person": "2f9a3e4f-5f91-40a4-904c-68a376b7320f",
            "role-type": "engagement",
            "user-key": "NULL"
        }

        output_org_funk = {
            'attributter': {
                'organisationfunktionegenskaber': [{
                    'funktionsnavn': 'job-title 1 b688513d-11f7-'
                                     '4efc-b679-ab082a2055d0',
                    'brugervendtnoegle': '2f9a3e4f-5f91-40a4-'
                                         '904c-68a376b7320f b688513d-11f7-'
                                         '4efc-b679-ab082a2055d0',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+01:00',
                        'from': '2017-12-01T00:00:00+01:00'
                    }
                }]
            },
            'note': 'Oprettet i MO',
            'relationer': {
                'tilknyttedeenheder': [{
                    'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    'virkning': {
                        'to_included': False, 'from_included': True,
                        'to': '2017-12-22T00:00:00+01:00',
                        'from': '2017-12-01T00:00:00+01:00'
                    }
                }],
                'tilknyttedebrugere': [{
                    'uuid': '2f9a3e4f-5f91-40a4-904c-68a376b7320f',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+01:00',
                        'from': '2017-12-01T00:00:00+01:00'
                    }
                }],
                'organisatoriskfunktionstype': [{
                    'uuid': 'ffffffff-ffff-ffff-ffff-ffffffffffff',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+01:00',
                        'from': '2017-12-01T00:00:00+01:00'
                    }
                }],
                'tilknyttedeorganisationer': [{
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+01:00',
                        'from': '2017-12-01T00:00:00+01:00'
                    }
                }],
                'opgaver': [{
                    'uuid': '11111111-1111-1111-1111-111111111111',
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+01:00',
                        'from': '2017-12-01T00:00:00+01:00'
                    }
                }]
            },
            'tilstande': {
                'organisationfunktiongyldighed': [{
                    'virkning': {
                        'to_included': False,
                        'from_included': True,
                        'to': '2017-12-22T00:00:00+01:00',
                        'from': '2017-12-01T00:00:00+01:00'
                    },
                    'gyldighed': 'Aktiv'
                }]
            }
        }

        self.assertDictEqual(writing.create_org_funktion(frontend_req),
                             output_org_funk,
                             'Org funktion not created correctly from FE req')
