#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json

from .settings import (
    ENABLE_AMQP_MESSAGES,
    AMQP_MO_EXCHANGE,
    AMQP_HOST,
    AMQP_PORT,
)


if ENABLE_AMQP_MESSAGES:
    import pika
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(host=AMQP_HOST, port=AMQP_PORT)
    )
    channel = conn.channel()
    channel.exchange_declare(exchange=AMQP_MO_EXCHANGE, exchange_type="topic")


def publish_message(domain, action, object_type, domain_uuid, date):
    """Send a message to the MO exchange.

    For the full documentation, refer to "AMQP Messages" in the docs.
    The source for that is in ``docs/amqp.rst``.
    """
    if not ENABLE_AMQP_MESSAGES:
        return

    topic = "%s.%s.%s" % (domain, action, object_type)
    message = {
        "uuid": domain_uuid,
        "time": date.isoformat(),
    }

    channel.publish(
        exchange=AMQP_MO_EXCHANGE,
        routing_key=topic,
        body=json.dumps(message),
    )
