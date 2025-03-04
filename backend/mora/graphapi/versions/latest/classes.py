# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from oio_rest import db

from mora import lora

from .models import ClassCreate
from .models import ClassTerminate
from .models import ClassUpdate


async def create_class(input: ClassCreate, organisation_uuid: UUID) -> UUID:
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    c = lora.Connector()
    return UUID(await c.klasse.create(registration, input.uuid))


async def update_class(input: ClassUpdate, organisation_uuid: UUID) -> UUID:
    c = lora.Connector()
    await c.klasse.update(
        input.to_registration(organisation_uuid=organisation_uuid), input.uuid
    )
    # coverage: pause
    return input.uuid
    # coverage: unpause


async def terminate_class(input: ClassTerminate) -> UUID:
    await lora.Connector().klasse.update(input.to_registration(), input.uuid)
    # coverage: pause
    return input.uuid
    # coverage: unpause


async def delete_class(class_uuid: UUID) -> UUID:
    # Gather a blank registration
    registration: dict = {
        "states": {},
        "attributes": {},
        "relations": {},
    }
    # Let LoRa's SQL templates do their magic
    await db.delete_object("klasse", registration, "", str(class_uuid))
    # coverage: pause
    return class_uuid
    # coverage: unpause
