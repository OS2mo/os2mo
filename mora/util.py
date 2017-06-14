#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import functools

import flask
import pytz
import tzlocal


DATE_PARSERS = (
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


def parsedate(s, default=None):
    if default is not None and not s:
        return default

    for parser in DATE_PARSERS:
        try:
            return parser(s)
        except ValueError:
            pass

    raise ValueError('unparsable date {!r}'.format(s))


def reparsedate(s):
    if s == 'infinity' or s == '-infinity':
        return s
    elif not s:
        # In the case that the end-date is not specified in the frontend
        return 'infinity'
    else:
        return parsedate(s).isoformat()


def now():
    return datetime.datetime.now(pytz.UTC)


def restrictargs(*values):
    argset = frozenset(values)

    def wrap(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            invalidargs = {
                k for k, v in flask.request.args.items()
                if v and k not in argset
            }

            if invalidargs:
                msg = (
                    'Unsupported request arguments: {}\n'
                    'Allowed: {}\n'
                    'Given: {}'.format(
                        ', '.join(sorted(invalidargs)),
                        ', '.join(sorted(argset)),
                        ', '.join(sorted(flask.request.args)),
                    )

                flask.current_app.logger.error(msg)

                return msg, 501

            return f(*args, **kwargs)

        return wrapper

    return wrap
