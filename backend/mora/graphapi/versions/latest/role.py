# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import RoleCreate
from .models import RoleUpdate
from mora import mapping
from mora.service.role import RoleRequestHandler


async def create_role(input: RoleCreate) -> UUID:
    input_dict = input.to_handler_dict()

    handler = await RoleRequestHandler.construct(input_dict, mapping.RequestType.CREATE)
    uuid = await handler.submit()

    return UUID(uuid)


async def update_role(input: RoleUpdate) -> UUID:
    """Updating a role."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.ROLE,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await RoleRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)
