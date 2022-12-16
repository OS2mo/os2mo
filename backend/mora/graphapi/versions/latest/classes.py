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


class ClassCreate(BaseModel):
    """Model representing a Class creation."""

    name: str = Field(description="Mo-class name.")
    user_key: str = Field(description="Extra info or uuid")
    facet_uuid: UUID = Field(description="UUID of the related facet.")

    scope: str | None = Field(description="Scope of the class.")
    published: str = Field(
        "Publiceret", description="Published state of the class object."
    )
    parent_uuid: UUID | None = Field(description="UUID of the parent class.")
    example: str | None = Field(description="Example usage.")
    owner: UUID | None = Field(description="Owner of class")

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid

    def to_registration(self, organisation_uuid: UUID) -> dict:
        from_time = to_lora_time("-infinity")
        to_time = to_lora_time("infinity")

        klasseegenskaber = {
            "brugervendtnoegle": self.user_key,
            "titel": self.name,
            "virkning": {"from": from_time, "to": to_time},
        }
        if self.example is not None:
            klasseegenskaber["eksempel"] = self.example
        if self.scope is not None:
            klasseegenskaber["omfang"] = self.scope

        relations = {
            "facet": [
                {
                    "uuid": str(self.facet_uuid),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "Facet",
                }
            ],
            "ansvarlig": [
                {
                    "uuid": str(organisation_uuid),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "Organisation",
                }
            ],
        }
        # TODO: fix
        if self.parent_uuid is not None:
            relations["overordnetklasse"] = [
                {
                    "uuid": str(self.parent_uuid),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "klasse",
                }
            ]
        if self.owner is not None:
            relations["ejer"] = [
                {
                    "uuid": str(self.owner),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "Organisationsenhed",
                }
            ]

        input = {
            "tilstande": {
                "klassepubliceret": [
                    {
                        "publiceret": self.published,
                        "virkning": {"from": from_time, "to": to_time},
                    }
                ]
            },
            "attributter": {"klasseegenskaber": [klasseegenskaber]},
            "relationer": relations,
        }
        validate.validate(input, "klasse")

        return {
            "states": input["tilstande"],
            "attributes": input["attributter"],
            "relations": input["relationer"],
        }


@strawberry.experimental.pydantic.input(
    model=ClassCreate,
    all_fields=True,
)
class ClassCreateInput:
    """input model for creating a class."""


async def create_class(input: ClassCreate, organisation_uuid: UUID, note: str) -> UUID:
    # Construct a LoRa registration object from our input arguments
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    # Let LoRa's SQL templates do their magic
    uuid = await asyncio.to_thread(
        db.create_or_import_object, "klasse", note, registration
    )
    return uuid


async def class_exists(uuid: UUID) -> bool:
    exists = await asyncio.to_thread(db.object_exists, "klasse", str(uuid))
    return exists


async def class_deleted(uuid: UUID) -> bool:
    livscyklus = db.get_life_cycle_code("klasse", str(uuid))
    return livscyklus == db.Livscyklus.SLETTET.value


async def class_passive(uuid: UUID) -> bool:
    livscyklus = db.get_life_cycle_code("klasse", str(uuid))
    return livscyklus == db.Livscyklus.PASSIVERET.value


async def update_class(
    input: ClassCreate, class_uuid: UUID, organisation_uuid: UUID, note: str
) -> UUID:
    exists = class_exists(class_uuid)
    if not exists:
        raise ValueError("Cannot update a non-existent object")

    # Construct a LoRa registration object from our input arguments
    registration = input.to_registration(organisation_uuid=organisation_uuid)

    deleted = class_deleted(class_uuid)
    passive = class_passive(class_uuid)
    # Let LoRa's SQL templates do their magic
    if deleted or passive:
        # Reactivate and update
        uuid = await asyncio.to_thread(
            db.update_object,
            "klasse",
            note,
            registration,
            uuid=str(class_uuid),
            # life_cycle_code=db.Livscyklus.IMPORTERET.value,
        )
    else:
        # Update
        uuid = await asyncio.to_thread(
            db.create_or_import_object,
            "klasse",
            note,
            registration,
            str(class_uuid),
        )
    return uuid


async def delete_class(class_uuid: UUID, note: str) -> UUID:
    # Gather a blank registration
    registration: dict = {
        "states": {},
        "attributes": {},
        "relations": {},
    }
    # Let LoRa's SQL templates do their magic
    await asyncio.to_thread(
        db.delete_object, "klasse", registration, note, str(class_uuid)
    )
    return class_uuid
