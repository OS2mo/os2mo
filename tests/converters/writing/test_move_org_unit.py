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
            'moveDate': '01-01-2010',
            'newParentOrgUnitUUID': '5c5ba813-0550-4284-8f47-cbb36725568d'
        }
        expected_output = {
            'relationer': {
                'overordnet': [
                    {
                        'virkning': {
                            'from': '2010-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                        'uuid': '5c5ba813-0550-4284-8f47-cbb36725568d',
                    }
                ]
            },
        }

        actual_output = writing.move_org_unit(frontend_req)
        self.assertEqual(actual_output, expected_output,
                         'Unexpected output for move org unit')
