#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os

from mora.converters import importing

from .. import util


class MockTests(util.TestCase):
    maxDiff = None

    @util.mock('importing.json')
    def test_load(self, m):
        expected = util.get_fixture('MAGENTA_01.json')

        self.assertEqual(expected, importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ]))

        self.assertEqual(expected, importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ], exact=True))

        self.assertEqual(expected, importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.xlsx'),
        ]))

    @util.mock()
    def test_convert(self, m):
        data = util.get_fixture('MAGENTA_01.json')

        # JSON converts tuples to lists - convert them back
        expected = list(map(tuple, util.get_fixture('MAGENTA_01-result.json')))

        with open('/tmp/x.json', 'w') as fp:
            import json
            json.dump(
                list(importing.convert([
                    os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
                ])),
                fp,
                indent=2, sort_keys=True,
            )

        self.assertEqual(sorted(expected), sorted(importing.convert([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ])))
