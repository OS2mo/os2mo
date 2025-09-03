# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder

from backend.mora.graphapi.versions.latest.inputs import ManagerUpdateInput
from mora import mapping
from mora.service.manager import ManagerRequestHandler

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


def to_handler_dict(input: ManagerUpdateInput) -> dict:
    data_dict: dict = {
        "validity": {
            "from": input.validity.from_date.date().isoformat(),
            "to": input.validity.to_date.date().isoformat()
            if input.validity.to_date
            else None,
        },
        "user_key": input.user_key,
        "person": gen_uuid(input.person),
        "org_unit": gen_uuid(input.org_unit),
        "manager_type": gen_uuid(input.manager_type),
        "manager_level": gen_uuid(input.manager_level),
    }
    if input.engagement is not strawberry.UNSET:
        data_dict["engagement"] = (
            gen_uuid(input.engagement) if input.engagement else None,
        )
    if input.responsibility:
        data_dict["responsibility"] = list(map(gen_uuid, input.responsibility))

    return {k: v for k, v in data_dict.items() if (v is not None) or k == "person"}


async def update_manager(input: ManagerUpdateInput) -> UUID:
    """Updating a manager."""

    input_dict = jsonable_encoder(to_handler_dict(input))

    req = {
        mapping.TYPE: mapping.MANAGER,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }
    breakpoint()
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
