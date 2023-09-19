# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from uuid import UUID
from uuid import uuid4

from .models import ClassCreate
from .models import ClassUpdate
from mora import lora
from oio_rest import db


async def create_class(input: ClassCreate, organisation_uuid: UUID) -> UUID:
    return await lora.Connector().klasse.create(
        input.to_registration(organisation_uuid=organisation_uuid),
        str(input.uuid) or str(uuid4()),
    )


async def update_class(input: ClassUpdate, organisation_uuid: UUID) -> UUID:
    return await lora.Connector().facet.update(
        input.to_registration(organisation_uuid=organisation_uuid), input.uuid
    )


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
