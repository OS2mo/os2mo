# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.config import Settings
from mora.service.kle import KLERequestHandler

from .models import KLECreate
from .models import KLETerminate
from .models import KLEUpdate


async def create_kle(input: KLECreate, settings: Settings) -> UUID:
    """Creating a KLE annotation."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await KLERequestHandler.construct(
        input_dict, mapping.RequestType.CREATE, settings
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_kle(input: KLEUpdate, settings: Settings) -> UUID:
    """Updating a KLE annotation."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.KLE,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await KLERequestHandler.construct(req, mapping.RequestType.EDIT, settings)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_kle(input: KLETerminate, settings: Settings) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await KLERequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE, settings
    )
    await request.submit()

    return input.uuid
