# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
import string
from datetime import datetime
from typing import Any
from typing import NamedTuple
from typing import TypeAlias
from uuid import UUID

from pydantic import ConstrainedStr
from strawberry.types.unset import UnsetType

from mora.db import Collection


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


# OIDC token role
Role: TypeAlias = str
# GraphQL field
Field: TypeAlias = str


class AccessKey(NamedTuple):
    """A field access request."""

    collection: Collection
    uuid: UUID
    field: Field


class WriteKey(NamedTuple):
    """A mutator access request."""

    mutator: str
    args: dict[str, Any]


class LoadKey(NamedTuple):
    uuid: UUID
    start: datetime | UnsetType | None
    end: datetime | UnsetType | None
    registration_time: datetime | None
