# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
from datetime import datetime
from itertools import product
from typing import Dict
from typing import List
from typing import Tuple
from uuid import UUID

from ramqp.moqp import MOAMQPSystem
from ramqp.moqp import ObjectType
from ramqp.moqp import PayloadType
from ramqp.moqp import RequestType
from ramqp.moqp import ServiceType

from structlog import get_logger

from mora import config
from mora import exceptions
from mora import mapping
from mora import triggers
from mora import util

logger = get_logger()


amqp_system = MOAMQPSystem()


async def start_amqp():
    await amqp_system.start(
        amqp_url=config.get_settings().amqp_url,
        amqp_exchange=config.get_settings().amqp_os2mo_exchange,
    )


async def stop_amqp():
    await amqp_system.stop()


def to_datetime(trigger_dict: Dict) -> datetime:
    request = trigger_dict[triggers.Trigger.REQUEST]
    if trigger_dict[triggers.Trigger.REQUEST_TYPE] == mapping.RequestType.EDIT:
        request = request["data"]
    try:
        return util.get_valid_from(request)
    except exceptions.HTTPException:
        return util.get_valid_to(request)


async def amqp_sender(trigger_dict: Dict) -> None:

    object_type = ObjectType(trigger_dict[triggers.Trigger.ROLE_TYPE].lower())
    request_type = RequestType(trigger_dict[triggers.Trigger.REQUEST_TYPE].lower())

    def dispatch(service_type: ServiceType, service_uuid: UUID) -> None:
        payload = PayloadType(
            uuid=service_uuid,
            object_uuid=UUID(trigger_dict["uuid"]),
            time=to_datetime(trigger_dict),
        )
        logger.debug(
            "Registering AMQP publish message task",
            service_type=service_type,
            object_type=object_type,
            request_type=request_type,
            payload=payload,
        )
        asyncio.create_task(
            amqp_system.publish_message(
                service_type, object_type, request_type, payload
            )
        )

    if trigger_dict.get(triggers.Trigger.EMPLOYEE_UUID):
        dispatch(
            ServiceType(mapping.EMPLOYEE),
            UUID(trigger_dict[triggers.Trigger.EMPLOYEE_UUID])
        )

    if trigger_dict.get(triggers.Trigger.ORG_UNIT_UUID):
        dispatch(
            ServiceType(mapping.ORG_UNIT),
            UUID(trigger_dict[triggers.Trigger.ORG_UNIT_UUID])
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
