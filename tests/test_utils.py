#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

import flask
import freezegun

from mora import util


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @freezegun.freeze_time('2017-12-31 00:00:00', tz_offset=+1)
    def test_should_reparse_31_12_2017_to_correct_date(self):
        self.assertEqual(util.reparsedatetime('31-12-2017'),
                         '2017-12-31T00:00:00+01:00', 'Error in parsing date')

    def test_should_reparse_date_infinity_correctly(self):
        self.assertEqual(util.reparsedatetime('infinity'), 'infinity',
                         'Error in parsing date')

    def test_should_reparse_date_minus_infinity_correctly(self):
        self.assertEqual(util.reparsedatetime('-infinity'), '-infinity',
                         'Error in parsing date')

    def test_should_reparse_None_to_infinity(self):
        self.assertEqual(util.reparsedatetime(None), 'infinity',
                         'Error when pasring empty date')


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
