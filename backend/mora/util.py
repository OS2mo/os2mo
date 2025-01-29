# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
""" "
Utility methods
---------------

This module contains various utility methods, i.e. a collection of
various small functions used in many places.

"""

import copy
import datetime
import io
import json
import operator
import re
import typing
import urllib.parse
import uuid
from contextlib import suppress
from functools import reduce
from uuid import UUID
from zoneinfo import ZoneInfo

import dateutil.parser
import dateutil.tz
from ramodels.base import to_parsable_timestamp
from starlette_context import context
from structlog import get_logger

from . import config
from . import exceptions
from . import mapping

_sentinel = object()

# timezone-aware versions of min/max
POSITIVE_INFINITY = datetime.datetime.max.replace(tzinfo=datetime.UTC)
NEGATIVE_INFINITY = datetime.datetime.min.replace(tzinfo=datetime.UTC)
MINIMAL_INTERVAL = datetime.timedelta(microseconds=1)
ONE_DAY = datetime.timedelta(days=1)

# TODO: the default timezone should be configurable, shouldn't it?
DEFAULT_TIMEZONE = ZoneInfo("Europe/Copenhagen")

_tzinfos = {
    None: DEFAULT_TIMEZONE,
    0: dateutil.tz.tzutc,
    1 * 60**2: DEFAULT_TIMEZONE,
    2 * 60**2: DEFAULT_TIMEZONE,
}

logger = get_logger()


def parsedatetime(
    s: str | datetime.date | datetime.datetime, default=_sentinel
) -> datetime.datetime:
    if isinstance(s, datetime.date):
        dt = s

        if dt in (POSITIVE_INFINITY, NEGATIVE_INFINITY):
            return dt

        if not isinstance(dt, datetime.datetime):
            dt = datetime.datetime.combine(
                dt,
                datetime.time(),
            )

        if not dt.tzinfo:
            dt = dt.replace(tzinfo=DEFAULT_TIMEZONE)

        return dt

    elif s == "infinity":
        return POSITIVE_INFINITY
    elif s == "-infinity":
        return NEGATIVE_INFINITY

    if " " in s:
        # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
        # we get it as a space
        s = re.sub(r" (?=\d\d:\d\d$)", "+", s)

    with suppress(ValueError):
        return from_iso_time(s)

    try:
        dt = dateutil.parser.parse(
            to_parsable_timestamp(s), dayfirst=True, tzinfos=_tzinfos
        )
    except ValueError:
        if default is not _sentinel:
            return default
        else:
            exceptions.ErrorCodes.E_INVALID_INPUT(f"cannot parse {s!r}")

    if dt.date() == POSITIVE_INFINITY.date():
        return POSITIVE_INFINITY

    dt = dt.astimezone(DEFAULT_TIMEZONE)

    return dt


def do_ranges_overlap(first_start, first_end, second_start, second_end):
    return max(first_start, second_start) < min(first_end, second_end)


def to_lora_time(s: str | datetime.date | datetime.datetime) -> str:
    dt = parsedatetime(s)

    if dt == POSITIVE_INFINITY:
        return "infinity"
    elif dt == NEGATIVE_INFINITY:
        return "-infinity"
    return dt.isoformat()


def to_iso_date(s, is_end: bool = False):
    """Return an ISO 8601 string representing date given by ``s``.

    We round times up or down, depending on whether ``is_end`` is set.
    Since the dates are *inclusive*, we round *down* for start
    dates and *up* for end dates.

    :param bool is_end: whether to round the time up or down.

    .. doctest::

        >>> to_iso_date('2001-01-01T00:00')
        '2001-01-01'
        >>> to_iso_date('2001-01-01T12:00')
        '2001-01-01'
        >>> to_iso_date('2001-01-01T00:00', is_end=True)
        '2000-12-31'
        >>> to_iso_date('2001-01-01T12:00', is_end=True)
        '2000-12-31'
        >>> to_iso_date('2000-20-20')
        Traceback (most recent call last):
        ...
        mora.exceptions.HTTPException: 400 Bad Request: \
        cannot parse '2000-20-20'
        >>> to_iso_date(POSITIVE_INFINITY, is_end=True)
        >>> to_iso_date(NEGATIVE_INFINITY)

    """
    dt = parsedatetime(s)

    if is_end and dt.year == POSITIVE_INFINITY.year:
        return None
    elif not is_end and dt.year == NEGATIVE_INFINITY.year:
        return None

    if dt.tzinfo != DEFAULT_TIMEZONE and dt.year != POSITIVE_INFINITY.year:
        dt = dt.astimezone(DEFAULT_TIMEZONE)

    if is_end:
        dt -= datetime.timedelta(minutes=1)

    return dt.date().isoformat()


