#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import datetime
import unittest

import flask
import freezegun

from mora import util


class TestUtils(unittest.TestCase):

    def test_to_lora_time(self):
        min, max = datetime.datetime.min, datetime.datetime.max
        self.assertEqual(util.to_lora_time('31-12-2017'),
                         '2017-12-31T00:00:00+01:00')
        self.assertEqual(util.to_lora_time('infinity'), 'infinity')
        self.assertEqual(util.to_lora_time('-infinity'), '-infinity')

        # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
        # we get it as a space
        self.assertEqual(util.to_lora_time('2017-07-31T22:00:00 00:00'),
                         '2017-07-31T22:00:00+00:00')

    def test_to_frontend_time(self):
        min, max = datetime.datetime.min, datetime.datetime.max
        self.assertEqual(util.to_frontend_time('2017-12-31 00:00:00+01'),
                         '31-12-2017')
        self.assertEqual(util.to_frontend_time('infinity'), 'infinity')
        self.assertEqual(util.to_frontend_time('-infinity'), '-infinity')


class TestAppUtils(unittest.TestCase):
    def test_restrictargs(self):
        app = flask.Flask(__name__)

        @app.route('/')
        @util.restrictargs('hest')
        def root():
            return 'Hest!'

        client = app.test_client()

        with app.app_context():
            self.assertEquals(client.get('/').status,
                              '200 OK')
            self.assertEquals(client.get('/?hest=').status,
                              '200 OK')
            self.assertEquals(client.get('/?hest=42').status,
                              '200 OK')
            self.assertEquals(client.get('/?HeSt=42').status,
                              '200 OK')
            self.assertEquals(client.get('/?fest=').status,
                              '200 OK')
            self.assertEquals(client.get('/?fest=42').status,
                              '501 NOT IMPLEMENTED')
