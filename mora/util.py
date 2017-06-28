#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import functools
import typing

import flask
import pytz
import tzlocal

DATETIME_PARSERS = (
    # DD/MM/YY w/o time -- sent by the frontend
    lambda s: tzlocal.get_localzone().localize(
        datetime.datetime.strptime(s, '%d-%m-%Y')
    ),
    lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S%z'),
    # handle PG two-digit offsets
    lambda s: datetime.datetime.strptime(s + '00', '%Y-%m-%d %H:%M:%S%z'),
    # ISO 8601
    lambda s: datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S%z'),
)


def parsedate(s: str) -> datetime.date:
    if isinstance(s, datetime.date):
        return s
    else:
        return datetime.date.strptime(s, '%d-%m-%Y')


def unparsedate(d: datetime.date) -> str:
    return d.strftime('%d-%m-%Y')


def parsedatetime(s: str, default: str=None) -> datetime.datetime:
    if default is not None and not s:
        return default
    elif isinstance(s, datetime.datetime):
        return s

    for parser in DATETIME_PARSERS:
        try:
            return parser(s)
        except ValueError:
            pass

    raise ValueError('unparsable date {!r}'.format(s))


def reparsedatetime(s):
    if s == 'infinity' or s == '-infinity':
        return s
    elif not s:
        # In the case that the end-date is not specified in the frontend
        return 'infinity'
    else:
        return parsedatetime(s).isoformat()


def now() -> datetime.datetime:
    '''Get the current time, localized to the current time zone.'''
    return datetime.datetime.now(tzlocal.get_localzone())


def fromtimestamp(t: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(int(t) / 1000, pytz.UTC)


def restrictargs(*allowed: typing.List[str], required: typing.List[str]=[]):
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

            # HACK: suppress timestamps from today
            if 't' in invalidargs:
                # TODO: delete this when timestamps actually work...
                t = fromtimestamp(flask.request.args['t'])
                if t.date() == datetime.date.today():
                    invalidargs.remove('t')

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