def from_iso_time(s):
    dt = dateutil.parser.isoparse(s)

    if not dt.tzinfo:
        dt = dt.replace(tzinfo=DEFAULT_TIMEZONE)
    else:
        dt = dt.astimezone(DEFAULT_TIMEZONE)

    return dt


def now() -> datetime.datetime:
    """Get the current time, localized to the current time zone."""
    return datetime.datetime.now(tz=DEFAULT_TIMEZONE)


def is_uuid(v):
    try:
        uuid.UUID(v)
        return True
    except Exception:
        return False


def is_cpr_number(v) -> bool:
    try:
        CPR.validate(v)
        return True
    except ValueError:
        return False


class CPR(str):
    """CPR Validation.

    Based on: https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        settings = config.get_settings()

        # First, check length of value given
        len_ok = v and len(v) == 10
        if not len_ok:
            raise ValueError("Invalid length")

        # Then, check birthdate
        if settings.cpr_validate_birthdate:
            try:
                birthdate_ok = bool(get_cpr_birthdate(v))
            except (TypeError, ValueError):
                birthdate_ok = False
        else:
            birthdate_ok = True
        if not birthdate_ok:
            raise ValueError("Birthdate not ok")

        return v

    def __repr__(self):
        return f"CPR({super().__repr__()})"


def get_cpr_birthdate(number: int | str) -> datetime.datetime:
    if isinstance(number, str):
        number = int(number)

    rest, code = divmod(number, 10000)
    rest, year = divmod(rest, 100)
    rest, month = divmod(rest, 100)
    rest, day = divmod(rest, 100)

    if rest:
        raise ValueError(f"invalid CPR number {number}")

    # see https://da.wikipedia.org/wiki/CPR-nummer :(
    if code < 4000:
        century = 1900
    elif code < 5000:
        century = 2000 if year <= 36 else 1900
    elif code < 9000:
        century = 2000 if year <= 57 else 1800
    else:
        century = 2000 if year <= 36 else 1900

    try:
        return datetime.datetime(century + year, month, day, tzinfo=DEFAULT_TIMEZONE)
    except ValueError:
        raise ValueError(f"invalid CPR number {number}")


URN_SAFE = frozenset(b"abcdefghijklmnopqrstuvwxyz0123456789+")


def urnquote(s):
    """Quote the given string so that it may safely pass through
    case-insensitive URN handling.

    Strictly speaking, the resulting string is not valid for a URN, as
    they may not contain anything other than colon, letters and
    digits. We add '+' and '%' to the mix so that we can roundtrip
    arbitrary text. Meh.

    """

    if not s:
        return ""

    with io.StringIO("w") as buf:
        for character in s.encode("utf-8"):
            if character in URN_SAFE:
                buf.write(chr(character))
            else:
                buf.write(f"%{character:02x}")

        return buf.getvalue()


# provide an alias for consistency
urnunquote = urllib.parse.unquote
K = typing.TypeVar("K", bound=typing.Hashable)
V = typing.TypeVar("V")
D = dict[K, V]


def checked_get(
    mapping: D,
    key: K,
    default: V,
    fallback: D = None,
    required: bool = False,
    can_be_empty: bool = True,
) -> V:
    """
    Get a value from a parsed JSON object, verifying that the value is of the
    expected type

    :param mapping: The object to get a value from
    :param key: The key to use
    :param default: A default value to use if nothing is found. The default is also used
        to check the type
    :param fallback: A fallback object to use if lookup in the first object fails
    :param required: Whether the value is required. Will raise an HTTPException if
        no value is found
    :param can_be_empty: Whether the found value can be empty. Will raise an
        HTTPException if found value is empty
    :return:
    """
    try:
        v = mapping[key]
    except (LookupError, TypeError):
        exc = exceptions.HTTPException(
            exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE,
            message=f"Missing {key}",
            key=key,
            obj=mapping,
        )

        if fallback is not None:
            try:
                return checked_get(fallback, key, default, required=required)
            except exceptions.HTTPException:
                # ensure that we raise an exception describing the
                # current object, even if a fallback was specified
                raise exc

        elif required:
            raise exc
        return default

    if not isinstance(v, type(default)):
        if v is None:
            if not required:
                return default
            else:
                exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
                    message=f"Missing {key}",
                    key=key,
                    obj=mapping,
                )

        expected = type(default).__name__
        actual = v
        exceptions.ErrorCodes.E_INVALID_TYPE(
            message="Invalid {!r}, expected {}, got: {}".format(
                key,
                expected,
                json.dumps(actual),
            ),
            key=key,
            expected=expected,
            actual=actual,
            obj=mapping,
        )

    if not can_be_empty and type(v) in {list, dict, str} and len(v) == 0:
        exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
            message=f"'{key}' cannot be empty",
            key=key,
            obj=mapping,
        )

    return v


def get_uuid(
    mapping: D,
    fallback: D = None,
    *,
    required: bool = True,
    key: typing.Hashable = mapping.UUID,
) -> str | None:
    v = checked_get(mapping, key, "", fallback=fallback, required=required)

    if not v and not required:
        return None
    elif not is_uuid(v):
        exceptions.ErrorCodes.E_INVALID_UUID(
            message=f"Invalid uuid for {key!r}: {v!r}", obj=mapping
        )

    return v


def get_mapping_uuid(mapping, key, *, fallback=None, required=False):
    """Extract a UUID from a mapping structure identified by 'key'.
    Expects a structure along the lines of:

    .. sourcecode:: python

      {
        "org": {
          "uuid": "<UUID>"
        }
      }

    """
    obj = checked_get(mapping, key, {}, fallback=fallback, required=required)

    if obj:
        return get_uuid(obj)
    return None


def set_obj_value(obj: dict, path: tuple, val: list[dict]):
    path_list = list(path)
    obj_copy = copy.deepcopy(obj)

    current_value = obj_copy

    for key in path_list[:-1]:
        current_value = current_value.setdefault(key, {})

    key = path_list[-1]

    if isinstance(current_value.get(key), list):
        current_value[key].extend(val)
    else:
        current_value[key] = val

    return obj_copy


T = typing.TypeVar("T")


def get_obj_value(
    obj,
    path: tuple[str, str],
    filter_fn: typing.Callable[[dict], bool] = None,
    default: T = None,
) -> T | None:
    try:
        props = reduce(operator.getitem, path, obj)
    except (LookupError, TypeError):
        return default

    if filter_fn:
        return list(filter(filter_fn, props))
    return props


def get_obj_uuid(obj, path: tuple):
    (obj,) = get_obj_value(obj, path, default={})
    return get_uuid(obj)


def get_effect_from(effect: dict) -> datetime.datetime:
    return parsedatetime(effect["virkning"]["from"])


def get_effect_to(effect: dict) -> datetime.datetime:
    return parsedatetime(effect["virkning"]["to"])


def get_effect_validity(effect):
    return {
        mapping.FROM: to_iso_date(get_effect_from(effect)),
        mapping.TO: to_iso_date(get_effect_to(effect), is_end=True),
    }


def get_valid_from(obj, fallback=None) -> datetime.datetime:
    """
    Extract the start of the validity interval in ``obj``, or otherwise
    ``fallback``, and return it as a timestamp delimiting the
    corresponding interval.

    raises mora.exceptions.HTTPException: if the given timestamp does
      not correspond to midnight in Central Europe.
    raises mora.exceptions.HTTPException: if neither ``obj`` nor ``fallback``
      specifiy a validity start.

    .. doctest::

      >>> get_valid_from({'validity': {'from': '2000-01-01'}})
      datetime.datetime(2000, 1, 1, 0, 0, \
      tzinfo=tzfile('/usr/share/zoneinfo/Europe/Copenhagen'))

      >>> get_valid_from({})
      Traceback (most recent call last):
      ...
      mora.exceptions.HTTPException: 400 Bad Request: Missing start date.
      >>> get_valid_from({'validity': {'from': '2000-01-01T12:00Z'}})
      Traceback (most recent call last):
      ...
      mora.exceptions.HTTPException: \
      400 Bad Request: '2000-01-01T13:00:00+01:00' is not at midnight!

    """
    sentinel = object()
    validity = obj.get(mapping.VALIDITY, sentinel)

    if validity and validity is not sentinel:
        valid_from = validity.get(mapping.FROM, sentinel)
        if valid_from is None:
            exceptions.ErrorCodes.V_MISSING_START_DATE(obj=obj)
        elif valid_from is not sentinel:
            dt = from_iso_time(valid_from)

            if dt.time() != datetime.time.min:
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    f"{dt.isoformat()!r} is not at midnight!",
                )

            return dt

    if fallback is not None:
        return get_valid_from(fallback)
    else:
        exceptions.ErrorCodes.V_MISSING_START_DATE(obj=obj)


def get_valid_to(obj, fallback=None, required=False) -> datetime.datetime:
    """Extract the end of the validity interval in ``obj``, or otherwise
    ``fallback``, and return it as a timestamp delimiting the
    corresponding interval. If neither specifies an end, assume a
    timestamp far in the future — practically infinite, in fact.

    Please note that as end intervals are *inclusive*, a date ends at
    24:00, or 0:00 the following day.

    :see also: :py:func:`to_iso_date`

    raises mora.exceptions.HTTPException: if the given timestamp does
      not correspond to midnight in Central Europe.
    raises mora.exceptions.HTTPException: if neither ``obj`` nor ``fallback``
      specifiy a validity start.

    .. doctest::

      >>> get_valid_to({'validity': {'to': '1999-12-31'}})
      datetime.datetime(2000, 1, 1, 0, 0, \
      tzinfo=tzfile('/usr/share/zoneinfo/Europe/Copenhagen'))
      >>> get_valid_to({}) == POSITIVE_INFINITY
      True

      >>> get_valid_to({'validity': {'to': '1999-12-31T12:00Z'}})
      Traceback (most recent call last):
      ...
      mora.exceptions.HTTPException: \
      400 Bad Request: '1999-12-31T13:00:00+01:00' is not at midnight!

    """
    sentinel = object()
    validity = obj.get(mapping.VALIDITY, sentinel)

    if validity and validity is not sentinel:
        valid_to = validity.get(mapping.TO, sentinel)

        if valid_to is None:
            return POSITIVE_INFINITY

        elif valid_to is not sentinel:
            dt = from_iso_time(valid_to)

            if dt.time() != datetime.time.min:
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    f"{dt.isoformat()!r} is not at midnight!",
                )

            # this is the reverse of to_iso_date, and an end date
            # _includes_ the day in question, so the end of the
            # interval corresponds to 24:00 on that day
            return dt + ONE_DAY

    if fallback is not None:
        return get_valid_to(fallback, required=required)
    elif not required:
        return POSITIVE_INFINITY
    else:
        exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
            message=f"Missing {mapping.VALIDITY}",
            key=mapping.VALIDITY,
            obj=obj,
        )


def get_validities(obj, fallback=None) -> tuple[datetime.datetime, datetime.datetime]:
    valid_from = get_valid_from(obj, fallback)
    valid_to = get_valid_to(obj, fallback)
    if valid_to < valid_from:
        exceptions.ErrorCodes.V_END_BEFORE_START(obj=obj)
    return valid_from, valid_to


# todo: timezone, quickfix, remove when the timezone mess in 56846 is fixed
def get_validity_object(start, end):
    return {mapping.FROM: to_iso_date(start), mapping.TO: to_iso_date(end, is_end=True)}


def get_states(reg):
    for tilstand in reg.get("tilstande", {}).values():
        yield from tilstand


def is_reg_valid(reg):
    """
    Check if a given registration is valid
    i.e. that the registration contains a 'gyldighed' that is 'Aktiv'

    :param reg: A registration object
    """

    return any(state.get("gyldighed") == "Aktiv" for state in get_states(reg))


def is_substitute_allowed(association_type_uuid: UUID) -> bool:
    """
    checks whether the chosen association needs a substitute
    """
    settings = config.get_settings()
    substitute_roles = settings.confdb_substitute_roles
    if association_type_uuid in substitute_roles:
        # chosen role does need substitute
        return True
    return False


def get_query_args():
    return copy.deepcopy(context.get("query_args"))


def get_args_flag(name: str):
    """
    Get an argument from the Flask request as a boolean flag.

    A 'flag' argument is false either when not set or one of the
    values '0', 'false', 'no' or 'n'. Anything else is true.

    """
    query_args = context.get("query_args", {})
    v = query_args.get(name, "")

    if v.lower() in ("", "0", "no", "n", "false"):
        return False
    return bool(v)


def ensure_list(obj: T | list[T]) -> list[T]:
    """
    wraps obj in a list, unless it is already a list
    :param obj: Anything
    :return: List-wrapped obj
    """
    return obj if isinstance(obj, list) else [obj]


def query_to_search_phrase(query: str):
    # If query consists of only digits, spaces and separators, try to
    # treat it as purely numeric, to support whole and partial matches on
    # CPR numbers, etc.
    if re.match(r"^[\d|\s|\-]+$", query):
        # Strip non-digits from query
        query = re.sub(r"[^\d]", "", query)
    # Substring match
    return f"%{query}%"


def is_detail_unpublished(
    detail_value: str, detail_type_published_attr: str | None = None
):
    """Checks if a mo details have been un-published (IkkePubliceret)

    Starts by checking if the detail_attr "published", if set.
    Afterward, if not already un-published, it checks the required detail value as a fallback.

    OBS: We use a fallback, since the detail "itusers.itsystem" does not have a "published" concept.
    """
    if detail_type_published_attr and detail_type_published_attr == "IkkePubliceret":
        return True

    return detail_value == "-"
