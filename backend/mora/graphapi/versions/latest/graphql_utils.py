# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
import string

from pydantic import ConstrainedStr


class PrintableStr(ConstrainedStr):
    """Custom restricted string type."""

    """
    Define custom type for string to make it
    strict "printable chars" only and min length of 1
    Used in Pydantic models.
    """

    regex = re.compile(rf"^[{string.printable}\n]+$")
