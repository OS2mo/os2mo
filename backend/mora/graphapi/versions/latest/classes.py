# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from uuid import UUID

from .models import ClassCreate
from .models import ClassUpdate
from oio_rest import db


async def create_class(input: ClassCreate, organisation_uuid: UUID) -> UUID:
    # Construct a LoRa registration object from our input arguments
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    # Let LoRa's SQL templates do their magic
    uuid = await asyncio.to_thread(
        db.create_or_import_object,
        "klasse",
        "",
        registration,
        str(input.uuid) if input.uuid else None,
    )
    return uuid


async def update_class(
    input: ClassUpdate, class_uuid: UUID, organisation_uuid: UUID
) -> UUID:
    exists = await asyncio.to_thread(db.object_exists, "klasse", str(class_uuid))
    if not exists:
        raise ValueError("Cannot update a non-existent object")

    # Construct a LoRa registration object from our input arguments
    registration = input.to_registration(organisation_uuid=organisation_uuid)

    # Let LoRa's SQL templates do their magic
    life_cycle_code = await asyncio.to_thread(
        db.get_life_cycle_code, "klasse", str(class_uuid)
    )
    if life_cycle_code in (db.Livscyklus.SLETTET.value, db.Livscyklus.PASSIVERET.value):
        # Reactivate and update
        uuid = await asyncio.to_thread(
            db.update_object,
            "klasse",
            "",
            registration,
            uuid=str(class_uuid),
            life_cycle_code=db.Livscyklus.IMPORTERET.value,
        )
    else:
        # Update
        uuid = await asyncio.to_thread(
            db.create_or_import_object,
            "klasse",
            "",
            registration,
            str(class_uuid),
        )
    return uuid


async def delete_class(class_uuid: UUID) -> UUID:
    # Gather a blank registration
    registration: dict = {
        "states": {},
        "attributes": {},
        "relations": {},
    }
    # Let LoRa's SQL templates do their magic
    await asyncio.to_thread(
        db.delete_object, "klasse", registration, "", str(class_uuid)
    )
    return class_uuid
