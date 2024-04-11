# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import string

from jinja2 import Environment  # noqa: E402
from jinja2 import Undefined  # noqa: E402


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
    if not isinstance(input_string, str):
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
    # TODO: Should this remove everything or just a single set?
    return text.replace("{", "").replace("}", "")


def bitwise_and(input: int, bitmask: int) -> int:
    """Bitwise and jinja filter.

    Mostly useful for accessing bits within userAccountControl.

    Args:
        input: The input integer.
        bitmask: The bitmask to filter the input through.

    Returns:
        The bitwise and on input and bitmask.
    """
    return input & bitmask


environment = Environment(undefined=Undefined, enable_async=True)
environment.filters["bitwise_and"] = bitwise_and
environment.filters["splitfirst"] = filter_splitfirst
environment.filters["splitlast"] = filter_splitlast
environment.filters["mo_datestring"] = filter_mo_datestring
environment.filters["strip_non_digits"] = filter_strip_non_digits
environment.filters["remove_curly_brackets"] = filter_remove_curly_brackets
