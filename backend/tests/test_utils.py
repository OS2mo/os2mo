# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import datetime

import dateutil.tz
import freezegun
import pytest

from .cases import TestCase
from mora import exceptions
from mora import util

from contextlib import nullcontext as does_not_raise


@freezegun.freeze_time("2015-06-01T01:10")
class TestUtils(TestCase):
    def test_checked_get(self):
        mapping = {
            "list": [1337],
            "dict": {1337: 1337},
            "string": "1337",
            "int": 1337,
            "null": None,
            "empty_list": list(),
            "empty_dict": dict(),
            "empty_str": str(),
        }

        # when it's there
        self.assertIs(
            util.checked_get(mapping, "list", []),
            mapping["list"],
        )

        self.assertIs(
            util.checked_get(mapping, "dict", {}),
            mapping["dict"],
        )

        self.assertIs(
            util.checked_get(mapping, "string", ""),
            mapping["string"],
        )

        self.assertIs(
            util.checked_get(mapping, "int", 1337),
            mapping["int"],
        )

        # when it's not there
        self.assertEqual(
            util.checked_get(mapping, "nonexistent", []),
            [],
        )

        self.assertEqual(
            util.checked_get(mapping, "nonexistent", {}),
            {},
        )

        self.assertEqual(
            util.checked_get(mapping, "null", {}),
            {},
        )

        self.assertEqual(
            util.checked_get(mapping, "empty_list", []),
            [],
        )

        self.assertEqual(
            util.checked_get(mapping, "empty_dict", {}),
            {},
        )

        with self.assertRaisesRegex(
            exceptions.HTTPException, "ErrorCodes.V_MISSING_REQUIRED_VALUE"
        ):
            util.checked_get(mapping, "nonexistent", [], required=True)

        with self.assertRaisesRegex(
            exceptions.HTTPException, "ErrorCodes.V_MISSING_REQUIRED_VALUE"
        ):
            util.checked_get(mapping, "nonexistent", {}, required=True)

        # bad value
        with self.assertRaises(exceptions.HTTPException) as err:
            util.checked_get(mapping, "dict", [])

        self.assertEqual(
            {
                "actual": {1337: 1337},
                "description": "Invalid 'dict', " 'expected list, got: {"1337": 1337}',
                "error": True,
                "error_key": "E_INVALID_TYPE",
                "expected": "list",
                "key": "dict",
                "obj": {
                    "dict": {1337: 1337},
                    "empty_dict": {},
                    "empty_list": [],
                    "empty_str": "",
                    "int": 1337,
                    "list": [1337],
                    "null": None,
                    "string": "1337",
                },
                "status": 400,
            },
            err.exception.detail,
        )

        with self.assertRaises(exceptions.HTTPException) as err:
            util.checked_get(mapping, "list", {})
        self.assertEqual(
            {
                "actual": [1337],
                "description": "Invalid 'list', expected dict, got: [1337]",
                "error": True,
                "error_key": "E_INVALID_TYPE",
                "expected": "dict",
                "key": "list",
                "obj": {
                    "dict": {1337: 1337},
                    "empty_dict": {},
                    "empty_list": [],
                    "empty_str": "",
                    "int": 1337,
                    "list": [1337],
                    "null": None,
                    "string": "1337",
                },
                "status": 400,
            },
            err.exception.detail,
        )

        with self.assertRaises(exceptions.HTTPException) as err:
            util.checked_get(
                mapping, "empty_list", [], required=True, can_be_empty=False
            )
        self.assertEqual(
            {
                "description": "'empty_list' cannot be empty",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "key": "empty_list",
                "obj": {
                    "dict": {1337: 1337},
                    "empty_dict": {},
                    "empty_list": [],
                    "empty_str": "",
                    "int": 1337,
                    "list": [1337],
                    "null": None,
                    "string": "1337",
                },
                "status": 400,
            },
            err.exception.detail,
        )

        with self.assertRaises(exceptions.HTTPException) as err:
            util.checked_get(
                mapping, "empty_dict", {}, required=True, can_be_empty=False
            )
        self.assertEqual(
            {
                "description": "'empty_dict' cannot be empty",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "key": "empty_dict",
                "obj": {
                    "dict": {1337: 1337},
                    "empty_dict": {},
                    "empty_list": [],
                    "empty_str": "",
                    "int": 1337,
                    "list": [1337],
                    "null": None,
                    "string": "1337",
                },
                "status": 400,
            },
            err.exception.detail,
        )

        with self.assertRaises(exceptions.HTTPException) as err:
            util.checked_get(
                mapping, "empty_str", "", required=True, can_be_empty=False
            )

        self.assertEqual(
            {
                "description": "'empty_str' cannot be empty",
                "error": True,
                "error_key": "V_MISSING_REQUIRED_VALUE",
                "key": "empty_str",
                "obj": {
                    "dict": {1337: 1337},
                    "empty_dict": {},
                    "empty_list": [],
                    "empty_str": "",
                    "int": 1337,
                    "list": [1337],
                    "null": None,
                    "string": "1337",
                },
                "status": 400,
            },
            err.exception.detail,
        )


