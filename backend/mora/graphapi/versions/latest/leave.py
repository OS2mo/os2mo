# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.leave import LeaveRequestHandler

from .models import LeaveCreate
from .models import LeaveTerminate
from .models import LeaveUpdate


async def create_leave(input: LeaveCreate) -> UUID:
    """Creating a leave."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await LeaveRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()
    # coverage: pause
    return UUID(uuid)
    # coverage: unpause


async def update_leave(input: LeaveUpdate) -> UUID:
    """Updating a leave."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.LEAVE,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await LeaveRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()
    # coverage: pause
    return UUID(uuid)
    # coverage: unpause


async def terminate_leave(input: LeaveTerminate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await LeaveRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    # coverage: pause
    await request.submit()

    return input.uuid
    # coverage: unpause
