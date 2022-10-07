# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import ManagerCreate
from .models import ManagerUpdate
from .types import ManagerType
from mora import mapping
from mora.service.manager import ManagerRequestHandler


async def create_manager(input: ManagerCreate) -> ManagerType:
    """Creating a manager."""
    input_dict = input.to_handler_dict()

    handler = await ManagerRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return ManagerType(uuid=UUID(uuid))


async def update_manager(input: ManagerUpdate) -> ManagerType:
    """Updating a manager."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.MANAGER,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await ManagerRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return ManagerType(uuid=UUID(uuid))
