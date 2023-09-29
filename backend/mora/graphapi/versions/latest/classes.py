# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from uuid import UUID
from uuid import uuid4

from .models import ClassCreate
from .models import ClassTerminate
from .models import ClassUpdate
from mora import lora
from mora.util import get_uuid
from oio_rest import db


async def create_class(input: ClassCreate, organisation_uuid: UUID) -> UUID:
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    new_uuid = get_uuid(registration, required=False) or str(uuid4())

    c = lora.Connector()
    return UUID(await c.klasse.create(registration, new_uuid))


async def update_class(input: ClassUpdate, organisation_uuid: UUID) -> UUID:
    return await lora.Connector().klasse.update(
        input.to_registration(organisation_uuid=organisation_uuid), input.uuid
    )


async def terminate_class(input: ClassTerminate) -> UUID:
    await lora.Connector().klasse.update(input.to_registration(), input.uuid)
    return input.uuid


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
