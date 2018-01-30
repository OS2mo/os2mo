#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import functools
import json
import os
import re
import sys
import typing
import uuid

import flask
import iso8601
import pytz
import dateutil.parser


# use this string rather than nothing or N/A in UI -- it's the em dash
PLACEHOLDER = "\u2014"

# timezone-aware versions of min/max
positive_infinity = pytz.FixedOffset(23 * 60).localize(
    datetime.datetime.max,
)
negative_infinity = pytz.FixedOffset(-23 * 60).localize(
    datetime.datetime.min,
)

default_timezone = dateutil.tz.gettz('Europe/Copenhagen')

tzinfos = {
    None: default_timezone,
    0: dateutil.tz.tzutc,
    1 * 60**2: default_timezone,
    2 * 60**2: default_timezone,
}


def unparsedate(d: datetime.date) -> str:
    return d.strftime('%d-%m-%Y')


def parsedatetime(s: str) -> datetime.datetime:
    if isinstance(s, datetime.date):
        dt = s

        if dt in (positive_infinity, negative_infinity):
            return dt

        if not isinstance(dt, datetime.datetime):
            dt = datetime.datetime.combine(
                dt, datetime.time(),
            )

        if not dt.tzinfo:
            dt = dt.replace(tzinfo=default_timezone)

        return dt

    elif s == 'infinity':
        return positive_infinity
    elif s == '-infinity':
        return negative_infinity

    if ' ' in s:
        # the frontend doesn't escape the 'plus' in ISO 8601 dates, so
        # we get it as a space
        s = re.sub(r' (?=\d\d:\d\d$)', '+', s)

    try:
        return iso8601.parse_date(s, default_timezone=default_timezone)
    except iso8601.ParseError:
        pass

    try:
        dt = dateutil.parser.parse(s, dayfirst=True, tzinfos=tzinfos)
    except ValueError:
        raise ValueError('cannot parse {!r}'.format(s))

    return dt


def to_lora_time(s):
    dt = parsedatetime(s)

    if dt == positive_infinity:
        return 'infinity'
    elif dt == negative_infinity:
        return '-infinity'
    else:
        return dt.isoformat()


def to_iso_time(s):
    dt = parsedatetime(s)

    return (
        dt.isoformat()
        if dt not in (positive_infinity, negative_infinity)
        else None
    )


def to_frontend_time(s):
    dt = parsedatetime(s)

    if dt == positive_infinity:
        return 'infinity'
    elif dt == negative_infinity:
        return '-infinity'
    elif dt and dt.time().replace(tzinfo=None) == datetime.time():
        return unparsedate(dt.date())
    else:
        return dt.isoformat()


def now() -> datetime.datetime:
    '''Get the current time, localized to the current time zone.'''
    return datetime.datetime.now().replace(tzinfo=default_timezone)


def today() -> datetime.datetime:
    '''Get midnight of current date, localized to the current time zone.'''
    return datetime.datetime.combine(datetime.date.today(),
                                     datetime.time(tzinfo=default_timezone))


def restrictargs(*allowed: str, required: typing.Iterable[str]=[]):
    '''Function decorator for checking and verifying Flask request arguments

    If any argument other than those listed is set and has a value,
    the function logs an error and return HTTP 501.

    '''
    allowed = {v.lower() for v in allowed}
    required = {v.lower() for v in required}
    allallowed = allowed | required

    def wrap(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if flask.g.get('are_args_valid'):
                return f(*args, **kwargs)

            invalidargs = {
                k for k, v in flask.request.args.items()
                if v and k.lower() not in allallowed
            }
            missing = {
                k for k in required
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
                    ', '.join(sorted(required)),
                    ', '.join(sorted(allowed)),
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
        raise ValueError('size must be positive!')

    i = 0
    nxs = len(xs)

    while i < nxs:
        yield xs[i:i + size]
        i += size


def is_uuid(v):
    try:
        uuid.UUID(v)
        return True
    except Exception:
        return False


# TODO: more thorough checking?
_cpr_re = re.compile(r'\d{10}')


def is_cpr_number(v):
    return isinstance(v, str) and _cpr_re.fullmatch(v)
