#
# Copyright (c) 2017-2019, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import freezegun

from . import util

IDP_URL = 'mock://idp'

ORG_URL = (
    'http://mox/organisation/organisation'
    '?bvn=%25'
    '&virkningfra=2001-01-01T00%3A00%3A00%2B01%3A00'
    '&virkningtil=2001-01-01T00%3A00%3A00.000001%2B01%3A00'
)


@freezegun.freeze_time('2001-01-01')
class MockTests(util.TestCase):
    @util.mock()
    def test_access_denied(self, mock):
        mock.get(ORG_URL, status_code=401, json={
            "message": "No Authorization header present",
        })

        self.assertRequestResponse(
            '/service/o/',
            {
                'error': True,
                'error_key': 'E_UNAUTHORIZED',
                'description': 'No Authorization header present',
                'status': 401,
            },
            status_code=401,
        )

    def test_get_user_returns_username(self):
        self.app.config['SAML_USERNAME_ATTR'] = 'whatever'

        with self.client.session_transaction() as sess:
            sess['samlAttributes'] = {'whatever': ['USERNAME']}

        self.assertRequestResponse(
            '/service/user',
            'USERNAME',
        )

    def test_get_user_no_username(self):
        self.assertRequestResponse(
            '/service/user',
            None,
        )
