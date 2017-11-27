#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import functools
import json
import typing
import uuid

import flask
import iso8601
import pytz
import tzlocal


# use this string rather than nothing or N/A in UI -- it's the em dash
PLACEHOLDER = "\u2014"

# timezone-aware versions of min/max
positive_infinity = datetime.datetime.max.replace(
    tzinfo=datetime.timezone(datetime.timedelta(hours=23)),
)
negative_infinity = datetime.datetime.min.replace(
    tzinfo=datetime.timezone(datetime.timedelta(hours=-23)),
)

DATETIME_PARSERS = (
    # limits
    lambda s: {
        'infinity': positive_infinity,
        '-infinity': negative_infinity,
    }[s],
    # ISO 8601
    iso8601.parse_date,
    lambda s: iso8601.parse_date(s.replace(' ', '+')),
    # DD/MM/YYYY w/o time -- sent by the frontend
    lambda s: tzlocal.get_localzone().localize(
        datetime.datetime.strptime(s, '%d-%m-%Y')
    ),
    lambda s: tzlocal.get_localzone().localize(
        datetime.datetime.strptime(s, '%Y-%m-%d')
    ),
    lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S%z'),
    # handle PG two-digit offsets
    lambda s: datetime.datetime.strptime(s + '00', '%Y-%m-%d %H:%M:%S%z'),
)


def unparsedate(d: datetime.date) -> str:
    return d.strftime('%d-%m-%Y')


def parsedatetime(s: str,
                  default: datetime.datetime=None) -> datetime.datetime:
    if default is not None and not s:
        return default
    elif isinstance(s, datetime.date):
        if s in (positive_infinity, negative_infinity):
            return s
        else:
            return tzlocal.get_localzone().localize(
                datetime.datetime.combine(s, datetime.time())
            )
    elif isinstance(s, datetime.datetime):
        return s

    for parser in DATETIME_PARSERS:
        try:
            return parser(s)
        except (ValueError, KeyError, iso8601.ParseError):
            pass

    raise ValueError('unparsable date {!r}'.format(s))


def to_lora_time(s):
    dt = parsedatetime(s)

    if dt == positive_infinity:
        return 'infinity'
    elif dt == negative_infinity:
        return '-infinity'
    else:
        return dt.isoformat()


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
    return datetime.datetime.now(tzlocal.get_localzone())


def today() -> datetime.datetime:
    '''Get midnight of current date, localized to the current time zone.'''
    dt = now()
    t = datetime.time(tzinfo=dt.tzinfo)
    return datetime.datetime.combine(dt.date(), t)


def fromtimestamp(t: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(int(t) / 1000, pytz.UTC)


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
            invalidargs = {
                k for k, v in flask.request.args.items()
                if v and k.lower() not in allallowed
            }
            missing = {
                k for k in required
                if not flask.request.args.get(k, None)
            }

            if missing or invalidargs:
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


def update_config(mapping, config_path):
    '''load the JSON configuration at the given path

    We disregard all entries in the configuration that lack a default
    within the mapping.

    '''
    try:
        with open(config_path) as fp:
            overrides = json.load(fp)
    except IOError:
        return

    for key in mapping.keys() & overrides.keys():
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
