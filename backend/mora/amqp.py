#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import logging

import pika

from . import settings


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


logger = logging.getLogger(__name__)


if settings.ENABLE_AMQP:
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.AMQP_HOST,
            port=settings.AMQP_PORT,
            heartbeat=0,
        )
    )
    channel = conn.channel()
    channel.exchange_declare(
        exchange=settings.AMQP_OS2MO_EXCHANGE,
        exchange_type="topic",
    )


def publish_message(service, object_type, action, service_uuid, date):
    """Send a message to the MO exchange.

    For the full documentation, refer to "AMQP Messages" in the docs.
    The source for that is in ``docs/amqp.rst``.

    Message publishing is a secondary task to writting to lora. We
    should not throw a HTTPError in the case where lora writting is
    successful, but amqp is down. Therefore, the try/except block.
    """
    if not settings.ENABLE_AMQP:
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
        channel.basic_publish(
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
