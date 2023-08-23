# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL IT-association related helper functions."""
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from .models import ITAssociationCreate
from mora import mapping
from mora.service.association import AssociationRequestHandler


async def create_itassociation(input: ITAssociationCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    handler = await AssociationRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return UUID(uuid)
