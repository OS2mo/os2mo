# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""GraphQL IT-association related helper functions."""
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from .models import ITAssociationCreate
from .models import ITAssociationTerminate
from .models import ITAssociationUpdate
from mora import lora
from mora import mapping
from mora.service.association import AssociationRequestHandler
from mora.triggers import Trigger


async def create_itassociation(input: ITAssociationCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    handler = await AssociationRequestHandler.construct(
        input_dict, mapping.RequestType.CREATE
    )
    uuid = await handler.submit()

    return UUID(uuid)


async def update_itassociation(input: ITAssociationUpdate) -> UUID:
    """Helper function for updating IT-associations."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ASSOCIATION,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await AssociationRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def terminate_itassociation(input: ITAssociationTerminate) -> UUID:
    trigger = input.get_itassociation_trigger()
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
