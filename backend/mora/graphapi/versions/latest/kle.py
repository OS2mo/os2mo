# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import KLECreate
from mora import mapping
from mora.service.kle import KLERequestHandler


async def create_kle(input: KLECreate) -> UUID:
    """Creating a KLE annotation."""
    input_dict = input.to_handler_dict()

    handler = await KLERequestHandler.construct(input_dict, mapping.RequestType.CREATE)
    uuid = await handler.submit()

    return UUID(uuid)
