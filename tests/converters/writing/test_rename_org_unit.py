#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun
import unittest
from mora.converters import writing


class TestRenameOrgUnit(unittest.TestCase):
    maxDiff = None

    @freezegun.freeze_time('2000-01-01 12:00:00', tz_offset=1)
    def test_should_rename_org_unit_correctly(self):
        frontend_req = {
            'name': 'A6om',
            'user-key': 'A6',
            'parent-object': {
                'name': 'Øvrige Enheder',
                'user-key': 'ØVRIGE',
                'parent-object': {
                    'name': 'Aarhus Kommune',
                    'user-key': 'ÅRHUS',
                    'parent-object': None,
                    'valid-to': 'infinity',
                    'activeName': 'Aarhus Kommune',
                    'valid-from': '2015-12-31 23:00:00+00',
                    'uuid': '7454a573-5dab-4c2f-baf2-89f273286dec',
                    'hasChildren': True,
                    'org': '59141156-ed0b-457c-9535-884447c5220b',
                    'parent': None},
                'valid-to': 'infinity',
                'activeName': 'Øvrige Enheder',
                'valid-from': '2015-12-31 23:00:00+00',
                'uuid': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc',
                'hasChildren': True,
                'org': '59141156-ed0b-457c-9535-884447c5220b',
                'parent': '7454a573-5dab-4c2f-baf2-89f273286dec'},
            'valid-to': 'infinity',
            'activeName': 'A6',
            'valid-from': '01-01-2010',
            'uuid': '65db58f8-a8b9-48e3-b1e3-b0b73636aaa5',
            'hasChildren': False,
            'org': '59141156-ed0b-457c-9535-884447c5220b',
            'parent': 'b2ec5a54-0713-43f8-91f2-e4fd8b9376bc'
        }
        expected_output = {
            'attributter': {
                'organisationenhedegenskaber': [
                    {
                        'virkning': {
                            'from': '2010-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                        'enhedsnavn': 'A6om'
                    }
                ]
            },
        }
        actual_output = writing.rename_org_unit(frontend_req)
        self.assertEqual(actual_output, expected_output,
                         'Unexpected output for rename org unit')
