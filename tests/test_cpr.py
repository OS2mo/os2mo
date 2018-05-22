#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import mock

import freezegun

from . import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
@util.mock()
class Tests(util.TestCase):
    maxDiff = None

    def test_cpr_lookup_prod_mode_false(self, m):
        # Arrange
        cpr = "0101501234"

        expected = {
            'name': 'Merle Mortensen',
            'cpr_no': cpr
        }

        # Act
        with util.override_settings(PROD_MODE=False):
            self.assertRequestResponse(
                '/service/e/cpr_lookup/?q={}'.format(cpr),
                expected)

            with mock.patch(
                'mora.integrations.serviceplatformen._get_citizen_stub',
                side_effect=KeyError('go away'),
                assert_called_with='asdasdasdx',
            ) as p:
                self.assertRequestResponse(
                    '/service/e/cpr_lookup/?q=1111111111',
                    {
                        'cpr': '1111111111',
                        'error_key': 'V_NO_PERSON_FOR_CPR',
                        'description': 'No person found for given CPR number.',
                        'error': True,
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
