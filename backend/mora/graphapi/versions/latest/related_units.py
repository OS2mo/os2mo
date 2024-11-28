# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from .models import RelatedUnitsUpdate
from mora.service.related import map_org_units


async def update_related_units(input: RelatedUnitsUpdate) -> UUID:
    """Updates relations for an org_unit."""
    input_dict = jsonable_encoder(input.to_handler_dict())
    print("¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
    print(input_dict)

    origin = input_dict.pop("origin")
    handler = await map_org_units(origin=origin, req=input_dict)
    if handler:
        uuid = origin

    return UUID(uuid)
