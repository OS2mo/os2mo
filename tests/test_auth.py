#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from mora.auth import tokens

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

        with util.override_settings(SAML_IDP_TYPE='wso2',
                                    SAML_IDP_URL='http://idp'):
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
                '/service/user/login',
                {
                    'error_key': 'E_UNAUTHORIZED',
                    'description': (
                        'The security token could not be authenticated or '
                        'authorized'
                    ),
                    'error': True,
                    'status': 401,
                },
                json={
                    'username': 'USER',
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
                '/service/user/login',
                {
                    'error': True,
                    'error_key': 'E_UNAUTHORIZED',
                    'description': (
                        'ID3242: The security token could not be '
                        'authenticated or authorized.'
                    ),
                    'status': 401,
                },
                json={
                    'username': 'USER',
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
                '/service/user/login',
                {'user': 'USER'},
                json={
                    'username': 'USER',
                    'password': 's3cr1t!',
                },
            )

            with self.subTest('raw'), self.app.app_context():
                self.assertEqual(
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
                '/service/user/login',
                {'user': 'USER'},
                json={
                    'username': 'USER',
                    'password': 's3cr1t!',
                },
            )

            with self.subTest('raw'), self.app.app_context():
                self.assertEqual(
                    tokens.get_token('X', 'Y', raw=True),
                    util.get_mock_text('auth/adfs-assertion.xml', 'rb')
                )

    @util.mock()
    def test_disabled_login(self, mock):
        with util.override_settings(SAML_IDP_TYPE=None,
                                    SAML_IDP_URL=None):
            self.assertRequestResponse(
                '/service/user/login',
                {'user': 'USER'},
                json={
                    'username': 'USER',
                    'password': 's3cr1t!',
                },
            )

    def test_empty_user(self):
        with util.override_settings(SAML_IDP_TYPE='adfs',
                                    SAML_IDP_URL=IDP_URL):
            self.assertRequestResponse(
                '/service/user/login',
                {
                    'error': True,
                    'error_key': 'E_UNAUTHORIZED',
                    'description': (
                        'Username/password cannot be blank'
                    ),
                    'status': 401,
                },
                json={
                    'username': '',
                    'password': 's3cr1t!',
                },
                status_code=401,
            )

    def test_empty_pass(self):
        with util.override_settings(SAML_IDP_TYPE='adfs',
                                    SAML_IDP_URL=IDP_URL):
            self.assertRequestResponse(
                '/service/user/login',
                {
                    'error': True,
                    'error_key': 'E_UNAUTHORIZED',
                    'description': (
                        'Username/password cannot be blank'
                    ),
                    'status': 401,
                },
                json={
                    'username': 'USER',
                    'password': '',
                },
                status_code=401,
            )
