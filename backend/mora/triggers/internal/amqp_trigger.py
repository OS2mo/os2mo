# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json

import pika
from structlog import get_logger

from mora import config
from mora import exceptions
from mora import mapping
from mora import triggers
from mora import util

logger = get_logger()
_amqp_connection = {}

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
_ACTIONS = ("create", "delete", "update", "refresh")


def publish_message(service, object_type, action, service_uuid, date):
    """Send a message to the MO exchange.

    For the full documentation, refer to "AMQP Messages" in the docs.
    The source for that is in ``docs/amqp.rst``.

    Message publishing is a secondary task to writting to lora. We
    should not throw a HTTPError in the case where lora writting is
    successful, but amqp is down. Therefore, the try/except block.
    """

    if not config.get_settings().amqp_enable:
        return

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
        "time": date.isoformat(),
    }

    connection = get_connection()

    try:
        connection["channel"].basic_publish(
            exchange=config.get_settings().amqp_os2mo_exchange,
            routing_key=topic,
            body=json.dumps(message),
        )
    except pika.exceptions.AMQPError:
        logger.error(
            "Failed to publish AMQP message",
            topic=topic,
            message=message,
            exc_info=True,
        )


def amqp_sender(trigger_dict):
    request = trigger_dict[triggers.Trigger.REQUEST]
    if trigger_dict[triggers.Trigger.REQUEST_TYPE] == mapping.RequestType.EDIT:
        request = request["data"]

    try:  # date = from or to
        date = util.get_valid_from(request)
    except exceptions.HTTPException:
        date = util.get_valid_to(request)
    action = {
        mapping.RequestType.CREATE: "create",
        mapping.RequestType.EDIT: "update",
        mapping.RequestType.TERMINATE: "delete",
        mapping.RequestType.REFRESH: "refresh",
    }[trigger_dict[triggers.Trigger.REQUEST_TYPE]]

    amqp_messages = []

    if trigger_dict.get(triggers.Trigger.EMPLOYEE_UUID):
        amqp_messages.append(
            (
                "employee",
                trigger_dict[triggers.Trigger.ROLE_TYPE],
                action,
                trigger_dict[triggers.Trigger.EMPLOYEE_UUID],
                date,
            )
        )

    if trigger_dict.get(triggers.Trigger.ORG_UNIT_UUID):
        amqp_messages.append(
            (
                "org_unit",
                trigger_dict[triggers.Trigger.ROLE_TYPE],
                action,
                trigger_dict[triggers.Trigger.ORG_UNIT_UUID],
                date,
            )
        )

    for message in amqp_messages:
        publish_message(*message)


def get_connection():
    # we cant bail out here, as it seems amqp trigger
    # tests must be able to run without ENABLE_AMQP
    # instead we leave the connection object empty
    # in which case publish_message will bail out
    # this is the original mode of operation restored

    # Please crash if rabbitmq is unavailable.
    if not _amqp_connection:
        conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.get_settings().amqp_host,
                port=config.get_settings().amqp_port,
                heartbeat=0,
            )
        )
        channel = conn.channel()
        channel.exchange_declare(
            exchange=config.get_settings().amqp_os2mo_exchange,
            exchange_type="topic",
        )

        _amqp_connection.update(
            {
                "conn": conn,
                "channel": channel,
            }
        )

    return _amqp_connection


def register(app):
    """Register amqp triggers on:
    any ROLE_TYPE
    any RequestType
    but only after submit (ON_AFTER)
    """
    ROLE_TYPES = [
        mapping.EMPLOYEE,
        mapping.ORG_UNIT,
        *mapping.RELATION_TRANSLATIONS.keys(),
    ]

    trigger_combinations = [
        (role_type, request_type, mapping.EventType.ON_AFTER)
        for role_type in ROLE_TYPES
        for request_type in mapping.RequestType
    ]

    for combi in trigger_combinations:
        triggers.Trigger.on(*combi)(amqp_sender)
