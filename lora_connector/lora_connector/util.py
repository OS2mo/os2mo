# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import datetime
import re

import dateutil.parser
import dateutil.tz

_sentinel = object()

# timezone-aware versions of min/max
POSITIVE_INFINITY = datetime.datetime.max.replace(tzinfo=datetime.timezone.utc)
NEGATIVE_INFINITY = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
MINIMAL_INTERVAL = datetime.timedelta(microseconds=1)
ONE_DAY = datetime.timedelta(days=1)

# TODO: the default timezone should be configurable, shouldn't it?
DEFAULT_TIMEZONE = dateutil.tz.gettz('Europe/Copenhagen')

_tzinfos = {
    None: DEFAULT_TIMEZONE,
    0: dateutil.tz.tzutc,
    1 * 60 ** 2: DEFAULT_TIMEZONE,
    2 * 60 ** 2: DEFAULT_TIMEZONE,
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
            exceptions.ErrorCodes.E_INVALID_INPUT(
                'cannot parse {!r}'.format(s)
            )

    if dt.date() == POSITIVE_INFINITY.date():
        return POSITIVE_INFINITY

    dt = dt.astimezone(DEFAULT_TIMEZONE)

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


def now() -> datetime.datetime:
    '''Get the current time, localized to the current time zone.'''
    return datetime.datetime.now().replace(tzinfo=DEFAULT_TIMEZONE)
