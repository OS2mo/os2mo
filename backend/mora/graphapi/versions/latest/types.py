# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from base64 import b64decode
from base64 import b64encode
from typing import NewType
from uuid import UUID

import strawberry

from mora.util import CPR

# https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
CPRType = strawberry.scalar(
    CPR,
    serialize=str,
    parse_value=CPR.validate,
)

Cursor = strawberry.scalar(
    NewType("Cursor", str),
    serialize=lambda v: b64encode(json.dumps(v).encode("ascii")).decode("ascii"),
    parse_value=lambda v: int(b64decode(v)),
)


@strawberry.type
class UUIDReturn:
    uuid: UUID
