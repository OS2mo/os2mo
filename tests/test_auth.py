#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from mora import tokens

from . import util

IDP_URL = 'mock://idp'

ORG_URL = (
    'http://mox/organisation/organisation'
    '?bvn=%25'
    '&virkningfra=2001-01-01T00%3A00%3A00%2B01%3A00'
    '&virkningtil=2001-01-02T00%3A00%3A00%2B01%3A00'
)


@freezegun.freeze_time('2001-01-01')
class MockTests(util.TestCase):
    @util.mock()
    def test_access_denied(self, mock):
        mock.get(ORG_URL, status_code=401, json={
            "message": "No Authorization header present",
        })

        with util.override_settings(SAML_IDP_TYPE='wso2',
                                    SAML_IDP_URL='http://idp'):
            self.assertRequestResponse(
                '/mo/o/',
                {
                    'message': 'No Authorization header present',
                    'status': 401,
                },
                status_code=401,
            )

    @util.mock()
    def test_failed_wso2_login(self, mock):
        mock.post(IDP_URL,
                  text=util.get_mock_text('auth/wso2-failed-login.xml'),
                  headers={
                      'Content-Type': 'application/soap+xml',
                  },
                  status_code=500)

        with util.override_settings(SAML_IDP_TYPE='wso2',
                                    SAML_IDP_URL=IDP_URL):
            self.assertRequestResponse(
                '/mo/service/user/USER/login',
                {
                    'message': (
                        'The security token could not be authenticated or '
                        'authorized'
                    ),
                    'status': 401,
                },
                json={
                    'password': 's3cr1t!',
                },
                status_code=401,
            )

    @util.mock()
    def test_failed_adfs_login(self, mock):
        mock.post(IDP_URL,
                  text=util.get_mock_text('auth/adfs-failed-login.xml'),
                  headers={
                      'Content-Type': 'application/soap+xml',
                  },
                  status_code=500)

        with util.override_settings(SAML_IDP_TYPE='adfs',
                                    SAML_IDP_URL=IDP_URL):
            self.assertRequestResponse(
                '/mo/service/user/USER/login',
                {
                    'message': (
                        'ID3242: The security token could not be '
                        'authenticated or authorized.'
                    ),
                    'status': 401,
                },
                json={
                    'password': 's3cr1t!',
                },
                status_code=401,
            )

    @util.mock()
    def test_successful_wso2_login(self, mock):
        mock.post(IDP_URL,
                  text=util.get_mock_text('auth/wso2-successful-login.xml'),
                  headers={
                      'Content-Type': 'application/soap+xml',
                  },
                  status_code=200)

        with util.override_settings(SAML_IDP_TYPE='wso2',
                                    SAML_IDP_URL=IDP_URL):
            self.assertRequestResponse(
                '/mo/service/user/USER/login',
                {'role': [], 'token': 'N/A', 'user': 'USER'},
                json={
                    'password': 's3cr1t!',
                },
            )

            with self.subTest('raw'), self.app.app_context():
                self.assertEquals(
                    tokens.get_token('X', 'Y', raw=True),
                    util.get_mock_text('auth/wso2-assertion.xml', 'rb'),
                )

    @util.mock()
    def test_successful_adfs_login(self, mock):
        mock.post(IDP_URL,
                  text=util.get_mock_text('auth/adfs-successful-login.xml'),
                  headers={
                      'Content-Type': 'application/soap+xml',
                  },
                  status_code=200)

        with util.override_settings(SAML_IDP_TYPE='adfs',
                                    SAML_IDP_URL=IDP_URL):
            self.assertRequestResponse(
                '/mo/service/user/USER/login',
                {'role': [], 'token': 'N/A', 'user': 'USER'},
                json={
                    'password': 's3cr1t!',
                },
            )

            with self.subTest('raw'), self.app.app_context():
                self.assertEquals(
                    tokens.get_token('X', 'Y', raw=True),
                    util.get_mock_text('auth/adfs-assertion.xml', 'rb')
                )

    @util.mock()
    def test_disabled_login(self, mock):
        with util.override_settings(SAML_IDP_TYPE=None,
                                    SAML_IDP_URL=None):
            self.assertRequestResponse(
                '/mo/service/user/USER/login',
                {'role': [], 'token': 'N/A', 'user': 'USER'},
                json={
                    'password': 's3cr1t!',
                },
            )
