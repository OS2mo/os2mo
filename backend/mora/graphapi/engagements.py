#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL engagement related helper functions."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from mora import lora
from mora import mapping
from mora.graphapi.models import EngagementTerminate
from mora.graphapi.types import EngagementTerminateType
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
