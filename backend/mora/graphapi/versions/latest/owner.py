# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from .models import OwnerCreate
from mora import mapping
from mora.service.owner import OwnerRequestHandler


async def create_owner(input: OwnerCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await OwnerRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)
