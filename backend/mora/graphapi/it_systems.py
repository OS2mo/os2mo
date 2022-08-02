#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from ramodels.lora import ITSystem as LoraITSystem

from mora.common import get_connector
from mora.graphapi.schema import ITSystem


async def upsert_it_system(
    type_: str,
    name: str,
    user_key: str = None,
    uuid: Optional[UUID] = None,
) -> ITSystem:

    if not user_key:
        user_key = str(uuid)

    lora_class = LoraITSystem.from_simplified_fields(
        state="Aktiv",
        type=type_,
        user_key=user_key,
        name=name,
        uuid=uuid,
    )
    jsonified = jsonable_encoder(
        obj=lora_class, by_alias=True, exclude={"uuid"}, exclude_none=True
    )

    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    uuid = await c.itsystem.create(jsonified, uuid)

    return ITSystem(
        type_=type_,
        name=name,
        user_key=user_key,
        uuid=uuid,
    )
