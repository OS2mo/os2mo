# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import json
from contextlib import nullcontext as does_not_raise

import dateutil.tz
import pytest
from mora import exceptions
from mora import util
from mora.util import parsedatetime


def get_uuid_test_id():
    return "00000000-0000-0000-0000-000000000000"


@pytest.mark.parametrize(
    "testing_time, expected_time",
    [
        ("01-06-2017", "2017-06-01T00:00:00+02:00"),
        ("31-12-2017", "2017-12-31T00:00:00+01:00"),
        ("infinity", "infinity"),
        ("-infinity", "-infinity"),
        ("2017-07-31T22:00:00+00:00", "2017-08-01T00:00:00+02:00"),
        # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
        # we get it as a space
        ("2017-07-31T22:00:00 00:00", "2017-08-01T00:00:00+02:00"),
        (datetime.date(2015, 6, 1), "2015-06-01T00:00:00+02:00"),
        # check parsing of raw dates
        ("2018-01-01", "2018-01-01T00:00:00+01:00"),
        ("2018-06-01", "2018-06-01T00:00:00+02:00"),
    ],
)
def test_to_lora_time(testing_time, expected_time):
    assert util.to_lora_time(testing_time) == expected_time


@pytest.mark.parametrize(
    "testing_parse_date, expected_parse_date",
    [  # make sure we can round-trip the edge cases correctly
        (util.NEGATIVE_INFINITY, util.NEGATIVE_INFINITY),
        (util.POSITIVE_INFINITY, util.POSITIVE_INFINITY),
        # We frequently get these dates in spreadsheets
        ("31-12-9999", util.POSITIVE_INFINITY),
    ],
)
def test_parse_datetime(testing_parse_date, expected_parse_date):
    assert util.parsedatetime(testing_parse_date) == expected_parse_date


def test_pase_datetime_fallback():
    # test fallback
    string_parse = ("blyf", "flaf")
    assert util.parsedatetime(*string_parse) == "flaf"


@pytest.mark.parametrize(
    "testing_uuid, expected",
    [("00000000-0000-0000-0000-000000000000", True), ("42", False), (None, False)],
)
def test_is_uuid(testing_uuid, expected):
    assert util.is_uuid(testing_uuid) == expected


@pytest.mark.parametrize(
    "testing_cpr, expected",
    [("0101011000", True), ("123456789", False), ("42", False), (None, False)],
)
def test_is_cpr_number(testing_cpr, expected):
    assert util.is_cpr_number(testing_cpr) == expected


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
def test_get_cpr_birthdate(valid_cpr, isodate, expected_raise):
    with expected_raise:
        assert util.get_cpr_birthdate(valid_cpr) == util.from_iso_time(isodate)


