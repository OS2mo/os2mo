#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import logging
import json
import pika
from mora import exceptions
from mora import util
from mora import mapping
from mora.triggers import Trigger
from mora.service.handlers import RequestType

logger = logging.getLogger("amqp")
amqp_connection = {}

_SERVICES = ("employee", "org_unit")
_OBJECT_TYPES = (
    "address",
    "association",
    "employee",
    "engagement",
    "it",
    "leave",
    "manager",
    "org_unit",
    "related_unit",
    "role",
)
_ACTIONS = ("create", "delete", "update")


def publish_message(service, object_type, action, service_uuid, date):
    """Send a message to the MO exchange.

    For the full documentation, refer to "AMQP Messages" in the docs.
    The source for that is in ``docs/amqp.rst``.

    Message publishing is a secondary task to writting to lora. We
    should not throw a HTTPError in the case where lora writting is
    successful, but amqp is down. Therefore, the try/except block.
    """
    if not amqp_connection:
        return

    # we are strict about the topic format to avoid programmer errors.
    if service not in _SERVICES:
        raise ValueError("service {!r} not allowed, use one of {!r}".format(
                         service, _SERVICES))
    if object_type not in _OBJECT_TYPES:
        raise ValueError(
            "object_type {!r} not allowed, use one of {!r}".format(
                object_type, _OBJECT_TYPES))
    if action not in _ACTIONS:
        raise ValueError("action {!r} not allowed, use one of {!r}".format(
                         action, _ACTIONS))

    topic = "{}.{}.{}".format(service, object_type, action)
    message = {
        "uuid": service_uuid,
        "time": date.isoformat(),
    }

    try:
        amqp_connection["channel"].basic_publish(
            exchange=settings.AMQP_OS2MO_EXCHANGE,
            routing_key=topic,
            body=json.dumps(message),
        )
    except pika.exceptions.AMQPError:
        logger.error(
            "Failed to publish message. Topic: %r, body: %r",
            topic,
            message,
            exc_info=True,
        )


def amqp_sender(trigger_dict):
    request = trigger_dict["request"]
    if trigger_dict["request_type"] == RequestType.EDIT:
        request = request['data']

    try:  # date = from or to
        date = util.get_valid_from(request)
    except exceptions.HTTPException:
        date = util.get_valid_to(request)
    action = {
        RequestType.CREATE: "create",
        RequestType.EDIT: "update",
        RequestType.TERMINATE: "delete",
    }[trigger_dict["request_type"]]

    amqp_messages = []

    if trigger_dict.get("employee_uuid"):
        amqp_messages.append((
            'employee',
            trigger_dict["role_type"],
            action,
            trigger_dict["employee_uuid"],
            date
        ))

    if trigger_dict.get("org_unit_uuid"):
        amqp_messages.append((
            'org_unit',
            trigger_dict["role_type"],
            action,
            trigger_dict["org_unit_uuid"],
            date
        ))

    for message in amqp_messages:
        publish_message(*message)


def register(app):
    """ Register amqp triggers on:
        any ROLE_TYPE
        any RequestType
        but only after submit (ON_AFTER)
    """
    if app.config.get("ENABLE_AMQP"):
        # we cant bail out here, as it seems amqp trigger
        # tests must be able to run without ENABLE_AMQP
        # instead we leave the connection object empty
        # in which case publish_message will bail out
        # this is the original mode of operation restored

        conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=app.config["AMQP_HOST"],
                port=app.config["AMQP_PORT"],
                heartbeat=0,
            )
        )
        channel = conn.channel()
        channel.exchange_declare(
            exchange=app.config["AMQP_OS2MO_EXCHANGE"],
            exchange_type="topic",
        )

        amqp_connection.update({
            "conn": conn,
            "channel": channel,
        })

    ROLE_TYPES = [
        mapping.ORG_UNIT,
        mapping.EMPLOYEE,
        *mapping.RELATION_TRANSLATIONS.keys(),
    ]

    trigger_combinations = [
        (role_type, request_type, Trigger.Event.ON_AFTER)
        for role_type in ROLE_TYPES
        for request_type in RequestType
    ]

    for combi in trigger_combinations:
        Trigger.on(*combi)(amqp_sender)
