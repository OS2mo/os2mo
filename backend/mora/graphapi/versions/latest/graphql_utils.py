# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import random
import re
import string
from datetime import datetime
from typing import NamedTuple
from uuid import UUID

from pydantic import ConstrainedStr
from strawberry.types.unset import UnsetType
from tests.conftest import GraphAPIPost

sys_random = random.SystemRandom()


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


async def get_uuids(obj: str, graphapi_post: GraphAPIPost) -> UUID:
    """Queries for uuids for a given object type. Eg. Employees."""
    # TODO: move this out of the production code and into the tests
    if obj == "org":
        query = "".join(["query FetchUUIDs {", obj, "{uuid}}"])
    else:
        query = "".join(["query FetchUUIDs {", obj, "{objects {uuid}}}"])

    response = graphapi_post(query=query)
    assert response.errors is None
    if obj == "org":
        uuids = response.data.get(obj, {}) if response.data else {}
    else:
        uuids = response.data.get(obj, {})["objects"] if response.data else {}
    if isinstance(uuids, dict):
        return UUID(uuids.get("uuid", {}))
    return UUID(sys_random.choice(uuids).get("uuid"))
