# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL engagement related helper functions."""
from uuid import UUID

from .models import EngagementCreate
from .models import EngagementTerminate
from .models import EngagementUpdate
from .types import EngagementTerminateType
from .types import EngagementType
from mora import lora
from mora import mapping
from mora.service.engagement import EngagementRequestHandler
from mora.triggers import Trigger


async def terminate_engagement(input: EngagementTerminate) -> EngagementTerminateType:
    trigger = input.get_engagement_trigger()
    trigger_dict = trigger.to_trigger_dict()

    # ON_BEFORE
    if not input.triggerless:
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

    if not input.triggerless:
        _ = await Trigger.run(trigger_dict)

    return EngagementTerminateType(uuid=UUID(lora_result))


async def create_engagement(input: EngagementCreate) -> EngagementType:
    input_dict = input.to_handler_dict()

    handler = await EngagementRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return EngagementType(uuid=UUID(uuid))


async def update_engagement(input: EngagementUpdate) -> EngagementType:
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.ENGAGEMENT,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await EngagementRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return EngagementType(uuid=UUID(uuid))
