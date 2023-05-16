# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from uuid import UUID

import strawberry
from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field

from mora.util import to_lora_time
from oio_rest import db
from oio_rest import validate


class FacetCreate(BaseModel):
    """Model representing a facet creation."""

    user_key: str = Field(description="Facet name.")
    published: str = Field(
        "Publiceret", description="Published state of the facet object."
    )

    class Config:
        frozen = True
        extra = Extra.forbid

    def to_registration(self, organisation_uuid: UUID) -> dict:
        from_time = to_lora_time("-infinity")
        to_time = to_lora_time("infinity")

        input = {
            "tilstande": {
                "facetpubliceret": [
                    {
                        "publiceret": self.published,
                        "virkning": {"from": from_time, "to": to_time},
                    }
                ]
            },
            "attributter": {
                "facetegenskaber": [
                    {
                        "brugervendtnoegle": self.user_key,
                        "virkning": {"from": from_time, "to": to_time},
                    }
                ]
            },
            "relationer": {
                "ansvarlig": [
                    {
                        "uuid": str(organisation_uuid),
                        "virkning": {"from": from_time, "to": to_time},
                        "objekttype": "Organisation",
                    }
                ],
            },
        }
        validate.validate(input, "facet")

        return {
            "states": input["tilstande"],
            "attributes": input["attributter"],
            "relations": input["relationer"],
        }


@strawberry.experimental.pydantic.input(
    model=FacetCreate,
    all_fields=True,
)
class FacetCreateInput:
    """input model for creating a facet."""


async def create_facet(input: FacetCreate, organisation_uuid: UUID, note: str) -> UUID:
    # Construct a LoRa registration object from our input arguments
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    # Let LoRa's SQL templates do their magic
    uuid = await asyncio.to_thread(
        db.create_or_import_object, "facet", note, registration
    )
    return uuid


async def delete_facet(facet_uuid: UUID, note: str) -> UUID:
    # Gather a blank registration
    registration: dict = {
        "states": {},
        "attributes": {},
        "relations": {},
    }
    # Let LoRa's SQL templates do their magic
    await asyncio.to_thread(
        db.delete_object, "facet", registration, note, str(facet_uuid)
    )
    return facet_uuid
