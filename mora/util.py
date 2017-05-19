#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime

import pytz
import tzlocal


def parsedate(s, default=None):
    if default is not None and not s:
        return default

    try:
        dt = tzlocal.get_localzone().localize(
            datetime.datetime.strptime(s, '%d-%m-%Y')
        )
    except ValueError:
        dt = None

    if dt is None:
        try:
            dt = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S%z')
        except ValueError:
            pass

    if dt is None:
        try:
            # handle PG two-digit offsets
            dt = datetime.datetime.strptime(s + '00', '%Y-%m-%d %H:%M:%S%z')
        except ValueError:
            pass

    if dt is None:
        try:
            # ISO 8601
            dt = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S%z')
        except ValueError:
            pass

    if dt is None:
        raise ValueError('unparsable date {!r}'.format(s))

    return dt

def reparsedate(s):
    if s == 'infinity' or s == '-infinity':
        return s
    else:
        return parsedate(s).isoformat()

def now():
    return datetime.datetime.now(pytz.UTC)
