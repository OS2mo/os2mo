#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest
import datetime

import dateutil.tz
import flask
import freezegun

from mora import exceptions
from mora import util
from mora import mapping

from .util import TestCase


@freezegun.freeze_time('2015-06-01T01:10')
class TestUtils(TestCase):
    @property
    def now(self):
        return util.now()

    @property
    def today(self):
        return util.now().replace(hour=0, minute=0, second=0, microsecond=0)

    def test_to_lora_time(self):
        tests = {
            self.today:
            '2015-06-01T00:00:00+02:00',

            self.now:
            '2015-06-01T01:10:00+02:00',

            '01-06-2017':
            '2017-06-01T00:00:00+02:00',

            '31-12-2017':
            '2017-12-31T00:00:00+01:00',

            'infinity': 'infinity',
            '-infinity': '-infinity',

            '2017-07-31T22:00:00+00:00':
            '2017-08-01T00:00:00+02:00',

            # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
            # we get it as a space
            '2017-07-31T22:00:00 00:00':
            '2017-08-01T00:00:00+02:00',

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
            self.assertRaises(exceptions.HTTPException, util.to_lora_time,
                              '1999-15-11 00:00:00+01')

        # make sure we can round-trip the edge cases correctly
        self.assertEqual(util.parsedatetime(util.NEGATIVE_INFINITY),
                         util.NEGATIVE_INFINITY)

        self.assertEqual(util.parsedatetime(util.POSITIVE_INFINITY),
                         util.POSITIVE_INFINITY)

        # we frequently get these dates in spreadsheets
        self.assertEqual(util.parsedatetime('31-12-9999'),
                         util.POSITIVE_INFINITY)

        # test fallback
        self.assertEqual(util.parsedatetime('blyf', 'flaf'), 'flaf')

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
        self.assertRaises(exceptions.HTTPException,
                          list, util.splitlist([], 0))
        self.assertRaises(exceptions.HTTPException,
                          list, util.splitlist([], -1))
        self.assertRaises(TypeError,
                          list, util.splitlist([], 'horse'))

    def test_is_uuid(self):
        self.assertTrue(util.is_uuid('00000000-0000-0000-0000-000000000000'))
        self.assertFalse(util.is_uuid('42'))
        self.assertFalse(util.is_uuid(None))

    def test_is_cpr_number(self):
        self.assertTrue(util.is_cpr_number('0101011000'))
        self.assertFalse(util.is_cpr_number('2222222222'))
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

    def test_urnquote(self):
        data = {
            '42': '42',
            'abc': 'abc',
            'aBc': 'a%42c',

            # from https://docs.python.org/3/library/urllib.parse.html
            'el niño': 'el%20ni%c3%b1o',
            'El Niño': '%45l%20%4ei%c3%b1o',
        }

        for s, expected in data.items():
            with self.subTest(s):
                self.assertEqual(util.urnquote(s), expected)

                self.assertEqual(util.urnunquote(util.urnquote(s)), s)

    def test_get_obj_path(self):
        # Arrange
        obj = {
            'whatever': 'no',
            'test1': {
                'garbage': 'there is some stuff here already',
                'test2': ['something']
            }
        }

        path = ('test1', 'test2')

        expected_props = ['something']

        # Act
        actual_props = util.get_obj_value(obj, path)

        # Assert
        self.assertEqual(expected_props, actual_props)

    def test_get_obj_path_none(self):
        # Arrange
        obj = {
            'whatever': 'no',
            'test1': None,
        }

        path = ('test1', 'test2')

        expected_props = None

        # Act
        actual_props = util.get_obj_value(obj, path)

        # Assert
        self.assertEqual(expected_props, actual_props)

    def test_get_obj_path_missing(self):
        # Arrange
        obj = {
            'whatever': 'no',
        }

        path = ('test1',)

        expected_props = None

        # Act
        actual_props = util.get_obj_value(obj, path)

        # Assert
        self.assertEqual(expected_props, actual_props)

    def test_get_obj_path_weird(self):
        # Arrange
        obj = {
            'whatever': 'no',
            'test1': 42,
        }

        path = ('test1', 'test2')

        expected_props = None

        # Act
        actual_props = util.get_obj_value(obj, path)

        # Assert
        self.assertEqual(expected_props, actual_props)

    def test_set_obj_value_existing_path(self):
        # Arrange
        obj = {'test1': {'test2': [{'key1': 'val1'}]}}
        path = ('test1', 'test2')

        val = [{'key2': 'val2'}]

        expected_result = {
            'test1': {
                'test2': [
                    {'key1': 'val1'},
                    {'key2': 'val2'},
                ]
            }
        }

        # Act
        actual_result = util.set_obj_value(obj, path, val)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_set_obj_value_new_path(self):
        # Arrange
        obj = {}
        path = ('test1', 'test2')

        val = [{'key2': 'val2'}]

        expected_result = {
            'test1': {
                'test2': [
                    {'key2': 'val2'},
                ]
            }
        }

        # Act
        actual_result = util.set_obj_value(obj, path, val)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_set_obj_value_existing_path_string(self):
        # Arrange
        obj = {'test1': {'test2': '1337'}}
        path = ('test1', 'test2')

        val = '42'

        expected_result = {
            'test1': {
                'test2': '42'
            }
        }

        # Act
        actual_result = util.set_obj_value(obj, path, val)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_set_obj_value_new_path_string(self):
        # Arrange
        obj = {}
        path = ('test1', 'test2')

        val = '42'

        expected_result = {
            'test1': {
                'test2': '42'
            }
        }

        # Act
        actual_result = util.set_obj_value(obj, path, val)

        # Assert
        self.assertEqual(expected_result, actual_result)

    def test_get_valid_from(self):
        ts = '2018-03-21T00:00:00+01:00'
        dt = datetime.datetime(2018, 3, 21,
                               tzinfo=dateutil.tz.tzoffset(None, 3600))

        self.assertEqual(dt, util.get_valid_from(
            {
                'validity': {
                    'from': ts,
                }
            },
        ))

        self.assertEqual(dt, util.get_valid_from(
            {
                'validity': {
                },
            },
            {
                'validity': {
                    'from': ts,
                }
            }
        ))

        self.assertRaises(
            exceptions.HTTPException, util.get_valid_from,
            {},
        )

        self.assertRaises(
            exceptions.HTTPException, util.get_valid_from,
            {
                'validity': {},
            },
        )

        self.assertRaises(
            exceptions.HTTPException, util.get_valid_from,
            {},
            {
                'validity': {
                }
            },
        )

        self.assertRaises(
            exceptions.HTTPException, util.get_valid_from,
            {

            },
            {
                'validity': {
                }
            },
        )

        self.assertRaises(
            exceptions.HTTPException, util.get_valid_from,
            {

            },
            {
                'validity': {
                    'from': None,
                }
            },
        )

    def test_get_valid_to(self):
        ts = '2018-03-21'
        dt = datetime.datetime(2018, 3, 22,
                               tzinfo=dateutil.tz.tzoffset(None, 3600))

        self.assertEqual(dt, util.get_valid_to(
            {
                'validity': {
                    'to': ts,
                }
            },
        ))

        self.assertEqual(dt, util.get_valid_to(
            {
                'validity': {
                },
            },
            {
                'validity': {
                    'to': ts,
                }
            },
        ))

        self.assertEqual(
            util.POSITIVE_INFINITY,
            util.get_valid_to({}),
        )

        self.assertEqual(
            util.get_valid_to({
                'validity': {},
            }),
            util.POSITIVE_INFINITY,
        )

        self.assertEqual(
            util.POSITIVE_INFINITY,
            util.get_valid_to(
                {},
                {
                    'validity': {
                    }
                },
            ),
        )

        self.assertEqual(
            util.POSITIVE_INFINITY,
            util.get_valid_to(
                {
                    'validity': {
                        'to': None,
                    }
                },
            ),
        )

        self.assertEqual(
            util.POSITIVE_INFINITY,
            util.get_valid_to(
                {},
                {
                    'validity': {
                        'to': None,
                    }
                },
            ),
        )

    def test_get_validities(self):
        # start time required
        self.assertRaises(
            exceptions.HTTPException,
            util.get_valid_from, {}, {},
        )

        self.assertRaises(
            exceptions.HTTPException,
            util.get_valid_from, {}, {
                'validity': None,
            },
        )

        self.assertRaises(
            exceptions.HTTPException,
            util.get_valid_from, {}, {
                'validity': {
                    'from': None,
                },
            },
        )

        # still nothing
        self.assertEqual(
            util.get_valid_to({}, {}),
            util.POSITIVE_INFINITY,
        )

        self.assertEqual(
            util.get_valid_to({}, {
                'validity': None,
            }),
            util.POSITIVE_INFINITY,
        )

        self.assertEqual(
            util.POSITIVE_INFINITY,
            util.get_valid_to({}, {
                'validity': {
                    'to': None,
                },
            }),
        )

        # actually set
        self.assertEqual(
            datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
            util.get_valid_from({
                'validity': {
                    'from': '2018-03-05',
                },
            }),
        )

        self.assertEqual(
            datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
            util.get_valid_from({
                'validity': {
                    'from': '2018-03-05',
                },
            }),
        )

        self.assertEqual(
            datetime.datetime(2018, 3, 6, tzinfo=util.DEFAULT_TIMEZONE),
            util.get_valid_to({
                'validity': {
                    'to': '2018-03-05',
                },
            }),
        )

        # actually set in the fallback
        self.assertEqual(
            datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
            util.get_valid_from({}, {
                'validity': {
                    'from': '2018-03-05',
                },
            }),
        )

        self.assertEqual(
            datetime.datetime(2018, 3, 6, tzinfo=util.DEFAULT_TIMEZONE),
            util.get_valid_to({}, {
                'validity': {
                    'to': '2018-03-05',
                },
            }),
        )

        self.assertEqual(
            datetime.datetime(2018, 3, 6, tzinfo=util.DEFAULT_TIMEZONE),
            util.get_valid_to({}, {
                'validity': {
                    'to': '2018-03-05',
                },
            }),
        )

        self.assertEqual(
            (datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
             datetime.datetime(2018, 4, 5, tzinfo=util.DEFAULT_TIMEZONE)),
            util.get_validities({
                'validity': {
                    'from': '2018-03-05',
                    'to': '2018-04-04',
                },
            }),
        )

        self.assertEqual(
            (datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
             util.POSITIVE_INFINITY),
            util.get_validities({
                'validity': {
                    'from': '2018-03-05'
                },
            }),
        )

        with self.assertRaisesRegex(exceptions.HTTPException,
                                    "End date is before start date"):
            util.get_validities({
                'validity': {
                    'from': '2019-03-05',
                    'to': '2018-03-05',
                },
            })

    def test_get_uuid(self):
        testid = '00000000-0000-0000-0000-000000000000'

        self.assertEqual(
            testid,
            util.get_uuid({
                'uuid': testid,
            }),
        )

        self.assertEqual(
            testid,
            util.get_uuid(
                {},
                {
                    'uuid': testid,
                },
            ),
        )

        self.assertRaises(
            exceptions.HTTPException,
            util.get_uuid,
            {
                'uuid': 42,
            },
        )

        self.assertEqual(
            None,
            util.get_uuid(
                {},
                required=False,
            ),
        )

        self.assertEqual(
            testid,
            util.get_uuid(
                {
                    'kaflaflibob': testid,
                    'uuid': 42,
                },
                key='kaflaflibob',
            ),
        )

    def test_checked_get(self):
        mapping = {
            'list': [1337],
            'dict': {1337: 1337},
            'string': '1337',
            'int': 1337,
            'null': None,
        }

        # when it's there
        self.assertIs(
            util.checked_get(mapping, 'list', []),
            mapping['list'],
        )

        self.assertIs(
            util.checked_get(mapping, 'dict', {}),
            mapping['dict'],
        )

        self.assertIs(
            util.checked_get(mapping, 'string', ''),
            mapping['string'],
        )

        self.assertIs(
            util.checked_get(mapping, 'int', 1337),
            mapping['int'],
        )

        # when it's not there
        self.assertEqual(
            util.checked_get(mapping, 'nonexistent', []),
            [],
        )

        self.assertEqual(
            util.checked_get(mapping, 'nonexistent', {}),
            {},
        )

        self.assertEqual(
            util.checked_get(mapping, 'null', {}),
            {},
        )

        with self.assertRaisesRegex(exceptions.HTTPException,
                                    "Missing nonexistent"):
            util.checked_get(mapping, 'nonexistent', [], required=True)

        with self.assertRaisesRegex(exceptions.HTTPException,
                                    "Missing nonexistent"):
            util.checked_get(mapping, 'nonexistent', {}, required=True)

        # bad value
        with self.assertRaisesRegex(
                exceptions.HTTPException,
                'Invalid \'dict\', expected list, got: {"1337": 1337}',
        ):
            util.checked_get(mapping, 'dict', [])

        with self.assertRaisesRegex(
                exceptions.HTTPException,
                r"Invalid 'list', expected dict, got: \[1337\]",
        ):
            util.checked_get(mapping, 'list', {})

    def test_get_urn(self):
        with self.subTest('bad string'):
            with self.assertRaisesRegex(
                exceptions.HTTPException,
                "invalid urn for 'urn': '42'",
            ) as ctxt:
                util.get_urn({'urn': '42'})

            self.assertEqual(
                {
                    'description': "invalid urn for 'urn': '42'",
                    'error': True,
                    'error_key': 'E_INVALID_URN',
                    'obj': {'urn': '42'},
                    'status': 400,
                },
                ctxt.exception.response.json,
            )

            self.assertEqual(
                "400 Bad Request: invalid urn for 'urn': '42'",
                str(ctxt.exception),
            )

        with self.assertRaisesRegex(
            exceptions.HTTPException,
            "Invalid 'urn', expected str, got: 42",
        ) as ctxt:
            util.get_urn({'urn': 42})

        self.assertEqual(
            {
                'description': "Invalid 'urn', expected str, got: 42",
                'error': True,
                'error_key': 'E_INVALID_TYPE',
                'expected': 'str',
                'actual': 42,
                'key': 'urn',
                'obj': {'urn': 42},
                'status': 400,
            },
            ctxt.exception.response.json,
        )


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

    def test_mapping_fieldtype(self):
        self.assertEqual("FieldTuple(('relationer', 'tilknyttedeitsystemer'), "
                         "FieldTypes.ADAPTED_ZERO_TO_MANY, None)",
                         str(mapping.SINGLE_ITSYSTEM_FIELD))
