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
    # coverage: pause
    return input.uuid
    # coverage: unpause


async def terminate_itsystem(input: ITSystemTerminate) -> UUID:
    c = lora.Connector()
    await c.itsystem.update(input.to_registration(), input.uuid)
    # coverage: pause
    return input.uuid
    # coverage: unpause


async def delete_itsystem(itsystem_uuid: UUID, note: str) -> UUID:  # pragma: no cover
    # Let LoRa's SQL templates do their magic
    await db.delete_object("itsystem", note, str(itsystem_uuid))
    return itsystem_uuid
