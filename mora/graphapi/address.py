# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.config import Settings
from mora.mapping import RequestType
from mora.service.address import AddressRequestHandler

from .models import AddressCreate
from .models import AddressTerminate
from .models import AddressUpdate


async def create_address(input: AddressCreate, settings: Settings) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AddressRequestHandler.construct(
        input_dict, RequestType.CREATE, settings
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_address(input: AddressUpdate, settings: Settings) -> UUID:
    """Helper function for updating addresses."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ADDRESS,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await AddressRequestHandler.construct(
        req, mapping.RequestType.EDIT, settings
    )
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_address(input: AddressTerminate, settings: Settings) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AddressRequestHandler.construct(
        input_dict, RequestType.TERMINATE, settings
    )
    await request.submit()

    return input.uuid
