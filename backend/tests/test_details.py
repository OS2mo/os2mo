#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora.service import detail_writing

from . import util


class Tests(util.TestCase):
    maxDiff = None

    def test_get_scope(self):
        self.assertEquals(detail_writing._get_scope('e').path,
                          'organisation/bruger')

        self.assertEquals(detail_writing._get_scope('ou').path,
                          'organisation/organisationenhed')

        self.assertRaises(ValueError,
                          detail_writing._get_scope, 'kaflaflibob')

    def test_invalid_type(self):
        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/create',
            {
                'description': 'Unknown role type.',
                'error': True,
                'error_key': 'E_UNKNOWN_ROLE_TYPE',
                'status': 400,
                'type': 'kaflaflibob',
            },
            json=[{
                'type': 'kaflaflibob',
            }],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/edit',
            {
                'description': 'Unknown role type.',
                'error': True,
                'error_key': 'E_UNKNOWN_ROLE_TYPE',
                'status': 400,
                'type': 'kaflaflibob',
            },
            json=[{
                'type': 'kaflaflibob',
            }],
            status_code=400,
        )

        self.assertRequestResponse(
            '/service/e/00000000-0000-0000-0000-000000000000/details/blyf',
            {
                'description': 'Unknown role type.',
                'error': True,
                'error_key': 'E_UNKNOWN_ROLE_TYPE',
                'status': 400,
                'type': 'blyf',
            },
            status_code=400,
        )
