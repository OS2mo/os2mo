# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.config import Settings
from mora.service.leave import LeaveRequestHandler

from .models import LeaveCreate
from .models import LeaveTerminate
from .models import LeaveUpdate


async def create_leave(input: LeaveCreate, settings: Settings) -> UUID:
    """Creating a leave."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await LeaveRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE, settings
    )
    uuid = await request.submit()
    return UUID(uuid)


async def update_leave(input: LeaveUpdate, settings: Settings) -> UUID:
    """Updating a leave."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.LEAVE,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await LeaveRequestHandler.construct(
        req, mapping.RequestType.EDIT, settings
    )
    uuid = await request.submit()
    return UUID(uuid)


async def terminate_leave(input: LeaveTerminate, settings: Settings) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await LeaveRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE, settings
    )
    await request.submit()

    return input.uuid
