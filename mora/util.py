#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import datetime
import functools
import itertools
import json
import marshal
import os
import re
import sys
import tempfile
import typing
import uuid

import flask
import dateutil.parser
import dateutil.tz

from . import exceptions


# use this string rather than nothing or N/A in UI -- it's the em dash
PLACEHOLDER = "\u2014"

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


# TODO: the default timezone should be configurable, shouldn't it?
DEFAULT_TIMEZONE = dateutil.tz.gettz('Europe/Copenhagen')

tzinfos = {
    None: DEFAULT_TIMEZONE,
    0: dateutil.tz.tzutc,
    1 * 60**2: DEFAULT_TIMEZONE,
    2 * 60**2: DEFAULT_TIMEZONE,
}


def unparsedate(d: datetime.date) -> str:
    return d.strftime('%d-%m-%Y')


def parsedatetime(s: str) -> datetime.datetime:
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
        dt = dateutil.parser.parse(s, dayfirst=True, tzinfos=tzinfos)
    except ValueError:
        raise exceptions.HTTPException('cannot parse {!r}'.format(s))

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


def from_iso_time(s):
    dt = dateutil.parser.isoparse(s)

    if not dt.tzinfo:
        dt = dt.replace(tzinfo=DEFAULT_TIMEZONE)

    return dt


def to_frontend_time(s):
    dt = parsedatetime(s)

    if dt == POSITIVE_INFINITY:
        return 'infinity'
    elif dt == NEGATIVE_INFINITY:
        return '-infinity'
    elif dt and dt.time().replace(tzinfo=None) == datetime.time():
        return unparsedate(dt.date())
    else:
        return dt.isoformat()


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
