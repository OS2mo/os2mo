# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.manager import ManagerRequestHandler

from .inputs import ManagerUpdateInput
from .models import ManagerCreate
from .models import ManagerTerminate
from .models import gen_uuid


async def create_manager(input: ManagerCreate) -> UUID:
    """Creating a manager."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await ManagerRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_manager(input: ManagerUpdateInput) -> UUID:
    """Updating a manager."""
    input_dict = jsonable_encoder(input.to_pydantic().to_handler_dict())

    req = {
        mapping.TYPE: mapping.MANAGER,
        mapping.UUID: str(input.uuid),  # type: ignore
        mapping.DATA: input_dict,
    }

    request = await ManagerRequestHandler.construct(req, mapping.RequestType.EDIT)
    # coverage: pause
    uuid = await request.submit()

    return UUID(uuid)
    # coverage: unpause


async def terminate_manager(input: ManagerTerminate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await ManagerRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    # coverage: pause
    await request.submit()

    return input.uuid
    # coverage: unpause
