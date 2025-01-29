# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from oio_rest import db

from mora import lora

from .models import ITSystemCreate
from .models import ITSystemTerminate
from .models import ITSystemUpdate


async def create_itsystem(input: ITSystemCreate, organisation_uuid: UUID) -> UUID:
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    c = lora.Connector()
    return UUID(await c.itsystem.create(registration, input.uuid))


async def update_itsystem(input: ITSystemUpdate, organisation_uuid: UUID) -> UUID:
    c = lora.Connector()
    await c.itsystem.update(
        input.to_registration(organisation_uuid=organisation_uuid), str(input.uuid)
    )
    return input.uuid


async def terminate_itsystem(input: ITSystemTerminate) -> UUID:
    c = lora.Connector()
    await c.itsystem.update(input.to_registration(), input.uuid)
    return input.uuid


async def delete_itsystem(itsystem_uuid: UUID, note: str) -> UUID:
    # Gather a blank registration
    registration: dict[str, dict] = {
        "states": {},
        "attributes": {},
        "relations": {},
    }
    # Let LoRa's SQL templates do their magic
    await db.delete_object("itsystem", registration, note, str(itsystem_uuid))
    return itsystem_uuid
