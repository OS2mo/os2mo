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


class TestMoveOrgUnit(unittest.TestCase):
    maxDiff = None

    @freezegun.freeze_time('2000-01-01 12:00:00', tz_offset=+1)
    def test_should_move_org_unit_correctly(self):
        frontend_req = {
            "activeName": "Aarhus Havn",
            "hasChildren": False,
            "name": "Aarhus Havn",
            "org": "59141156-ed0b-457c-9535-884447c5220b",
            "parent": "80945a5a-ca10-4470-a801-80c6edaf6341",
            "parent-object": {
                "activeName": "Aarhus Kommune",
                "hasChildren": True,
                "name": "Aarhus Kommune",
                "org": "59141156-ed0b-457c-9535-884447c5220b",
                "parent": None, "parent-object": None,
                "user-key": "ÅRHUS",
                "uuid": "80945a5a-ca10-4470-a801-80c6edaf6341",
                "valid-from": "2015-12-31 23:00:00+00",
                "valid-to": "infinity"
            },
            "user-key": "HAVNEN",
            "uuid": "20780e20-3faa-4dd7-9102-4f0583bb1092",
            "valid-from": "01-01-2010",
            "valid-to": "infinity",
            "$$hashKey": "04E",
            "type-updated": "",
            "type": {
                "uuid": "0034fa1f-b1ef-4764-8505-c5b9ca43aaa9"
            },
            "changed": True,
            "valid-from-updated": "2017-06-30T22:00:00.000Z"
        }
        expected_output = {
            'note': 'Ret enhedstype',
            'relationer': {
                'enhedstype': [
                    {
                        'virkning': {
                            'from': '2010-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                        'uuid': '0034fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                    }
                ]
            },
        }
        actual_output = writing.retype_org_unit(frontend_req)

        self.assertEqual(actual_output, expected_output,
                         'Unexpected output for retype org unit')
