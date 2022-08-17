#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from mora import lora
from mora import mapping
from mora.graphapi.models import AddressTerminate
from mora.graphapi.types import AddressTerminateType
from mora.triggers import Trigger


async def terminate_addr(address_terminate: AddressTerminate) -> AddressTerminateType:
    address_trigger = address_terminate.get_address_trigger()
    trigger_dict = address_trigger.to_trigger_dict()

    # ON_BEFORE
    if not address_terminate.triggerless:
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

    # ON_AFTER
    if not address_terminate.triggerless:
        _ = await Trigger.run(trigger_dict)

    return AddressTerminateType(uuid=UUID(lora_result))
