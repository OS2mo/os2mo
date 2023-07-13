# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import KLECreate
from .models import KLETerminate
from .models import KLEUpdate
from mora import lora
from mora import mapping
from mora.service.kle import KLERequestHandler
from mora.triggers import Trigger


async def create_kle(input: KLECreate) -> UUID:
    """Creating a KLE annotation."""
    input_dict = input.to_handler_dict()

    handler = await KLERequestHandler.construct(input_dict, mapping.RequestType.CREATE)
    uuid = await handler.submit()

    return UUID(uuid)


async def update_kle(input: KLEUpdate) -> UUID:
    """Updating a KLE annotation."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.KLE,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await KLERequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_kle(input: KLETerminate) -> UUID:
    trigger = input.get_kle_trigger()
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
