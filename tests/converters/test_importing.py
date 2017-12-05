#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import os

from mora.converters import importing

from .. import util


class MockTests(util.TestCase):
    maxDiff = None

    @util.mock('importing.json')
    def test_load(self, m):
        expected = util.get_fixture('MAGENTA_01.json')

        self.assertEqual(expected, dict(importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ])))

        self.assertEqual(expected, dict(importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ], exact=True)))

        self.assertEqual(expected, dict(importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.xlsx'),
        ])))

    @util.mock()
    def test_convert(self, m):
        def keyfunc(val):
            fromdates = {
                f['virkning']['from']
                for group in val[2].values()
                if isinstance(group, dict)
                for effects in group.values()
                for f in effects
            }
            return val[0], val[1], fromdates

        # JSON converts tuples to lists - the map() converts them back
        expected = sorted(map(tuple,
                              util.get_fixture('MAGENTA_01-expected.json')),
                          key=keyfunc)

        actual = sorted(importing.convert([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ]), key=keyfunc)
        actual_path = os.path.join(util.FIXTURE_DIR, 'MAGENTA_01-actual.json')

        # for resetting the test
        with open(actual_path, 'w') as fp:
                json.dump(actual, fp, indent=2, sort_keys=True)

        self.assertEqual(expected, actual)

    @util.mock()
    def test_unknown_suffix(self, m):
        gen = importing.read_paths('test.hest')
        self.assertRaises(ValueError, next, gen)

    @util.mock('importing-wash.json')
    def test_addr_wash(self, m):
        w = importing._wash_address

        w.cache_clear()

        self.assertEqual(w('', None, None),
                         None)

        self.assertEqual(w('Rådhuspladsen', 8100, 'Århus C'),
                         '9b9a6a18-ffb7-4ece-a7f1-5368812e4719')

        self.assertEqual(w('Rådhuset', '8100', 'Aarhus C'),
                         '9b9a6a18-ffb7-4ece-a7f1-5368812e4719')

        self.assertEqual(w('Skejbygårdsvej 14-16', 8240, 'Risskov'),
                         None)

        self.assertEqual(w('Runevej 107-109', 8210, 'Aarhus V'),
                         '209b75e7-a662-4224-9e3d-64ef1f16eab0')

        self.assertEqual(w('Jettesvej 2, Hus 1', 8220, 'Brabrand'),
                         '2240aef2-7636-40b6-8c19-8f3e4dd65710')

        self.assertEqual(w('Grundtvigsvej 14, kld.', 8260, 'Viby J'),
                         None)
