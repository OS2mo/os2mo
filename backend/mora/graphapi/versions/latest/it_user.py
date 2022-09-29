# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import ITUserCreate
from .models import ITUserTerminate
from .types import ITUserType
from mora import lora
from mora import mapping
from mora.service.itsystem import ItsystemRequestHandler
from mora.triggers import Trigger


async def create(input: ITUserCreate) -> ITUserType:
    input_dict = input.to_handler_dict()

    handler = await ItsystemRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return ITUserType(uuid=UUID(uuid))


async def terminate(input: ITUserTerminate) -> ITUserType:
    trigger = input.get_trigger()
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

    return ITUserType(uuid=UUID(lora_result))
