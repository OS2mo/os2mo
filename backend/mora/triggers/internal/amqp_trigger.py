# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from datetime import datetime
from itertools import product
from uuid import UUID

from ramqp.mo import MOAMQPSystem
from structlog import get_logger

from mora import config
from mora import exceptions
from mora import mapping
from mora import triggers
from mora import util

logger = get_logger()
amqp_url = config.get_settings().amqp_url

amqp_settings = config.AMQPSettings(url=amqp_url) if amqp_url else {}

amqp_system = MOAMQPSystem(settings=amqp_settings)


async def start_amqp():
    await amqp_system.start()


async def stop_amqp():
    await amqp_system.stop()


def to_datetime(trigger_dict: dict) -> datetime:
    request = trigger_dict[triggers.Trigger.REQUEST]
    if trigger_dict[triggers.Trigger.REQUEST_TYPE] == mapping.RequestType.EDIT:
        request = request["data"]
    try:
        return util.get_valid_from(request)
    except exceptions.HTTPException:
        return util.get_valid_to(request)


async def amqp_sender(trigger_dict: dict) -> None:
    def dispatch(service_type: str, service_uuid: UUID) -> None:
        object_type = trigger_dict[triggers.Trigger.ROLE_TYPE].lower()
        request_type = trigger_dict[triggers.Trigger.REQUEST_TYPE].lower()
        routing_key = f"{service_type}.{object_type}.{request_type}"

        payload = {
            "uuid": service_uuid,
            "object_uuid": UUID(trigger_dict["uuid"]),
            "time": to_datetime(trigger_dict),
        }

        logger.debug(
            "Registering AMQP publish message task",
            routing_key=routing_key,
            payload=payload,
        )
        asyncio.create_task(amqp_system.publish_message(routing_key, payload))

    if trigger_dict.get(triggers.Trigger.EMPLOYEE_UUID):
        dispatch(
            mapping.EMPLOYEE,
            UUID(trigger_dict[triggers.Trigger.EMPLOYEE_UUID]),
        )

    if trigger_dict.get(triggers.Trigger.ORG_UNIT_UUID):
        dispatch(
            mapping.ORG_UNIT,
            UUID(trigger_dict[triggers.Trigger.ORG_UNIT_UUID]),
        )


async def register(app) -> bool:
    """Register an ON_AFTER triggers for all ROLE_TYPEs and RequestTypes.

    This method:
    * Checks the configuration of the module.
    * Establishes an AMQP connection to check credentials
    * Registers the AMQP trigger for all types.
    """
    if not config.get_settings().amqp_enable:
        logger.debug("AMQP Triggers not enabled!")
        return False

    await start_amqp()

    # Register trigger on everything
    ROLE_TYPES = [
        mapping.EMPLOYEE,
        mapping.ORG_UNIT,
        *mapping.RELATION_TRANSLATIONS.keys(),
    ]
    trigger_combinations = product(
        ROLE_TYPES, mapping.RequestType, [mapping.EventType.ON_AFTER]
    )
    for combi in trigger_combinations:
        triggers.Trigger.on(*combi)(amqp_sender)
    return True
