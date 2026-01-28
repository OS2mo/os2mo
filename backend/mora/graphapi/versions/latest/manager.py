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


def to_handler_dict(input: ManagerUpdateInput) -> dict:
    input_any: Any = input
    data_dict: dict = {
        "validity": {
            "from": input_any.validity.from_date.date().isoformat(),
            "to": input_any.validity.to_date.date().isoformat()
            if input_any.validity.to_date
            else None,
        },
    }

    if input_any.user_key is not strawberry.UNSET:
        data_dict["user_key"] = input_any.user_key

    if input_any.person is not strawberry.UNSET:
        data_dict["person"] = gen_uuid(input_any.person)

    if input_any.org_unit is not strawberry.UNSET:
        data_dict["org_unit"] = gen_uuid(input_any.org_unit)

    if input_any.manager_type is not strawberry.UNSET:
        data_dict["manager_type"] = gen_uuid(input_any.manager_type)

    if input_any.manager_level is not strawberry.UNSET:
        data_dict["manager_level"] = gen_uuid(input_any.manager_level)

    if input_any.engagement is not strawberry.UNSET:
        data_dict["engagement"] = (
            gen_uuid(input_any.engagement) if input_any.engagement else None
        )
    if input_any.responsibility is not strawberry.UNSET and input_any.responsibility:
        data_dict["responsibility"] = list(map(gen_uuid, input_any.responsibility))

    return {
        k: v
        for k, v in data_dict.items()
        if (v is not None) or k in ("person", "engagement")
    }


async def update_manager(input: ManagerUpdateInput) -> UUID:
    """Updating a manager."""
    input_dict = jsonable_encoder(to_handler_dict(input))

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
