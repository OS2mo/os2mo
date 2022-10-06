# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL association related helper functions."""
from uuid import UUID

from .models import AssociationCreate
from .models import AssociationUpdate
from .types import AssociationType
from mora import mapping
from mora.service.association import AssociationRequestHandler


async def create_association(input: AssociationCreate) -> AssociationType:
    input_dict = input.to_handler_dict()

    handler = await AssociationRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return AssociationType(uuid=UUID(uuid))


async def update_association(input: AssociationUpdate) -> AssociationType:
    """Helper function for updating associations."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.ASSOCIATION,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await AssociationRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return AssociationType(uuid=UUID(uuid))
