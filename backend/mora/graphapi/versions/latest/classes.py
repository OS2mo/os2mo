#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder

from .types import ClassCreateType
from mora.common import get_connector
from mora.graphapi.versions.latest.models import ClassCreate
from ramodels.lora import Klasse

# --------------------------------------------------------------------------------------
# Supporting functions for Graphapi mo-classes
# --------------------------------------------------------------------------------------


async def upsert_class(input: ClassCreate) -> ClassCreateType:

    input_dict = input.dict(by_alias=True)

    lora_class = Klasse.from_simplified_fields(
        facet_uuid=input_dict["facet_uuid"],
        user_key=input_dict["user_key"],
        organisation_uuid=input_dict["org_uuid"],
        title=input_dict["name"],
        uuid=input_dict["uuid"],
        scope=input_dict["scope"],
    )

    jsonified = jsonable_encoder(
        obj=lora_class, by_alias=True, exclude={"uuid"}, exclude_none=True
    )

    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    uuid = await c.klasse.create(jsonified, input_dict["uuid"])

    return ClassCreateType(uuid=str(uuid))