def get_uuid_test_id():
    return "00000000-0000-0000-0000-000000000000"


@freezegun.freeze_time("2015-06-01T01:10")
def frozen_time_now():
    return util.now()


def frozen_time_today():
    return frozen_time_now().replace(hour=0, minute=0, second=0, microsecond=0)


# class TestUtilsPy:
@pytest.mark.parametrize(
    "trying_time, expected_time",
    [
        (frozen_time_today(), "2015-06-01T00:00:00+02:00"),
        (frozen_time_now(), "2015-06-01T01:10:00+02:00"),
        ("2017-06-01", "2017-06-01T00:00:00+02:00"),
        ("01-06-2017", "2017-06-01T00:00:00+02:00"),
        ("31-12-2017", "2017-12-31T00:00:00+01:00"),
        ("infinity", "infinity"),
        ("-infinity", "-infinity"),
        ("2017-07-31T22:00:00+00:00", "2017-08-01T00:00:00+02:00"),
        # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
        # we get it as a space
        ("2017-07-31T22:00:00 00:00", "2017-08-01T00:00:00+02:00"),
        (datetime.date(2015, 6, 1), "2015-06-01T00:00:00+02:00"),
        ("2018-01-01", "2018-01-01T00:00:00+01:00"),
        ("2018-06-01", "2018-06-01T00:00:00+02:00"),
    ],
)
def test_to_lora_time_py(trying_time, expected_time):
    assert util.to_lora_time(trying_time) == expected_time


@pytest.mark.parametrize(
    "trying_parse_date, expected_parse_date",
    [
        (util.NEGATIVE_INFINITY, util.NEGATIVE_INFINITY),
        (util.POSITIVE_INFINITY, util.POSITIVE_INFINITY),
        # We frequently get these dates in spreadsheets
        ("31-12-9999", util.POSITIVE_INFINITY),
    ],
)
def test_parse_datetime_py(trying_parse_date, expected_parse_date):
    assert util.parsedatetime(trying_parse_date) == expected_parse_date


@pytest.mark.parametrize(
    "trying_uuid, expected",
    [("00000000-0000-0000-0000-000000000000", True), ("42", False), (None, False)],
)
def test_is_uuid_py(trying_uuid, expected):
    assert util.is_uuid(trying_uuid) == expected


@pytest.mark.parametrize(
    "trying_cpr, expected",
    [("0101011000", True), ("123456789", False), ("42", False), (None, False)],
)
def test_is_cpr_number_py(trying_cpr, expected):
    assert util.is_cpr_number(trying_cpr) == expected


@pytest.mark.parametrize(
    "valid_cpr, isodate, expected_raise",
    [
        (1010771999, "1977-10-10", does_not_raise()),
        (1010274999, "2027-10-10", does_not_raise()),
        (1010774999, "1977-10-10", does_not_raise()),
        (1010575999, "2057-10-10", does_not_raise()),
        (1010775999, "1877-10-10", does_not_raise()),
        (1010776999, "1877-10-10", does_not_raise()),
        (1010476999, "2047-10-10", does_not_raise()),
        (1010359999, "2035-10-10", does_not_raise()),
        (1010779999, "1977-10-10", does_not_raise()),
        ("1205320000", "1932-05-12", does_not_raise()),
        ("0906340000", "1934-06-09", does_not_raise()),
        ("0905380000", "1938-05-09", does_not_raise()),
        ("0000000000", "", pytest.raises(ValueError, match="^invalid CPR number")),
        (2222222222, "", pytest.raises(ValueError, match="^invalid CPR number")),
        (10101010000, "", pytest.raises(ValueError, match="^invalid CPR number")),
    ],
)
def test_get_cpr_birthdate_py(valid_cpr, isodate, expected_raise):
    with expected_raise:
        assert util.get_cpr_birthdate(valid_cpr) == util.from_iso_time(isodate)


