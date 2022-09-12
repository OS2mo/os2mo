#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder

from .models import FacetCreate
from .types import FacetType
from mora.common import get_connector
from ramodels.lora.facet import Facet as LoraFacet

# --------------------------------------------------------------------------------------
# Helper functions for Facet mutators
# --------------------------------------------------------------------------------------


async def create_facet(input: FacetCreate) -> FacetType:

    input_dict = input.dict(by_alias=True)

    lora_facet = LoraFacet.from_simplified_fields(
        user_key=input_dict["user_key"],
        organisation_uuid=input_dict["org_uuid"],
        uuid=input_dict["uuid"],
    )

    jsonified = jsonable_encoder(
        obj=lora_facet, by_alias=True, exclude={"uuid"}, exclude_none=True
    )

    c = get_connector(virkningfra="-infinity", virkningtil="infinity")
    uuid = await c.facet.create(jsonified, input_dict["uuid"])

    return FacetType(uuid=str(uuid))
