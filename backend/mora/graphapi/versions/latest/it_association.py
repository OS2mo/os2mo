# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL IT-association related helper functions."""

from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.association import AssociationRequestHandler

from .models import ITAssociationCreate
from .models import ITAssociationTerminate
from .models import ITAssociationUpdate


async def create_itassociation(input: ITAssociationCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AssociationRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_itassociation(input: ITAssociationUpdate) -> UUID:
    """Helper function for updating IT-associations."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ASSOCIATION,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await AssociationRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_itassociation(input: ITAssociationTerminate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AssociationRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    await request.submit()

    return input.uuid
