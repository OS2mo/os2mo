# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import string

import pandas as pd
from jinja2 import Environment
from jinja2 import Undefined


def filter_parse_datetime(datestring):
    if not datestring or datestring.lower() == "none":
        return None
    try:
        return pd.to_datetime(datestring, dayfirst=False)
    except pd.errors.OutOfBoundsDatetime:
        year = int(datestring.split("-")[0])
        if year > 2000:
            return pd.Timestamp.max
        else:
            return pd.Timestamp.min


def filter_mo_datestring(datetime_object):
    """
    Converts a datetime object to a date string which is accepted by MO.

    Notes
    -------
    MO only accepts date objects dated at midnight.
    """
    if not datetime_object:
        return None
    return datetime_object.strftime("%Y-%m-%dT00:00:00")


def filter_strip_non_digits(input_string):
    if type(input_string) is not str:
        return None
    return "".join(c for c in input_string if c in string.digits)


def filter_splitfirst(text, separator=" "):
    """
    Splits a string at the first space, returning two elements
    This is convenient for splitting a name into a givenName and a surname
    and works for names with no spaces (surname will then be empty)
    """
    if text is not None:
        text = str(text)
        if text != "":
            s = text.split(separator, 1)
            return s if len(s) > 1 else (s + [""])
    return ["", ""]


def filter_splitlast(text, separator=" "):
    """
    Splits a string at the last space, returning two elements
    This is convenient for splitting a name into a givenName and a surname
    and works for names with no spaces (givenname will then be empty)
    """
    if text is not None:
        text = str(text)
        if text != "":
            text = str(text)
            s = text.split(separator)
            return [separator.join(s[:-1]), s[-1]]
    return ["", ""]


def filter_remove_curly_brackets(text: str) -> str:
    return text.replace("{", "").replace("}", "")


environment = Environment(undefined=Undefined, enable_async=True)
environment.filters["splitfirst"] = filter_splitfirst
environment.filters["splitlast"] = filter_splitlast
environment.filters["mo_datestring"] = filter_mo_datestring
environment.filters["parse_datetime"] = filter_parse_datetime
environment.filters["strip_non_digits"] = filter_strip_non_digits
environment.filters["remove_curly_brackets"] = filter_remove_curly_brackets
