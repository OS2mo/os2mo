#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import base64
import os
from urllib.parse import urlparse, parse_qs, urlencode

import freezegun
from flask_testing import TestCase
from mock import patch
from onelogin.saml2.utils import OneLogin_Saml2_Utils as saml_utils

from mora.app import app

TESTS_DIR = os.path.dirname(__file__)


class TestSSO(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SERVER_NAME'] = "127.0.0.1:5000"

        app.config['AUTH'] = True
        app.config['SAML_IDP_METADATA_FILE'] = TESTS_DIR + '/sso/idp.xml'
        return app

    def get_sso_response(self):
        with open(TESTS_DIR + '/sso/sso_response.xml', 'rb') as sso_response:
            return base64.b64encode(sso_response.read())

    def get_slo_response(self):
        with open(TESTS_DIR + '/sso/slo_response.xml', 'rb') as slo_response:
            return saml_utils.deflate_and_base64_encode(slo_response.read())

    def test_sso_redirects_to_login_with_next(self):
        r = self.client.get('/saml/sso/?next=http://redirect.me/to/here')
        url = urlparse(r.location)
        query = parse_qs(url.query)

        self.assertEqual(302, r.status_code)
        self.assertEqual('https', url.scheme)
        self.assertEqual('192.168.1.212', url.netloc)
        self.assertEqual('/simplesaml/saml2/idp/SSOService.php', url.path)
        self.assertEqual('http://redirect.me/to/here',
                         query.get('RelayState')[0])

    def test_sso_redirects_to_login_with_no_next(self):
        r = self.client.get('/saml/sso/')
        url = urlparse(r.location)
        query = parse_qs(url.query)

        self.assertEqual(302, r.status_code)
        self.assertEqual('https', url.scheme)
        self.assertEqual('192.168.1.212', url.netloc)
        self.assertEqual('/simplesaml/saml2/idp/SSOService.php', url.path)
        self.assertEqual('http://127.0.0.1:5000/',
                         query.get('RelayState')[0])

    @freezegun.freeze_time('2018-09-17T13:30:00Z')
    def test_acs_redirects_correctly_with_relaystate(self):
        data = {
            'SAMLResponse': self.get_sso_response(),
            'RelayState': 'http://redirect.me/to/here'
        }
        r = self.client.post('/saml/acs/', data=data)

        self.assertEqual(302, r.status_code)
        self.assertEqual('http://redirect.me/to/here', r.location)

    @freezegun.freeze_time('2018-09-17T13:30:00Z')
    def test_acs_redirects_correctly_with_no_relaystate(self):
        data = {
            'SAMLResponse': self.get_sso_response(),
        }
        r = self.client.post('/saml/acs/', data=data)

        self.assertEqual(302, r.status_code)
        self.assertEqual('http://127.0.0.1:5000/', r.location)

    @freezegun.freeze_time('2018-09-17T13:30:00Z')
    def test_acs_sets_session_correctly(self):
        data = {
            'SAMLResponse': self.get_sso_response(),
        }
        with self.client.session_transaction() as sess:
            self.assertFalse(sess.get('MO-Token'))

        r = self.client.post('/saml/acs/', data=data)

        samlUserData = {
            'urn:oid:0.9.2342.19200300.100.1.1': ['bruce'],
            'urn:oid:0.9.2342.19200300.100.1.3': ['bruce@kung.fu'],
            'urn:oid:2.5.4.41': ['Bruce Lee']
        }
        samlNameId = '_e3dfaf3e3385fd182b1c4d4164644393cce3ac7bfe'
        samlSessionIndex = '_6a54ed11e21b64af1a0380b1fba3ec575b05855465'

        with self.client.session_transaction() as sess:
            self.assertTrue(sess.get('MO-Token'))
            self.assertEqual(samlUserData, sess.get('samlUserdata'))
            self.assertEqual(samlNameId, sess.get('samlNameId'))
            self.assertEqual(samlSessionIndex, sess.get('samlSessionIndex'))

    @freezegun.freeze_time('2010-09-17T13:30:00Z')
    def test_acs_returns_error_when_timestamp_is_not_valid(self):
        data = {
            'SAMLResponse': self.get_sso_response(),
        }

        expected = {
            'description': "invalid_response",
            'error': True,
            'error_key': 'E_SAML_AUTH_ERROR',
            'status': 500
        }

        r = self.client.post('/saml/acs/', data=data)

        self.assertEqual(expected, r.json)

    def test_slo_redirects_to_logout_page(self):
        r = self.client.get('/saml/slo/')
        url = urlparse(r.location)

        self.assertEqual(302, r.status_code)
        self.assertEqual('https', url.scheme)
        self.assertEqual('192.168.1.212', url.netloc)
        self.assertEqual('/simplesaml/saml2/idp/SingleLogoutService.php',
                         url.path)

    def test_sls_redirects_correctly(self):
        data = {
            'SAMLResponse': self.get_slo_response(),
        }
        r = self.client.get('/saml/sls/', query_string=urlencode(data))

        self.assertEqual(302, r.status_code)
        self.assertEqual('http://127.0.0.1:5000/', r.location)

    def test_sls_deletes_session(self):
        data = {
            'SAMLResponse': self.get_slo_response(),
        }

        with self.client.session_transaction() as sess:
            sess['MO-Token'] = "TOKEN"

        r = self.client.get('/saml/sls/', query_string=urlencode(data))

        with self.client.session_transaction() as sess:
            self.assertFalse(sess)

    @patch('onelogin.saml2.auth.OneLogin_Saml2_Auth.get_errors',
           lambda *x, **y: ['ERROR 2'])
    def test_sls_returns_errors(self):
        data = {
            'SAMLResponse': self.get_slo_response(),
        }

        r = self.client.get('/saml/sls/', query_string=urlencode(data))

        expected = {
            'description': "ERROR 2",
            'error': True,
            'error_key': 'E_SAML_AUTH_ERROR',
            'status': 500
        }

        self.assertEqual(expected, r.json)

    def test_metadata_returns_metadata(self):
        ns = 'onelogin.saml2.settings.OneLogin_Saml2_Settings'
        metadata = b"<metadata/>"

        with patch(ns + '.validate_metadata') as validate, \
                patch(ns + '.get_sp_metadata') as get_sp:
            validate.return_value = False
            get_sp.return_value = metadata

            r = self.client.get('/saml/metadata/')

        self.assertEqual(metadata, r.data)
        self.assertIn(('Content-Type', 'text/xml'), list(r.headers))

    @patch(
        'onelogin.saml2.settings.OneLogin_Saml2_Settings.validate_metadata',
        lambda *x, **y: ['ERROR 3', 'ERROR 4']
    )
    def test_metadata_returns_errors(self):
        r = self.client.get('/saml/metadata/')

        expected = {
            'description': "ERROR 3, ERROR 4",
            'error': True,
            'error_key': 'E_SAML_AUTH_ERROR',
            'status': 500
        }

        self.assertEqual(expected, r.json)
