# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.itsystem import ItsystemRequestHandler

from .models import ITUserCreate
from .models import ITUserTerminate
from .models import ITUserUpdate


async def create_ituser(input: ITUserCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await ItsystemRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_ituser(input: ITUserUpdate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.IT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await ItsystemRequestHandler.construct(req, mapping.RequestType.EDIT)
    # coverage: pause
    uuid = await request.submit()

    return UUID(uuid)
    # coverage: unpause


async def terminate_ituser(input: ITUserTerminate) -> UUID:  # pragma: no cover
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await ItsystemRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    await request.submit()

    return input.uuid
