# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL association related helper functions."""

from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.association import AssociationRequestHandler

from .models import AssociationCreate
from .models import AssociationTerminate
from .models import AssociationUpdate


async def create_association(input: AssociationCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AssociationRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_association(input: AssociationUpdate) -> UUID:
    """Helper function for updating associations."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ASSOCIATION,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await AssociationRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_association(input: AssociationTerminate) -> UUID:
    """Helper function for terminating associations."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AssociationRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    await request.submit()

    return input.uuid
