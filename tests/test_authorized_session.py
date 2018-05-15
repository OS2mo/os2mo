#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


# -- coding: utf-8 --
#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest import TestCase

from flask import g

from mora.app import app
from mora.lora import AuthorizedSession


class TestAuthorizedSession(TestCase):

    def setUp(self):
        # Dummy token
        self.token = "saml-gzipped someencryptedstring"

        # Set auth header
        self.auth_header = {
            "Authorization": self.token
        }

    def test_auth_header(self):

        with app.test_client() as client:

            # GET request
            # assuming that token value will be attached to the context
            client.get(path='/service/e/create', headers=self.auth_header)

            # Inserted token should match context user_token
            self.assertEqual(self.token, g.user_token)

    def test_init_session(self):

        with app.test_client() as client:

            # GET request
            client.get(path='/service/e/create', headers=self.auth_header)

            # Init session with current context
            session = AuthorizedSession(context=g)

            session_auth_header = session.headers["Authorization"]

            # Session auth header token value
            # should match token value from current context
            self.assertEqual(session_auth_header, g.user_token)

    def test_missing_auth_header(self):

        with app.test_client() as client:

            # GET request
            # No auth header
            client.get(path='/service/e/create')

            # Should fail due to missing token in context
            # TODO: ValueError should be replaced with custom exception
            self.assertRaises(ValueError, AuthorizedSession, context=g)
