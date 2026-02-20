# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL engagement related helper functions."""

from uuid import UUID

from fastapi.encoders import jsonable_encoder

from mora import mapping
from mora.service.engagement import EngagementRequestHandler

from .models import EngagementCreate
from .models import EngagementTerminate
from .models import EngagementUpdate


async def create_engagement(input: EngagementCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await EngagementRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_engagement(input: EngagementUpdate) -> UUID:  # pragma: no cover
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ENGAGEMENT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await EngagementRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_engagement(input: EngagementTerminate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await EngagementRequestHandler.construct(
        input_dict, mapping.RequestType.TERMINATE
    )
    # coverage: pause
    await request.submit()

    return input.uuid
    # coverage: unpause
