#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest
import datetime

import flask
import freezegun

from mora import exceptions
from mora import util

from .util import TestCase


@freezegun.freeze_time('2015-06-01T01:10')
class TestUtils(TestCase):

    def test_to_lora_time(self):
        tests = {
            util.today():
            '2015-06-01T00:00:00+02:00',

            util.now():
            '2015-06-01T01:10:00+02:00',

            '01-06-2017':
            '2017-06-01T00:00:00+02:00',

            '31-12-2017':
            '2017-12-31T00:00:00+01:00',

            'infinity': 'infinity',
            '-infinity': '-infinity',

            '2017-07-31T22:00:00+00:00':
            '2017-07-31T22:00:00+00:00',

            # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
            # we get it as a space
            '2017-07-31T22:00:00 00:00':
            '2017-07-31T22:00:00+00:00',

            datetime.date(2015, 6, 1):
            '2015-06-01T00:00:00+02:00',

            # check parsing of raw dates
            '2018-01-01':
            '2018-01-01T00:00:00+01:00',

            '2018-06-01':
            '2018-06-01T00:00:00+02:00',
        }

        for value, expected in tests.items():
            self.assertEqual(expected, util.to_lora_time(value),
                             'failed to parse {!r}'.format(value))

        # NB: this test used to work, but we now use dateutil,
        # which tries it best to make of the inputs from the
        # user...
        if False:
            # 15 is not a valid month
            self.assertRaises(exceptions.ValidationError, util.to_lora_time,
                              '1999-15-11 00:00:00+01')

        # make sure we can round-trip the edge cases correctly
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
        self.assertRaises(exceptions.ValidationError,
                          list, util.splitlist([], 0))
        self.assertRaises(exceptions.ValidationError,
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

    def test_get_cpr_birthdate(self):
        def check(cpr, isodate):
            with self.subTest(str(cpr)):
                self.assertEqual(
                    util.get_cpr_birthdate(cpr),
                    util.from_iso_time(isodate),
                )

        check(1010771999, '1977-10-10')

        check(1010274999, '2027-10-10')
        check(1010774999, '1977-10-10')

        check(1010575999, '2057-10-10')
        check(1010775999, '1877-10-10')

        check(1010776999, '1877-10-10')
        check(1010476999, '2047-10-10')

        check(1010359999, '2035-10-10')
        check(1010779999, '1977-10-10')

        check('1205320000', '1932-05-12')
        check('0906340000', '1934-06-09')
        check('0905380000', '1938-05-09')

        with self.assertRaisesRegex(ValueError, '^invalid CPR number'):
            util.get_cpr_birthdate('0000000000')

        with self.assertRaisesRegex(ValueError, '^invalid CPR number'):
            util.get_cpr_birthdate(2222222222)

        with self.assertRaisesRegex(ValueError, '^invalid CPR number'):
            util.get_cpr_birthdate(10101010000)


class TestAppUtils(unittest.TestCase):
    def test_restrictargs(self):
        app = flask.Flask(__name__)

        @app.route('/')
        @util.restrictargs('hest')
        def root():
            return 'Hest!'

        client = app.test_client()

        with app.app_context():
            self.assertEqual(client.get('/').status,
                             '200 OK')

        with app.app_context():
            self.assertEqual(client.get('/?hest=').status,
                             '200 OK')

        with app.app_context():
            self.assertEqual(client.get('/?hest=42').status,
                             '200 OK')

        with app.app_context():
            self.assertEqual(client.get('/?HeSt=42').status,
                             '200 OK')

        with app.app_context():
            self.assertEqual(client.get('/?fest=').status,
                             '200 OK')

        with app.app_context():
            self.assertEqual(client.get('/?fest=42').status,
                             '501 NOT IMPLEMENTED')

        with app.app_context():
            self.assertEqual(client.get('/?hest=42').status,
                             '200 OK')

            # verify that we only perform the check once -- normally,
            # this will only happen if a request invokes another
            # request
            self.assertEqual(client.get('/?fest=42').status,
                             '200 OK')