@pytest.mark.parametrize(
    "quote, expected_quote",
    [
        ("42", "42"),
        ("abc", "abc"),
        ("aBc", "a%42c"),
        # from https://docs.python.org/3/library/urllib.parse.html
        ("el niño", "el%20ni%c3%b1o"),
        ("El Niño", "%45l%20%4ei%c3%b1o"),
    ],
)
def test_urnquote(quote, expected_quote):
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
def test_get_obj(obj, path, expected_location):
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
def test_set_obj(obj, path, value, expected_result):
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
        (({}, {}), None, pytest.raises(exceptions.HTTPException)),
        (({}, {"validity": None}), None, pytest.raises(exceptions.HTTPException)),
        (
            ({}, {"validity": {"from": None}}),
            None,
            pytest.raises(exceptions.HTTPException),
        ),
        (
            ({"validity": {"from": "2018-03-05"}}, None),
            datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
            does_not_raise(),
        ),
        (
            ({}, {"validity": {"from": "2018-03-05"}}),
            datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
            does_not_raise(),
        ),
    ],
)
def test_get_valid_from(valid_from, expected_result, expected_raise):
    with expected_raise:
        assert util.get_valid_from(*valid_from) == expected_result


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
        (({}, {}), util.POSITIVE_INFINITY),
        (({}, {"validity": None}), util.POSITIVE_INFINITY),
        (({}, {"validity": {"to": None}}), util.POSITIVE_INFINITY),
        (
            ({"validity": {"to": "2018-03-05"}}, None),
            datetime.datetime(2018, 3, 6, tzinfo=util.DEFAULT_TIMEZONE),
        ),
        (
            ({}, {"validity": {"to": "2018-03-05"}}),
            datetime.datetime(2018, 3, 6, tzinfo=util.DEFAULT_TIMEZONE),
        ),
    ],
)
def test_get_valid_to(valid_to, expected_result):
    assert util.get_valid_to(*valid_to) == expected_result


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
        (
            {"validity": {"from": "2018-03-05", "to": "2018-04-04"}},
            (
                datetime.datetime(2018, 3, 5, tzinfo=util.DEFAULT_TIMEZONE),
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
def test_get_validities(validations, expected_result, expected_raise):
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
        assert util.get_uuid(*value) == get_uuid_test_id()


def test_get_uuid_with_required():
    assert util.get_uuid({}, required=False) is None


def test_get_uuid_with_key():
    testing_uuid = get_uuid_test_id()
    key = "kaflabibob"
    assert util.get_uuid({key: testing_uuid, "uuid": 42}, key=key) == testing_uuid


@pytest.mark.parametrize(
    "key, default, required, expected_raise",
    [
        ("list", [], False, does_not_raise()),
        ("dict", {}, False, does_not_raise()),
        ("string", "", False, does_not_raise()),
        ("int", 1337, False, does_not_raise()),
        ("nonexistent", [], False, does_not_raise()),
        ("nonexistent", {}, False, does_not_raise()),
        ("null", None, False, does_not_raise()),
        ("empty_list", [], False, does_not_raise()),
        ("empty_dict", {}, False, does_not_raise()),
        (
            "nonexistent",
            [],
            True,
            pytest.raises(
                exceptions.HTTPException, match="ErrorCodes.V_MISSING_REQUIRED_VALUE"
            ),
        ),
        (
            "nonexistent",
            {},
            True,
            pytest.raises(
                exceptions.HTTPException, match="ErrorCodes.V_MISSING_REQUIRED_VALUE"
            ),
        ),
    ],
)
def test_checked_get_py(key, default, required, expected_raise):
    mapping = {
        "list": [1337],
        "dict": {1337: 1337},
        "string": "1337",
        "int": 1337,
        "null": None,
        "empty_list": [],
        "empty_dict": {},
        "empty_str": "",
    }
    with expected_raise:
        assert util.checked_get(
            mapping, key, default, required=required
        ) == mapping.get(key, default)


@pytest.mark.parametrize(
    "key, default, required",
    [
        ("dict", [], False),
        ("list", {}, False),
        ("int", "", False),
        ("empty_list", [], True),
        ("empty_dict", {}, True),
        ("empty_str", "", True),
    ],
)
def test_checked_get_exception(key, default, required):
    mapping = {
        "dict": {1337: 1337},
        "empty_dict": {},
        "empty_list": [],
        "empty_str": "",
        "int": 1337,
        "list": [1337],
        "null": None,
        "string": "1337",
    }
    output = {
        "description": f"'{key}' cannot be empty",
        "error": True,
        "error_key": "V_MISSING_REQUIRED_VALUE",
        "key": key,
        "obj": mapping,
        "status": 400,
    }
    if not required and mapping.get(key) is not None:
        expected = type(default).__name__
        output["error_key"] = "E_INVALID_TYPE"
        output["description"] = "Invalid '{}', expected {}, got: {}".format(
            key, expected, json.dumps(mapping.get(key))
        )
        output["actual"] = mapping.get(key)
        output["expected"] = expected

    with pytest.raises(exceptions.HTTPException) as err:
        util.checked_get(mapping, key, default, required=required, can_be_empty=False)
    assert output == err.value.detail


def test_know_timezone_trigger():
    start = "2052-06-30 22:00:00+00"
    end = "2052-06-30 23:00:00+00"

    validity = util.get_validity_object(start, end)

    assert parsedatetime(validity["from"]) <= parsedatetime(validity["to"])
