# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL association related helper functions."""
from uuid import UUID

from .models import AssociationCreate
from .models import AssociationTerminate
from .models import AssociationUpdate
from .types import UUIDReturn
from mora import lora
from mora import mapping
from mora.service.association import AssociationRequestHandler
from mora.triggers import Trigger


async def create_association(input: AssociationCreate) -> UUIDReturn:
    input_dict = input.to_handler_dict()

    handler = await AssociationRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return UUIDReturn(uuid=UUID(uuid))


async def update_association(input: AssociationUpdate) -> UUIDReturn:
    """Helper function for updating associations."""
    input_dict = input.to_handler_dict()

    req = {
        mapping.TYPE: mapping.ASSOCIATION,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await AssociationRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUIDReturn(uuid=UUID(uuid))


async def terminate_association(input: AssociationTerminate) -> UUIDReturn:
    """Helper function for terminating associations."""
    trigger = input.get_association_trigger()
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
