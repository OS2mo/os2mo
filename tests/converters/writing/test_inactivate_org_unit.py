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
from tests import util


class TestInactivateOrgUnit(unittest.TestCase):
    maxDiff = None

    @util.mock()
    @freezegun.freeze_time('2000-01-01 12:00:00', tz_offset=+1)
    def test_should_inactivate_org_unit_correctly(self, mock):
        mock.get(
            'http://mox/organisation/organisationenhed/00000000-0000-0000-'
            '0000-000000000000?virkningfra=-infinity&virkningtil=infinity',
            json={
                'tilstande': {
                    'organisationenhedgyldighed': [
                        {
                            'virkning': {
                                'from': '2010-01-01T00:00:00+01:00',
                                'from_included': True,
                                'to': 'infinity',
                                'to_included': False,
                            },
                            'gyldighed': 'Aktiv',
                        },
                    ]
                }
            }
        )
        expected_output = {
            'note': 'Afslut enhed',
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'virkning': {
                            'from': '2009-01-01T00:00:00+01:00',
                            'from_included': True,
                            'to': '2010-01-01T00:00:00+01:00',
                            'to_included': False,
                        },
                        'gyldighed': 'Aktiv',
                    },
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
        actual_output = writing.inactivate_org_unit('2009-01-01 00:00:00+01',
                                                    '01-01-2010')
        self.assertEqual(actual_output, expected_output,
                         'Unexpected output from inactivate org unit')
