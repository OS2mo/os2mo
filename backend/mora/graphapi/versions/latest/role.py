# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.role import RoleBindingRequestHandler

from .models import RoleBindingCreate
from .models import RoleBindingTerminate
from .models import RoleBindingUpdate


async def create_rolebinding(input: RoleBindingCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await RoleBindingRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_rolebinding(input: RoleBindingUpdate) -> UUID:
    """Updating a role."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ROLEBINDING,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await RoleBindingRequestHandler.construct(req, mapping.RequestType.EDIT)
    # coverage: pause
    uuid = await request.submit()

    return UUID(uuid)
    # coverage: unpause


async def terminate_rolebinding(input: RoleBindingTerminate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await RoleBindingRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    # coverage: pause
    await request.submit()

    return input.uuid
    # coverage: unpause
