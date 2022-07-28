#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from asyncio import gather
from typing import Optional
from uuid import UUID

import httpx
from fastapi import Path
from fastapi import Query
from pydantic import BaseModel
from pydantic import Field

from mora import config
from mora import exceptions
from mora.graphapi.shim import execute_graphql
from mora.service.address import router as address_router

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------

client = httpx.AsyncClient(
    headers={
        "User-Agent": "MORA/0.1",
    }
)


class AddressAutoCompleteEntry(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "name": "Skt. Johannes Allé 2, 8000 Aarhus C",
                "uuid": "0a3f5096-e43f-32b8-e044-0003ba298018",
            }
        }

    name: str = Field(description="A human readable name for the address.")
    uuid: str = Field(description="A UUID of a DAR address .")


class AddressAutoCompleteReturn(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "location": {
                    "name": "Skt. Johannes Allé 2, 8000 Aarhus C",
                    "uuid": "0a3f5096-e43f-32b8-e044-0003ba298018",
                }
            }
        }

    location: AddressAutoCompleteEntry = Field(
        description="Container for address matches"
    )


@address_router.get(
    "/o/{orgid}/address_autocomplete/",
    response_model=list[AddressAutoCompleteReturn],
    response_model_exclude_unset=True,
    responses={"400": {"description": "Invalid input"}},
)
async def address_autocomplete(
    orgid: UUID = Path(
        ...,
        description="UUID of the organisation, used for filtering addresses.",
        example="3b866d97-0b1f-48e0-8078-686d96f430b3",
    ),
    q: str = Query(..., description="A query string to be used for lookup"),
    global_lookup: Optional[bool] = Query(
        False,
        alias="global",
        description=(
            "Whether or not the lookup should be in the entire country,"
            "or contained to the municipality of the organisation"
        ),
    ),
) -> list[dict[str, str]]:
    """Perform address autocomplete.

    Address resolution is run against both ``adgangsadresse`` and ``adresse``.
    """

    if not config.get_settings().enable_dar:
        return []

    code: Optional[int] = None
    if not global_lookup:
        query = "query OrganisationQuery { org { uuid, municipality_code } }"
        r = await execute_graphql(query)
        if r.errors:
            exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY()
        data = {r.data["org"]["uuid"]: r.data["org"]["municipality_code"]}

        if str(orgid) not in data:
            exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY()
        code = data[str(orgid)]
        if code is None:
            exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY()

    #
    # In order to allow reading both access & regular addresses, we
    # autocomplete both into an ordered dictionary, with the textual
    # representation as keys. Regular addresses tend to be less
    # relevant than access addresses, so we list them last.
    #
    # The limits are somewhat arbitrary: Since access addresses mostly
    # differ by street number or similar, we only show five -- by
    # comparison, ten addresses seems apt since they may refer to
    # apartments etc.
    #
    params = {
        "noformat": "1",
        "q": q,
    }
    if code is not None:
        params["kommunekode"] = code

    async def get_access_addreses() -> list[dict]:
        r = await client.get(
            "https://api.dataforsyningen.dk/adgangsadresser/autocomplete",
            params={**params, "per_side": 5},
        )
        return r.json()

    async def get_addresses() -> list[dict]:
        r = await client.get(
            "https://api.dataforsyningen.dk/adresser/autocomplete",
            params={**params, "per_side": 10},
        )
        return r.json()

    access_addrs, addrs = await gather(get_access_addreses(), get_addresses())

    result_addrs = {
        addr["tekst"]: addr["adgangsadresse"]["id"] for addr in access_addrs
    }
    for addr in addrs:
        result_addrs.setdefault(addr["tekst"], addr["adresse"]["id"])

    return [
        {
            "location": {
                "name": key,
                "uuid": value,
            },
        }
        for key, value in result_addrs.items()
    ]