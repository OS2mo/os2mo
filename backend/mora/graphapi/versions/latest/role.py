# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from .models import RoleCreate
from .models import RoleTerminate
from .models import RoleUpdate
from mora import lora
from mora import mapping
from mora.service.role import RoleRequestHandler
from mora.triggers import Trigger


async def create_role(input: RoleCreate) -> UUID:
    input_dict = input.to_handler_dict()

    handler = await RoleRequestHandler.construct(input_dict, mapping.RequestType.CREATE)
    uuid = await handler.submit()

    return UUID(uuid)


async def update_role(input: RoleUpdate) -> UUID:
    """Updating a role."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.ROLE,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await RoleRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_role(input: RoleTerminate) -> UUID:
    trigger = input.get_role_trigger()
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