@pytest.mark.parametrize(
    "quote, expected_quote",
    [
        ("42", "42"),
        ("abc", "abc"),
        ("aBc", "a%42c"),
        ("el niño", "el%20ni%c3%b1o"),
        ("El Niño", "%45l%20%4ei%c3%b1o"),
    ],
)
def test_urnquote_py(quote, expected_quote):
    assert util.urnquote(quote) == expected_quote
    assert util.urnunquote(util.urnquote(quote)) == quote


@pytest.mark.parametrize(
    "obj, path, expected_location",
    [
        (
            {
                "whatever": "no",
                "test1": {
                    "garbage": "there is some stuff here already",
                    "test2": ["something"],
                },
            },
            ("test1", "test2"),
            ["something"],
        ),
        ({"whatever": "no", "test1": None}, ("test1", "test2"), None),  # None
        ({"whatever": "no"}, ("test1",), None),  # Missing
        ({"whatever": "no", "test1": 42}, ("test1", "test2"), None),  # Weird
    ],
)
def test_get_obj_py(obj, path, expected_location):
    assert util.get_obj_value(obj, path) == expected_location


@pytest.mark.parametrize(
    "obj, path, value, expected_result",
    [
        (
            {"test1": {"test2": [{"key1": "val1"}]}},
            ("test1", "test2"),
            [{"key2": "val2"}],
            {"test1": {"test2": [{"key1": "val1"}, {"key2": "val2"}]}},
        ),  # Existing path.
        (
            {},
            ("test1", "test2"),
            [{"key2": "val2"}],
            {"test1": {"test2": [{"key2": "val2"}]}},
        ),  # New path.
        (
            {"test1": {"test2": "1337"}},
            ("test1", "test2"),
            "42",
            {"test1": {"test2": "42"}},
        ),  # Existing path string.
        ({}, ("test1", "test2"), "42", {"test1": {"test2": "42"}}),  # New path string.
    ],
)
def test_set_obj_py(obj, path, value, expected_result):
    assert util.set_obj_value(obj, path, value) == expected_result


@pytest.mark.parametrize(
    "valid_from, expected_result, expected_raise",
    [
        (
            ({"validity": {"from": "2018-03-21T00:00:00+01:00"}}, None),
            datetime.datetime(2018, 3, 21, tzinfo=dateutil.tz.tzoffset(None, 3600)),
            does_not_raise(),
        ),
        (
            ({"validity": {}}, {"validity": {"from": "2018-03-21T00:00:00+01:00"}}),
            datetime.datetime(2018, 3, 21, tzinfo=dateutil.tz.tzoffset(None, 3600)),
            does_not_raise(),
        ),
        (({}, None), None, pytest.raises(exceptions.HTTPException)),
        (({"validity": {}}, None), None, pytest.raises(exceptions.HTTPException)),
        (({}, {"validity": {}}), None, pytest.raises(exceptions.HTTPException)),
        (
            ({}, {"validity": {"from": None}}),
            None,
            pytest.raises(exceptions.HTTPException),
        ),
        (({}, {}), None, pytest.raises(exceptions.HTTPException)),  # Tests from 413
        (({}, {"validity": None}), None, pytest.raises(exceptions.HTTPException)),
        (
            ({}, {"validity": {"from": None}}),
            None,
            pytest.raises(exceptions.HTTPException),
        ),
        (
            ({"validity": {"from": "2018-03-05"}}, None),  # From 477
            datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
            does_not_raise(),
        ),
        (
            ({}, {"validity": {"from": "2018-03-05"}}),
            datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
            does_not_raise(),
        )
        # 511
    ],
)
def test_get_valid_from_py(valid_from, expected_result, expected_raise):
    with expected_raise:
        assert util.get_valid_from(valid_from[0], valid_from[1]) == expected_result


