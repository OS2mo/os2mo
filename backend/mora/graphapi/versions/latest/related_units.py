# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.related import RelatedUnitRequestHandler
from mora.service.related import map_org_units

from .models import RelatedUnitCreate
from .models import RelatedUnitsUpdate
from .models import RelatedUnitTerminate
from .models import RelatedUnitUpdate


async def create_related_unit(input: RelatedUnitCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await RelatedUnitRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_related_unit(input: RelatedUnitUpdate) -> UUID:
    """Helper function for updating related units."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.RELATED_UNIT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await RelatedUnitRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_related_unit(input: RelatedUnitTerminate) -> UUID:
    """Helper function for terminating related units."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await RelatedUnitRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    await request.submit()

    return input.uuid


async def update_related_units(input: RelatedUnitsUpdate) -> UUID:
    """Updates relations for an org_unit."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    origin = input_dict.pop("origin")
    handler = await map_org_units(origin=origin, req=input_dict)
    if handler:
        uuid = origin

    return UUID(uuid)
