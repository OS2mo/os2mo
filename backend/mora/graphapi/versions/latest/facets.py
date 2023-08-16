# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from uuid import UUID

import strawberry
from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field

from mora.util import NEGATIVE_INFINITY
from mora.util import POSITIVE_INFINITY
from mora.util import to_lora_time
from oio_rest import db
from oio_rest import validate
from ramodels.mo import Validity as RAValidity


class FacetCreate(BaseModel):
    """Model representing a facet creation."""

    user_key: str = Field(description="Facet name.")
    published: str = Field(
        "Publiceret", description="Published state of the facet object."
    )

    validity: RAValidity | None = Field(
        None,
        description="Validity range for the facet. Default to ['-infinity', 'infinity']",
    )

    class Config:
        frozen = True
        extra = Extra.forbid

    def to_registration(self, organisation_uuid: UUID) -> dict:
        from_time = to_lora_time(NEGATIVE_INFINITY)
        to_time = to_lora_time(POSITIVE_INFINITY)

        if self.validity and self.validity.from_date:
            from_time = to_lora_time(self.validity.from_date)
        if self.validity and self.validity.to_date:
            to_time = to_lora_time(self.validity.to_date)

        input = {
            "tilstande": {
                "facetpubliceret": [
                    {
                        "publiceret": self.published,
                        "virkning": {"from": from_time, "to": to_time},
                    }
                ],
                # TODO: Implement missing custom db-type for below state
                # "facetgyldighed": [
                #     {
                #         "gyldighed": "Aktiv",
                #         "virkning": {"from": from_time, "to": to_time},
                #     }
                # ],
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
    """Input model for creating a facet."""


async def create_facet(input: FacetCreate, organisation_uuid: UUID, note: str) -> UUID:
    # Construct a LoRa registration object from our input arguments
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    # Let LoRa's SQL templates do their magic
    uuid = await asyncio.to_thread(
        db.create_or_import_object, "facet", note, registration
    )
    return uuid


class FacetUpdate(FacetCreate):
    """Model representing a facet updates."""

    uuid: UUID = Field(description="UUID of the facet to update.")


@strawberry.experimental.pydantic.input(
    model=FacetUpdate,
    all_fields=True,
)
class FacetUpdateInput:
    """Input model for updating a facet."""


async def update_facet(
    input: FacetCreate, facet_uuid: UUID, organisation_uuid: UUID, note: str
) -> UUID:
    exists = await asyncio.to_thread(db.object_exists, "facet", str(facet_uuid))
    if not exists:
        raise ValueError("Cannot update a non-existent object")

    # Construct a LoRa registration object from our input arguments
    registration = input.to_registration(organisation_uuid=organisation_uuid)

    # Let LoRa's SQL templates do their magic
    life_cycle_code = await asyncio.to_thread(
        db.get_life_cycle_code, "facet", str(facet_uuid)
    )
    if life_cycle_code in (db.Livscyklus.SLETTET.value, db.Livscyklus.PASSIVERET.value):
        # Reactivate and update
        uuid = await asyncio.to_thread(
            db.update_object,
            "facet",
            note,
            registration,
            uuid=str(facet_uuid),
            life_cycle_code=db.Livscyklus.IMPORTERET.value,
        )
    else:
        # Update
        uuid = await asyncio.to_thread(
            db.create_or_import_object,
            "facet",
            note,
            registration,
            str(facet_uuid),
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
