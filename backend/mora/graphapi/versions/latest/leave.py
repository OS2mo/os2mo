# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from .models import LeaveCreate
from mora import mapping
from mora.service.leave import LeaveRequestHandler


async def create_leave(input: LeaveCreate) -> UUID:
    """Creating a leave."""
    req = jsonable_encoder(input.to_handler_dict())

    request = await LeaveRequestHandler.construct(req, mapping.RequestType.CREATE)
    uuid = await request.submit()

    return UUID(uuid)
