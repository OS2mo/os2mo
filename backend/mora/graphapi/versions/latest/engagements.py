# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL engagement related helper functions."""
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from .models import EngagementCreate
from .models import EngagementTerminate
from .models import EngagementUpdate
from mora import lora
from mora import mapping
from mora.service.engagement import EngagementRequestHandler
from mora.triggers import Trigger


async def terminate_engagement(input: EngagementTerminate) -> UUID:
    trigger = input.get_engagement_trigger()
    trigger_dict = trigger.to_trigger_dict()

    # ON_BEFORE
    _ = await Trigger.run(trigger_dict)

    # Do LoRa update
    lora_conn = lora.Connector()
    lora_result = await lora_conn.organisationfunktion.update(
        input.get_lora_payload(), str(input.uuid)
    )

    # ON_AFTER
    trigger_dict.update(
        {
            Trigger.RESULT: lora_result,
            Trigger.EVENT_TYPE: mapping.EventType.ON_AFTER,
        }
    )

    _ = await Trigger.run(trigger_dict)

    return UUID(lora_result)


async def create_engagement(input: EngagementCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    handler = await EngagementRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return UUID(uuid)


async def update_engagement(input: EngagementUpdate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ENGAGEMENT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await EngagementRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)
