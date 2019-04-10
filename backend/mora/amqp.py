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


logger = logging.getLogger(__name__)


if settings.ENABLE_AMQP:
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.AMQP_HOST,
            port=settings.AMQP_PORT,
        )
    )
    channel = conn.channel()
    channel.exchange_declare(
        exchange=settings.AMQP_MO_EXCHANGE,
        exchange_type="topic",
    )


def publish_message(domain, object_type, action, domain_uuid, date):
    """Send a message to the MO exchange.

    For the full documentation, refer to "AMQP Messages" in the docs.
    The source for that is in ``docs/amqp.rst``.

    Message publishing is a secondary task to writting to lora. We
    should not throw a HTTPError in the case where lora writting is
    successful, but amqp is down. Therefore, the try/except block.
    """
    if not settings.ENABLE_AMQP:
        return

    topic = "{}.{}.{}".format(domain, object_type, action)
    message = {
        "uuid": domain_uuid,
        "time": date.isoformat(),
    }

    try:
        channel.publish(
            exchange=settings.AMQP_MO_EXCHANGE,
            routing_key=topic,
            body=json.dumps(message),
        )
    except pika.AMQPError:
        logger.error(
            "Failed to publish message. Topic: %r, body: %r",
            topic,
            body,
            exc_info=True,
        )
