# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL association related helper functions."""
from uuid import UUID

from .models import AssociationCreate
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
