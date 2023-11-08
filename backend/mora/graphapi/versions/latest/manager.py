# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import ManagerCreate
from .models import ManagerTerminate
from .models import ManagerUpdate
from mora import mapping
from mora.service.manager import ManagerRequestHandler


async def create_manager(input: ManagerCreate) -> UUID:
    """Creating a manager."""
    input_dict = input.to_handler_dict()

    request = await ManagerRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_manager(input: ManagerUpdate) -> UUID:
    """Updating a manager."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.MANAGER,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await ManagerRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_manager(input: ManagerTerminate) -> UUID:
    input_dict = input.to_handler_dict()

    request = await ManagerRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    await request.submit()

    return input.uuid
