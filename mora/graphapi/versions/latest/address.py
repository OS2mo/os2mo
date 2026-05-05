# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.address import AddressRequestHandler

from ....mapping import RequestType
from .models import AddressCreate
from .models import AddressTerminate
from .models import AddressUpdate


async def create_address(input: AddressCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AddressRequestHandler.construct(input_dict, RequestType.CREATE)
    # coverage: pause
    uuid = await request.submit()

    return UUID(uuid)
    # coverage: unpause


async def update_address(input: AddressUpdate) -> UUID:
    """Helper function for updating addresses."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ADDRESS,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await AddressRequestHandler.construct(req, mapping.RequestType.EDIT)
    # coverage: pause
    uuid = await request.submit()

    return UUID(uuid)
    # coverage: unpause


async def terminate_address(input: AddressTerminate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AddressRequestHandler.construct(input_dict, RequestType.TERMINATE)
    # coverage: pause
    await request.submit()

    return input.uuid
    # coverage: unpause
