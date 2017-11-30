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
