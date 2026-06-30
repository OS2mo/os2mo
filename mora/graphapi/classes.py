# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from mora import lora
from oio_rest import db

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
    return input.uuid


async def terminate_class(input: ClassTerminate) -> UUID:
    await lora.Connector().klasse.update(input.to_registration(), input.uuid)
    return input.uuid


async def delete_class(class_uuid: UUID) -> UUID:
    # Let LoRa's SQL templates do their magic
    # TODO: or maybe don't, this blocks from deleting oio_rest entirely
    await db.delete_object("klasse", "", str(class_uuid))
    return class_uuid
