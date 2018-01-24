#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

from mora.converters import writing


class TestInactivateOrgFunktion(unittest.TestCase):
    maxDiff = None

    def test_should_inactivate_org_funktion_correctly(self):
        expected_output = {
            'note': 'Afslut funktion',
            'tilstande': {
                'organisationfunktiongyldighed': [
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
        actual_output = writing.inactivate_org_funktion(
            '2009-01-01 00:00:00+01',
            '01-01-2010')
        self.assertEqual(actual_output, expected_output,
                         'Unexpected output from inactivate org funktion')
