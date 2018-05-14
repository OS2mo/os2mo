#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import mock

from tests import util


class Tests(util.TestCase):
    def test_failing_service(self):
        self.assertRequestResponse(
            '/service/kaflaflibob',
            {
                'error': True,
                'key': 'E_NO_SUCH_ENDPOINT',
                'description': 'No such endpoint.',
                'status': 404,
            },
            status_code=404,
        )

    @mock.patch('mora.service.common.get_connector')
    def test_exception_handling(self, p):
        p.side_effect = ValueError('go away')

        self.assertRequestResponse(
            '/service/ou/00000000-0000-0000-0000-000000000000/details/',
            {
                'error': True,
                'key': 'E_UNKNOWN',
                'description': 'go away',
                'status': 500,
            },
            status_code=500,
            drop_keys=['stacktrace'],
        )
