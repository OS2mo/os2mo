# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
import string
from datetime import datetime
from typing import NamedTuple
from uuid import UUID

from pydantic import ConstrainedStr
from strawberry.types.unset import UnsetType


class PrintableStr(ConstrainedStr):
    """Custom restricted string type."""

    """
    Define custom type for string to make it
    strict "printable chars" only and min length of 1
    Used in Pydantic models.
    """

    regex = re.compile(rf"^[{string.printable}\n]+$")


class CprNo(ConstrainedStr):
    """Danish CPR No. restricted string type.

    Only allow strings which contain 10 digits from beginning to end
    of the string.
    """

    regex = re.compile(r"^\d{10}$")


class LoadKey(NamedTuple):
    uuid: UUID
    start: datetime | UnsetType | None
    end: datetime | UnsetType | None
