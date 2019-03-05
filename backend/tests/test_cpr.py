#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from . import util
from mora import util as mora_util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@util.mock()
class Tests(util.TestCase):
    maxDiff = None

    @util.override_settings(DUMMY_MODE=True)
    def test_cpr_lookup_dummy_mode_true(self, m):
        with self.subTest('found'):
            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q=0101501234',
                {
                    'name': 'Merle Mortensen',
                    'cpr_no': "0101501234"
                })

        with self.subTest('too early'):
            self.assertEqual(mora_util.get_cpr_birthdate(2004936541).year,
                             1893)

            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q=2004936541',
                {
                    'cpr': '2004936541',
                    'description': 'No person found for given CPR number.',
                    'error': True,
                    'error_key': 'V_NO_PERSON_FOR_CPR',
                    'status': 404,
                },
                status_code=404,
            )

        with self.subTest('too late'):
            self.assertEqual(mora_util.get_cpr_birthdate(2004256543).year,
                             2025)

            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q=2004256543',
                {
                    'cpr': '2004256543',
                    'description': 'No person found for given CPR number.',
                    'error': True,
                    'error_key': 'V_NO_PERSON_FOR_CPR',
                    'status': 404,
                },
                status_code=404,
            )

    def test_cpr_lookup_raises_on_wrong_length(self, m):
        # Arrange

        # Act
        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=1234/',
            {
                'cpr': '1234/',
                'error_key': 'V_CPR_NOT_VALID',
                'description': 'Not a valid CPR number.',
                'error': True,
                'status': 400,
            },
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=1234567890123',
            {
                'cpr': '1234567890123',
                'error_key': 'V_CPR_NOT_VALID',
                'description': 'Not a valid CPR number.',
                'error': True,
                'status': 400,
            },
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/cpr_lookup/?q=2222222222',
            {
                'cpr': '2222222222',
                'error_key': 'V_CPR_NOT_VALID',
                'description': 'Not a valid CPR number.',
                'error': True,
                'status': 400,
            },
            status_code=400,
        )
