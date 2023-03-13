# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import ManagerCreate
from .models import ManagerTerminate
from .models import ManagerUpdate
from .types import UUIDReturn
from mora import lora
from mora import mapping
from mora.service.manager import ManagerRequestHandler
from mora.triggers import Trigger


async def create_manager(input: ManagerCreate) -> UUIDReturn:
    """Creating a manager."""
    input_dict = input.to_handler_dict()

    handler = await ManagerRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return UUIDReturn(uuid=UUID(uuid))


async def update_manager(input: ManagerUpdate) -> UUIDReturn:
    """Updating a manager."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.MANAGER,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await ManagerRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUIDReturn(uuid=UUID(uuid))


async def terminate_manager(input: ManagerTerminate) -> UUIDReturn:
    trigger = input.get_manager_trigger()
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

    return UUIDReturn(uuid=UUID(lora_result))
