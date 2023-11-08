# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from .models import LeaveCreate
from .models import LeaveTerminate
from .models import LeaveUpdate
from mora import lora
from mora import mapping
from mora.service.leave import LeaveRequestHandler
from mora.triggers import Trigger


async def create_leave(input: LeaveCreate) -> UUID:
    """Creating a leave."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await LeaveRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await request.submit()

    return UUID(uuid)


async def update_leave(input: LeaveUpdate) -> UUID:
    """Updating a leave."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.LEAVE,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await LeaveRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_leave(input: LeaveTerminate) -> UUID:
    trigger = input.get_leave_trigger()
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
