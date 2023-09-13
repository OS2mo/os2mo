# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from uuid import UUID
from uuid import uuid4

from .models import ClassCreate
from .models import ClassUpdate
from mora import lora
from mora.util import get_uuid
from oio_rest import db


async def create_class(input: ClassCreate, organisation_uuid: UUID) -> UUID:
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    new_uuid = get_uuid(registration, required=False) or str(uuid4())

    c = lora.Connector()
    return await c.klasse.create(registration, new_uuid)


async def update_class(input: ClassUpdate, organisation_uuid: UUID) -> UUID:
    c = lora.Connector()
    result = await c.klasse.update(
        input.to_registration(organisation_uuid=organisation_uuid), input.uuid
    )
    return result
    # return await c.facet.update(
    #     input.to_registration(organisation_uuid=organisation_uuid), input.uuid
    # )


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
