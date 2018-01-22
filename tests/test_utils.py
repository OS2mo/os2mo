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
import datetime
import pytz

from mora import util


@freezegun.freeze_time(datetime.datetime(2015, 6, 1, 1, 10))
class TestUtils(unittest.TestCase):

    def test_to_lora_time(self):

        self.assertEqual('2015-06-01T00:00:00+02:00',
                         util.to_lora_time(util.today()))
        self.assertEqual('2015-06-01T01:10:00+02:00',
                         util.to_lora_time(util.now()))

        self.assertEqual(util.to_lora_time('31-12-2017'),
                         '2017-12-31T00:00:00+01:00')
        self.assertEqual(util.to_lora_time('infinity'), 'infinity')
        self.assertEqual(util.to_lora_time('-infinity'), '-infinity')

        # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
        # we get it as a space
        self.assertEqual(util.to_lora_time('2017-07-31T22:00:00 00:00'),
                         '2017-07-31T22:00:00+00:00')

        self.assertEqual(util.to_lora_time(datetime.date(2015, 6, 1)),
                         '2015-06-01T00:00:00+02:00')

        self.assertEqual('-infinity',
                         util.to_lora_time('-infinity'))

        self.assertEqual('infinity',
                         util.to_lora_time('infinity'))

        # 15 is not a valid month
        self.assertRaises(ValueError, util.to_lora_time,
                          '1999-15-11 00:00:00+01')

        # make sure we can unstringify the edge cases correctly
        self.assertEqual(
            util.parsedatetime('0001-01-01T00:00:00-23:00'),
            util.negative_infinity,
        )

        self.assertEqual(
            util.parsedatetime('9999-12-31T23:59:59.999999+23:00'),
            util.positive_infinity,
        )

        self.assertEqual(util.parsedatetime(util.negative_infinity),
                         util.negative_infinity)

        self.assertEqual(util.parsedatetime(util.positive_infinity),
                         util.positive_infinity)

    def test_to_frontend_time(self):
        self.assertEqual(util.to_frontend_time(util.today()),
                         '01-06-2015')

        self.assertEqual(util.to_frontend_time('2017-12-31 00:00:00+01'),
                         '31-12-2017')
        self.assertEqual(util.to_frontend_time('infinity'), 'infinity')
        self.assertEqual(util.to_frontend_time('-infinity'), '-infinity')

        self.assertEqual(
            util.to_frontend_time('1980-07-01 00:00:00+02'),
            '01-07-1980',
        )

        self.assertEqual(
            util.to_frontend_time('1980-01-01 00:00:00+01'),
            '01-01-1980',
        )

        self.assertEqual(
            util.to_frontend_time('1980-07-01 02:00:00+02'),
            '1980-07-01T02:00:00+02:00',
        )

        self.assertEqual('01-06-2015',
                         util.to_frontend_time(datetime.date.today()))
        self.assertEqual('01-06-2015',
                         util.to_frontend_time(util.today()))
        self.assertEqual('2015-06-01T01:10:00+02:00',
                         util.to_frontend_time(util.now()))
        self.assertEqual('01-01-2015',
                         util.to_frontend_time(datetime.date(2015, 1, 1)))
        self.assertEqual('01-06-2015',
                         util.to_frontend_time(datetime.date(2015, 6, 1)))

        self.assertEqual('-infinity',
                         util.to_frontend_time('-infinity'))

        self.assertEqual('infinity',
                         util.to_frontend_time('infinity'))

    def test_splitlist(self):
        self.assertEqual(
            list(util.splitlist([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)),
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]],
        )
        self.assertEqual(
            list(util.splitlist([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4)),
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]],
        )
        self.assertEqual(
            list(util.splitlist([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 11)),
            [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]],
        )
        self.assertRaises(ValueError,
                          list, util.splitlist([], 0))
        self.assertRaises(ValueError,
                          list, util.splitlist([], -1))
        self.assertRaises(TypeError,
                          list, util.splitlist([], 'horse'))

    def test_is_uuid(self):
        self.assertTrue(util.is_uuid('00000000-0000-0000-0000-000000000000'))
        self.assertFalse(util.is_uuid('42'))
        self.assertFalse(util.is_uuid(None))

    def test_is_cpr_number(self):
        self.assertTrue(util.is_cpr_number('0101011000'))
        self.assertFalse(util.is_cpr_number('42'))
        self.assertFalse(util.is_cpr_number(None))


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