@pytest.mark.parametrize(
    "valid_to, expected_result",
    [
        (
            ({"validity": {"to": "2018-03-21"}}, {}),
            datetime.datetime(2018, 3, 22, tzinfo=dateutil.tz.tzoffset(None, 3600)),
        ),
        (
            ({"validity": {}}, {"validity": {"to": "2018-03-21"}}),
            datetime.datetime(2018, 3, 22, tzinfo=dateutil.tz.tzoffset(None, 3600)),
        ),
        (({}, {}), util.POSITIVE_INFINITY),
        (({"validity": {}}, {}), util.POSITIVE_INFINITY),
        (({}, {"validity": {}}), util.POSITIVE_INFINITY),
        (({"validity": {"to": None}}, {}), util.POSITIVE_INFINITY),
        (({}, {"validity": {"to": None}}), util.POSITIVE_INFINITY),
        (({}, {}), util.POSITIVE_INFINITY),  # From 442
        (({}, {"validity": None}), util.POSITIVE_INFINITY),
        (({}, {"validity": {"to": None}}), util.POSITIVE_INFINITY),
        (
            ({"validity": {"to": "2018-03-05"}}, None),
            datetime.datetime(2018, 3, 6, tzinfo=util.DEFAULT_TIMEZONE),
        ),  # 482
        (
            ({}, {"validity": {"to": "2018-03-05"}}),
            datetime.datetime(2018, 3, 6, tzinfo=util.DEFAULT_TIMEZONE),
        ),
    ],
)
def test_get_valid_to_py(valid_to, expected_result):
    assert util.get_valid_to(valid_to[0], valid_to[1]) == expected_result


@pytest.mark.parametrize(
    "validations, expected_result, expected_raise",
    [
        (
            {"validity": {"from": "2018-03-05", "to": "2018-04-04"}},
            (
                datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
                datetime.datetime(2018, 4, 5, tzinfo=util.DEFAULT_TIMEZONE),
            ),
            does_not_raise(),
        ),  # From 550
        (
            {"validity": {"from": "2018-03-05"}},
            (
                datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
                util.POSITIVE_INFINITY,
            ),
            does_not_raise(),
        ),
        (
            {"validity": {"from": "2019-03-05", "to": "2018-03-05"}},
            None,
            pytest.raises(exceptions.HTTPException),
        ),
        (
            {
                "description": "End date is before start date.",
                "error": True,
                "error_key": "V_END_BEFORE_START",
                "obj": {"validity": {"from": "2019-03-05", "to": "2018-03-05"}},
                "status": 400,
            },
            None,
            pytest.raises(exceptions.HTTPException),
        ),
        (
            {"validity": {"from": "2018-03-05", "to": "2018-04-04"}},
            (
                datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),  # 518
                datetime.datetime(2018, 4, 5, tzinfo=util.DEFAULT_TIMEZONE),
            ),
            does_not_raise(),
        ),
        (
            {"validity": {"from": "2018-03-05"}},
            (
                datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
                util.POSITIVE_INFINITY,
            ),
            does_not_raise(),
        ),
        (
            {"validity": {"from": "2019-03-05", "to": "2018-03-05"}},
            None,
            pytest.raises(exceptions.HTTPException),
        ),
        (
            {
                "description": "End date is before start date.",
                "error": True,
                "error_key": "V_END_BEFORE_START",
                "obj": {"validity": {"from": "2019-03-05", "to": "2018-03-05"}},
                "status": 400,
            },
            None,
            pytest.raises(exceptions.HTTPException),
        ),
    ],
)
def test_get_validities_py(validations, expected_result, expected_raise):
    with expected_raise:
        assert util.get_validities(validations) == expected_result


@pytest.mark.parametrize(
    "value, expected_raise",
    [
        (({"uuid": get_uuid_test_id()}, None), does_not_raise()),
        (({}, {"uuid": get_uuid_test_id()}), does_not_raise()),
        (({"uuid": 42}, None), pytest.raises(exceptions.HTTPException)),
    ],
)
def test_get_uuid_py(value, expected_raise):
    with expected_raise:
        assert util.get_uuid(value[0], value[1]) == get_uuid_test_id()


@pytest.mark.parametrize("value, expected_result", [(({}, False), None)])
def test_get_uuid_with_required_py(value, expected_result):
    assert util.get_uuid(value[0], value[1], required=False) == expected_result


@pytest.mark.parametrize(
    "value",
    [
        (
            {"kaflaflibob": get_uuid_test_id(), "uuid": 42},
            "kaflaflibob",
        )
    ],
)
def test_get_uuid_with_key_py(value):
    assert util.get_uuid(value[0], value[1], key="kaflaflibob") == get_uuid_test_id()
