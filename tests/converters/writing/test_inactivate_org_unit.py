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


class TestInactivateOrgUnit(unittest.TestCase):
    maxDiff = None

    @freezegun.freeze_time('2000-01-01 12:00:00', tz_offset=+1)
    def test_should_rename_org_unit_correctly(self):
        expected_output = {
            'note': 'Afslut enhed',
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'virkning': {
                            'from': '2010-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': 'infinity',
                            'to_included': False,
                        },
                        'gyldighed': 'Inaktiv',
                    }
                ]
            },
        }
        actual_output = writing.inactivate_org_unit('01-01-2010')
        self.assertEqual(actual_output, expected_output,
                         'Unexpected output from inactivate org unit')
