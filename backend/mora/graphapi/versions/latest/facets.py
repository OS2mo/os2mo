# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from oio_rest import db

from mora import lora

from .models import FacetCreate
from .models import FacetTerminate
from .models import FacetUpdate


async def create_facet(input: FacetCreate, organisation_uuid: UUID) -> UUID:
    registration = input.to_registration(organisation_uuid=organisation_uuid)
    c = lora.Connector()
    return UUID(await c.facet.create(registration, input.uuid))


async def update_facet(input: FacetUpdate, organisation_uuid: UUID) -> UUID:
    c = lora.Connector()
    await c.facet.update(
        input.to_registration(organisation_uuid=organisation_uuid), input.uuid
    )
    # coverage: pause
    return input.uuid
    # coverage: unpause


async def terminate_facet(input: FacetTerminate) -> UUID:
    await lora.Connector().facet.update(input.to_registration(), input.uuid)
    # coverage: pause
    return input.uuid
    # coverage: unpause


async def delete_facet(facet_uuid: UUID) -> UUID:
    # Let LoRa's SQL templates do their magic
    await db.delete_object("facet", "", str(facet_uuid))
    # coverage: pause
    return facet_uuid
    # coverage: unpause
