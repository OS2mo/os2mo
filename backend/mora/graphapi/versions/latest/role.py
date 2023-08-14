# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import RoleCreate
from mora import mapping
from mora.service.role import RoleRequestHandler


async def create_role(input: RoleCreate) -> UUID:
    input_dict = input.to_handler_dict()

    handler = await RoleRequestHandler.construct(input_dict, mapping.RequestType.CREATE)
    uuid = await handler.submit()

    return UUID(uuid)
