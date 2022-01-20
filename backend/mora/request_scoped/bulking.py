# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from contextlib import asynccontextmanager
from typing import Any
from typing import Dict
from typing import Optional

from more_itertools import one

from mora.common import get_connector
from mora.lora import Connector
from mora.lora import LoraObjectType
from mora.lora import filter_registrations

LORA_OBJ = Dict[Any, Any]
UUID = str


class __BulkBookkeeper:
    """
    Thin request wide bulking implementation based on lora.py dataloader.
    """

    @property
    def connector(self) -> Connector:
        return get_connector()

    async def get_lora_object(self, type_: LoraObjectType, uuid: str) -> Optional[LORA_OBJ]:
        results = await self.connector.scope(type_).load(uuid=uuid)
        if not results:
            return None
        uuid, registration = one(filter_registrations(results, wantregs=False))
        return registration

    @asynccontextmanager
    async def cache_context(self):
        yield None


request_wide_bulk = __BulkBookkeeper()
