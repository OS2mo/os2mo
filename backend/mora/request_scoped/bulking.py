# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from mora.common import get_connector
from mora.lora import Connector
from mora.lora import LoraObjectType
from mora.lora import filter_registrations
from more_itertools import one

LORA_OBJ = dict[Any, Any]
UUID = str


async def get_lora_object(
    type_: LoraObjectType, uuid: str, connector: Connector | None = None
) -> LORA_OBJ | None:
    connector = connector or get_connector()
    results = await connector.scope(type_).load(uuid=uuid)
    if not results:
        return None
    _, registration = one(filter_registrations(results, wantregs=False))
    return registration
