# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
from uuid import UUID

from fastapi.encoders import jsonable_encoder

from ....mapping import RequestType
from .models import AddressCreate
from .models import AddressTerminate
from .models import AddressUpdate
from mora import exceptions
from mora import lora
from mora import mapping
from mora.service.address import AddressRequestHandler
from mora.triggers import Trigger


async def create_address(input: AddressCreate) -> UUID:
    input_dict = jsonable_encoder(input.to_handler_dict())

    request = await AddressRequestHandler.construct(input_dict, RequestType.CREATE)
    uuid = await request.submit()

    return UUID(uuid)


async def update_address(input: AddressUpdate) -> UUID:
    """Helper function for updating addresses."""
    input_dict = jsonable_encoder(input.to_handler_dict())

    req = {
        mapping.TYPE: mapping.ADDRESS,
        mapping.UUID: str(input.uuid),
        mapping.DATA: input_dict,
    }

    request = await AddressRequestHandler.construct(req, mapping.RequestType.EDIT)
    uuid = await request.submit()

    return UUID(uuid)


async def _get_original_addr(
    addr_uuid: UUID, from_date: datetime.datetime | None
) -> dict | None:
    original = await lora.Connector(effective_date=from_date).organisationfunktion.get(
        str(addr_uuid)
    )

    return original


async def terminate_address(input: AddressTerminate) -> UUID:
    address_terminate = input
    original_addr = await _get_original_addr(
        address_terminate.uuid, address_terminate.from_date
    )
    if not original_addr:
        exceptions.ErrorCodes.E_NOT_FOUND(
            uuid=str(address_terminate.uuid),
            original=original_addr,
        )

    address_trigger = address_terminate.get_address_trigger()
    trigger_dict = address_trigger.to_trigger_dict()

    # ON_BEFORE
    _ = await Trigger.run(trigger_dict)

    # Do LoRa update
    lora_conn = lora.Connector()
    lora_result = await lora_conn.organisationfunktion.update(
        address_terminate.get_lora_payload(), str(address_terminate.uuid)
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
