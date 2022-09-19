# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
import string

from pydantic import ConstrainedStr


class SafeString(ConstrainedStr):
    """Custom string type, which will fail if using invalid on invalid characters."""

    # Strings which only allow:
    # Words:            '\w' = [a-zA-Z0-9_]
    # Whitespace chars: '\s' = [ \t\n\r\f\v]
    # ref: https://docs.python.org/3/library/re.html
    # regex = re.compile(r"^[\w\s]*$")
    regex = re.compile(r"^[{0}\n]*$".format(string.printable))


class CprNo(ConstrainedStr):
    regex = re.compile(r"^\d{10}$")
