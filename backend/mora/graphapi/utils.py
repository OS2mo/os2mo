# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re

from pydantic import ConstrainedStr
import string


class PrintableStr(ConstrainedStr):
    """Custom printable string type.

    Define custom type for string to make it
    strict "printable chars" only and min length of 1
    Used in Pydantic models.
    """

    regex = re.compile(r"^[{0}\n]+$".format(string.printable))


class CprNo(ConstrainedStr):
    regex = re.compile(r"^\d{10}$")


