# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json
from datetime import datetime
from itertools import product
from typing import Dict
from typing import List
from typing import Tuple

import aio_pika
from mora import config
from mora import exceptions
from mora import mapping
from mora import triggers
from mora import util
from structlog import get_logger

logger = get_logger()

_SERVICES = ("employee", "org_unit")
_OBJECT_TYPES = (
    "address",
    "association",
    "employee",
    "engagement",
    "it",
    "kle",
    "leave",
    "manager",
    "owner",
    "org_unit",
    "related_unit",
    "role",
)
_ACTIONS = tuple(request_type.value.lower() for request_type in mapping.RequestType)


async def publish_message(
    service: str,
    object_type: str,
    action: str,
    service_uuid: str,
    object_uuid: str,
    datetime: datetime,
) -> None:
    """Send a message to the MO exchange.

    For the full documentation, refer to "AMQP Messages" in the docs.
    The source for that is in ``docs/amqp.rst``.

    """
    # we are strict about the topic format to avoid programmer errors.
    if service not in _SERVICES:
        raise ValueError(
            "service {!r} not allowed, use one of {!r}".format(service, _SERVICES)
        )
    if object_type not in _OBJECT_TYPES:
        raise ValueError(
            "object_type {!r} not allowed, use one of {!r}".format(
                object_type, _OBJECT_TYPES
            )
        )
    if action not in _ACTIONS:
        raise ValueError(
            "action {!r} not allowed, use one of {!r}".format(action, _ACTIONS)
        )

    topic = "{}.{}.{}".format(service, object_type, action)
    message = {
        "uuid": service_uuid,
        "object_uuid": object_uuid,
        "time": datetime.isoformat(),
    }

    message = aio_pika.Message(body=json.dumps(message).encode("utf-8"))

    # Message publishing is a secondary task to writing to lora.
    #
    # We should not throw a HTTPError in the case where lora writing is
    # successful, but amqp is down. Therefore, the try/except block.
    try:
        connection = await get_connection()
        await connection["exchange"].publish(
            message=message,
            routing_key=topic,
        )
    except aio_pika.exceptions.AMQPError:
        logger.error(
            "Failed to publish AMQP message",
            topic=topic,
            message=message,
            exc_info=True,
        )


async def amqp_sender(trigger_dict: Dict) -> None:
    request_type = trigger_dict[triggers.Trigger.REQUEST_TYPE]

    request = trigger_dict[triggers.Trigger.REQUEST]
    if request_type == mapping.RequestType.EDIT:
        request = request["data"]

    try:  # date = from or to
        datetime = util.get_valid_from(request)
    except exceptions.HTTPException:
        datetime = util.get_valid_to(request)

    action = request_type.value.lower()
    object_type = trigger_dict[triggers.Trigger.ROLE_TYPE]
    object_uuid = trigger_dict["uuid"]

    amqp_messages: List[Tuple[str, str]] = []

    if trigger_dict.get(triggers.Trigger.EMPLOYEE_UUID):
        amqp_messages.append(
            (mapping.EMPLOYEE, trigger_dict[triggers.Trigger.EMPLOYEE_UUID])
        )

    if trigger_dict.get(triggers.Trigger.ORG_UNIT_UUID):
        amqp_messages.append(
            (mapping.ORG_UNIT, trigger_dict[triggers.Trigger.ORG_UNIT_UUID])
        )

    for service, service_uuid in amqp_messages:
        await publish_message(
            service, object_type, action, service_uuid, object_uuid, datetime
        )


async def get_connection():
    # we cant bail out here, as it seems amqp trigger
    # tests must be able to run without ENABLE_AMQP
    # instead we leave the connection object empty
    # in which case publish_message will bail out
    # this is the original mode of operation restored

    connection = await aio_pika.connect_robust(
        host=config.get_settings().amqp_host,
        port=config.get_settings().amqp_port,
    )
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        name=config.get_settings().amqp_os2mo_exchange,
        type="topic",
    )
    return {
        "connection": connection,
        "channel": channel,
        "exchange": exchange,
    }


def register(app) -> bool:
    """Register an ON_AFTER triggers for all ROLE_TYPEs and RequestTypes.

    This method:
    * Checks the configuration of the module.
    * Establishes an AMQP connection to check credentials
    * Registers the AMQP trigger for all types.
    """
    if not config.get_settings().amqp_enable:
        logger.debug("AMQP Triggers not enabled!")
        return False

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
