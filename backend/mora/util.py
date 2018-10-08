#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Utility methods
---------------

This module contains various utility methods, i.e. a collection of
various small functions used in many places.

'''


import collections
import copy
import datetime
import functools
import io
import operator

import itertools
import json
import marshal
import os
import re
import sys
import tempfile
import typing
import urllib.parse
import uuid

import flask
import dateutil.parser
import dateutil.tz

from . import exceptions
from . import mapping


# use this string rather than nothing or N/A in UI -- it's the em dash
PLACEHOLDER = "\u2014"

_sentinel = object()

# timezone-aware versions of min/max
POSITIVE_INFINITY = datetime.datetime.max.replace(
    tzinfo=dateutil.tz.tzoffset(
        'MAX',
        datetime.timedelta(hours=23, minutes=59),
    ),
)
NEGATIVE_INFINITY = datetime.datetime.min.replace(
    tzinfo=dateutil.tz.tzoffset(
        'MIN',
        -datetime.timedelta(hours=23, minutes=59),
    ),
)
MINIMAL_INTERVAL = datetime.timedelta(microseconds=1)
ONE_DAY = datetime.timedelta(days=1)

# TODO: the default timezone should be configurable, shouldn't it?
DEFAULT_TIMEZONE = dateutil.tz.gettz('Europe/Copenhagen')

_tzinfos = {
    None: DEFAULT_TIMEZONE,
    0: dateutil.tz.tzutc,
    1 * 60**2: DEFAULT_TIMEZONE,
    2 * 60**2: DEFAULT_TIMEZONE,
}


def parsedatetime(s: str, default=_sentinel) -> datetime.datetime:
    if isinstance(s, datetime.date):
        dt = s

        if dt in (POSITIVE_INFINITY, NEGATIVE_INFINITY):
            return dt

        if not isinstance(dt, datetime.datetime):
            dt = datetime.datetime.combine(
                dt, datetime.time(),
            )

        if not dt.tzinfo:
            dt = dt.replace(tzinfo=DEFAULT_TIMEZONE)

        return dt

    elif s == 'infinity':
        return POSITIVE_INFINITY
    elif s == '-infinity':
        return NEGATIVE_INFINITY

    if ' ' in s:
        # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
        # we get it as a space
        s = re.sub(r' (?=\d\d:\d\d$)', '+', s)

    try:
        return from_iso_time(s)
    except ValueError:
        pass

    try:
        dt = dateutil.parser.parse(s, dayfirst=True, tzinfos=_tzinfos)
    except ValueError:
        if default is not _sentinel:
            return default
        else:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_INVALID_INPUT,
                'cannot parse {!r}'.format(s)
            )

    if dt.date() == POSITIVE_INFINITY.date():
        return POSITIVE_INFINITY

    return dt


def do_ranges_overlap(first_start, first_end, second_start, second_end):
    return max(first_start, second_start) < min(first_end, second_end)


def to_lora_time(s):
    dt = parsedatetime(s)

    if dt == POSITIVE_INFINITY:
        return 'infinity'
    elif dt == NEGATIVE_INFINITY:
        return '-infinity'
    else:
        return dt.isoformat()


def to_iso_time(s):
    '''Return an ISO 8601 string representing the time and date given by `s`.

    We always localise this to our ‘default’ timezone, since LoRA
    might be running under something silly such as UTC.

    '''
    dt = parsedatetime(s)

    return (
        dt.astimezone(DEFAULT_TIMEZONE).isoformat()
        if dt not in (POSITIVE_INFINITY, NEGATIVE_INFINITY)
        else None
    )


def to_iso_date(s, is_end: bool=False):
    '''Return an ISO 8601 string representing date given by `s`.

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

    '''
    dt = parsedatetime(s)

    if is_end and dt == POSITIVE_INFINITY:
        return None
    elif not is_end and dt == NEGATIVE_INFINITY:
        return None

    if dt.time() != datetime.time.min:
        dt = datetime.datetime.combine(dt, datetime.time.min)

    if is_end:
        dt -= ONE_DAY

    return dt.date().isoformat()


def from_iso_time(s):
    dt = dateutil.parser.isoparse(s)

    if not dt.tzinfo:
        dt = dt.replace(tzinfo=DEFAULT_TIMEZONE)
    else:
        dt = dt.astimezone(DEFAULT_TIMEZONE)

    return dt


def now() -> datetime.datetime:
    '''Get the current time, localized to the current time zone.'''
    return datetime.datetime.now().replace(tzinfo=DEFAULT_TIMEZONE)


def restrictargs(*allowed: str, required: typing.Iterable[str]=[]):
    '''Function decorator for checking and verifying Flask request arguments

    If any argument other than those listed is set and has a value,
    the function logs an error and return HTTP 501.

    '''
    allowed_values = {v.lower() for v in allowed}
    required_values = {v.lower() for v in required}
    all_allowed_values = allowed_values | required_values

    def wrap(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if flask.g.get('are_args_valid'):
                return f(*args, **kwargs)

            invalidargs = {
                k for k, v in flask.request.args.items()
                if v and k.lower() not in all_allowed_values
            }
            missing = {
                k for k in required_values
                if not flask.request.args.get(k, None)
            }

            flask.g.are_args_valid = not (missing or invalidargs)

            if not flask.g.are_args_valid:
                msg = '\n'.join((
                    'Unsupported request arguments:',
                    'URL: {}',
                    'Required: {}',
                    'Allowed: {}',
                    'Given: {}',
                    'Missing: {}',
                    'Unsupported: {}'
                )).format(
                    flask.request.url,
                    ', '.join(sorted(required_values)),
                    ', '.join(sorted(allowed_values)),
                    ', '.join(sorted(flask.request.args)),
                    ', '.join(sorted(missing)),
                    ', '.join(sorted(invalidargs)),
                )

                flask.current_app.logger.error(msg)

                return msg, 501

            return f(*args, **kwargs)

        return wrapper

    return wrap


def update_config(mapping, config_path, allow_environment=True):
    '''load the JSON configuration at the given path

    We disregard all entries in the configuration that lack a default
    within the mapping.

    '''

    keys = {
        k
        for k, v in mapping.items()
        if not k.startswith('_')
    }

    try:
        with open(config_path) as fp:
            overrides = json.load(fp)

        for key in keys & overrides.keys():
            mapping[key] = overrides[key]

    except IOError:
        pass

    if allow_environment:
        overrides = {
            k[5:]: v
            for k, v in os.environ.items()
            if k.startswith('MORA_')
        }

        for key in keys & overrides.keys():
            print(' * Using override MORA_{}={!r}'.format(key, overrides[key]),
                  file=sys.stderr)
            mapping[key] = overrides[key]


def splitlist(xs, size):
    if size <= 0:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_SIZE_MUST_BE_POSITIVE)

    i = 0
    nxs = len(xs)

    while i < nxs:
        yield xs[i:i + size]
        i += size


def is_urn(v):
    return v and isinstance(v, str) and v.startswith('urn:')


def is_uuid(v):
    try:
        uuid.UUID(v)
        return True
    except Exception:
        return False


def is_cpr_number(v):
    try:
        return v and bool(get_cpr_birthdate(v))
    except ValueError:
        return False


def uniqueify(xs):
    '''return the contents of xs as a list, but stable'''
    # TODO: is this fast?
    return list(collections.OrderedDict(itertools.zip_longest(xs, ())).keys())


def log_exception(msg=''):
    data = flask.request.get_json()

    if data:
        if 'password' in data:
            data['password'] = 'X' * 8

        data_str = '\n' + json.dumps(data, indent=2)

    else:
        data_str = ''

    flask.current_app.logger.exception(
        'AN ERROR OCCURRED in {!r}: {}\n{}'.format(
            flask.request.url,
            msg,
            data_str,
        )
    )


def get_cpr_birthdate(number: typing.Union[int, str]) -> datetime.datetime:
    if isinstance(number, str):
        number = int(number)

    rest, code = divmod(number, 10000)
    rest, year = divmod(rest, 100)
    rest, month = divmod(rest, 100)
    rest, day = divmod(rest, 100)

    if rest:
        raise ValueError('invalid CPR number {}'.format(number))

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
        return datetime.datetime(century + year, month, day,
                                 tzinfo=DEFAULT_TIMEZONE)
    except ValueError:
        raise ValueError('invalid CPR number {}'.format(number))


def cached(func):
    @functools.wraps(func)
    def wrapper(*args):
        try:
            return wrapper.cache[args]
        except KeyError:
            wrapper.cache[args] = result = func(*args)

            with open(wrapper.cache_file, 'wb') as fp:
                marshal.dump(wrapper.cache, fp, marshal.version)

            return result

    wrapper.cache = {}
    wrapper.uncached = wrapper.__wrapped__

    wrapper.cache_file = os.path.join(
        tempfile.gettempdir(),
        '-'.join(
            func.__module__.split('.') +
            [
                func.__name__,
                str(os.getuid()),
            ],
        ) + '.data',
    )

    try:
        with open(wrapper.cache_file, 'rb') as fp:
            wrapper.cache = marshal.load(fp)
    except (IOError, EOFError):
        wrapper.cache = {}

    return wrapper


URN_SAFE = frozenset(b'abcdefghijklmnopqrstuvwxyz'
                     b'0123456789'
                     b'+')


def urnquote(s):
    '''Quote the given string so that it may safely pass through
    case-insensitive URN handling.

    Strictly speaking, the resulting string is not valid for a URN, as
    they may not contain anything other than colon, letters and
    digits. We add '+' and '%' to the mix so that we can roundtrip
    arbitrary text. Meh.

    '''

    with io.StringIO('w') as buf:
        for character in s.encode('utf-8'):
            if character in URN_SAFE:
                buf.write(chr(character))
            else:
                buf.write('%{:02x}'.format(character))

        return buf.getvalue()


# provide an alias for consistency
urnunquote = urllib.parse.unquote
K = typing.TypeVar('K', bound=typing.Hashable)
V = typing.TypeVar('V')
D = typing.Dict[K, V]


def checked_get(
    mapping: D,
    key: K,
    default: V,
    fallback: D=None,
    required: bool=False,
) -> V:
    try:
        v = mapping[key]
    except (LookupError, TypeError):
        exc = exceptions.HTTPException(
            exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE,
            message='Missing {}'.format(key),
            key=key,
            obj=mapping,
        )

        if fallback is not None:
            try:
                return checked_get(fallback, key, default, None, required)
            except exceptions.HTTPException:
                # ensure that we raise an exception describing the
                # current object, even if a fallback was specified
                raise exc

        elif required:
            raise exc
        else:
            return default

    if not isinstance(v, type(default)):
        if not required and v is None:
            return default

        expected = type(default).__name__
        actual = v
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_INVALID_TYPE,
            message='Invalid {!r}, expected {}, got: {}'.format(
                key, expected, json.dumps(actual),
            ),
            key=key,
            expected=expected,
            actual=actual,
            obj=mapping,
        )

    return v


def get_uuid(
    mapping: D,
    fallback: D=None,
    *,
    required: bool=True,
    key: typing.Hashable=mapping.UUID
) -> typing.Optional[str]:
    v = checked_get(mapping, key, '', fallback=fallback, required=required)

    if not v and not required:
        return None
    elif not is_uuid(v):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_INVALID_UUID,
            message='Invalid uuid for {!r}: {!r}'.format(key, v),
            obj=mapping
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
    else:
        return None


def get_urn(
    mapping: D,
    fallback: D=None,
    *,
    key: typing.Hashable=mapping.URN
) -> str:
    v = checked_get(mapping, key, '', fallback=fallback, required=True)

    if not is_urn(v):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_INVALID_URN,
            message='invalid urn for {!r}: {!r}'.format(key, v),
            obj=mapping
        )

    return v


def set_obj_value(obj: dict, path: tuple, val: typing.List[dict]):
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


T = typing.TypeVar('T')


def get_obj_value(obj,
                  path: typing.Tuple[str, str],
                  filter_fn: typing.Callable[[dict], bool] = None,
                  default: T=None) -> typing.Optional[T]:
    try:
        props = functools.reduce(operator.getitem, path, obj)
    except (LookupError, TypeError):
        return default

    if filter_fn:
        return list(filter(filter_fn, props))
    else:
        return props


def get_obj_uuid(obj, path: tuple):
    (obj,) = get_obj_value(obj, path, default={})
    return get_uuid(obj)


def get_effect_from(effect: dict) -> datetime.datetime:
    return parsedatetime(effect['virkning']['from'])


def get_effect_to(effect: dict) -> datetime.datetime:
    return parsedatetime(effect['virkning']['to'])


def get_effect_validity(effect):
    return {
        mapping.FROM: to_iso_date(get_effect_from(effect)),
        mapping.TO: to_iso_date(get_effect_to(effect), is_end=True),
    }


def get_valid_from(obj, fallback=None) -> datetime.datetime:
    '''Extract the start of the validity interval in ``obj``, or otherwise
    ``fallback``, and return it as a timestamp delimiting the
    corresponding interval.

    :raises mora.exceptions.HTTPException: if the given timestamp does
      not correspond to midnight in Central Europe.
    :raises mora.exceptions.HTTPException: if neither ``obj`` nor ``fallback``
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

    '''
    sentinel = object()
    validity = obj.get(mapping.VALIDITY, sentinel)

    if validity and validity is not sentinel:
        valid_from = validity.get(mapping.FROM, sentinel)
        if valid_from is None:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.V_MISSING_START_DATE,
                obj=obj
            )
        elif valid_from is not sentinel:
            dt = from_iso_time(valid_from)

            if dt.time() != datetime.time.min:
                raise exceptions.HTTPException(
                    exceptions.ErrorCodes.E_INVALID_INPUT,
                    '{!r} is not at midnight!'.format(dt.isoformat()),
                )

            return dt

    if fallback is not None:
        return get_valid_from(fallback)
    else:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_MISSING_START_DATE,
            obj=obj
        )


def get_valid_to(obj, fallback=None) -> datetime.datetime:
    '''Extract the end of the validity interval in ``obj``, or otherwise
    ``fallback``, and return it as a timestamp delimiting the
    corresponding interval. If neither specifies an end, assume a
    timestamp far in the future — practically infinite, in fact.

    Please note that as end intervals are *inclusive*, a date ends at
    24:00, or 0:00 the following day.

    :see also: :py:func:`to_iso_date`

    :raises mora.exceptions.HTTPException: if the given timestamp does
      not correspond to midnight in Central Europe.
    :raises mora.exceptions.HTTPException: if neither ``obj`` nor ``fallback``
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

    '''
    sentinel = object()
    validity = obj.get(mapping.VALIDITY, sentinel)

    if validity and validity is not sentinel:
        valid_to = validity.get(mapping.TO, sentinel)

        if valid_to is None:
            return POSITIVE_INFINITY

        elif valid_to is not sentinel:
            dt = from_iso_time(valid_to)

            if dt.time() != datetime.time.min:
                raise exceptions.HTTPException(
                    exceptions.ErrorCodes.E_INVALID_INPUT,
                    '{!r} is not at midnight!'.format(dt.isoformat()),
                )

            # this is the reverse of to_iso_date, and an end date
            # _includes_ the day in question, so the end of the
            # interval corresponds to 24:00 on that day
            return dt + ONE_DAY

    if fallback is not None:
        return get_valid_to(fallback)
    else:
        return POSITIVE_INFINITY


def get_validities(obj, fallback=None):
    valid_from = get_valid_from(obj, fallback)
    valid_to = get_valid_to(obj, fallback)
    if valid_to < valid_from:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_END_BEFORE_START,
            obj=obj
        )
    return valid_from, valid_to


def get_validity_effect(entry, fallback=None):
    if mapping.VALIDITY not in entry and fallback is None:
        return None

    valid_from, valid_to = get_validities(entry, fallback)

    return {
        mapping.FROM: to_lora_time(valid_from),
        mapping.TO: to_lora_time(valid_to),
    }


def get_states(reg):
    for tilstand in reg.get('tilstande', {}).values():
        yield from tilstand


def is_reg_valid(reg):
    """
    Check if a given registration is valid
    i.e. that the registration contains a 'gyldighed' that is 'Aktiv'

    :param reg: A registration object
    """

    return any(
        state.get('gyldighed') == 'Aktiv'
        for state in get_states(reg)
    )


def get_args_flag(name: str):
    '''Get an argument from the Flask request as a boolean flag.

    A 'flag' argument is false either when not set or one of the
    values '0', 'false' and 'False'. Anything else is true.

    '''

    v = flask.request.args.get(name, False)

    if v in ('0', 'false', 'False'):
        return False
    else:
        return bool(v)
