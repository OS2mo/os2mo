# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio

import structlog
from fastramqpi.ramqp import AMQPSystem

from .types import DN

logger = structlog.stdlib.get_logger()


async def publish_dns(
    ldap_amqpsystem: AMQPSystem,
    dns: list[DN],
) -> None:
    logger.info("Registered change for LDAP object(s)", dns=dns)
    await asyncio.gather(*[ldap_amqpsystem.publish_message("dn", dn) for dn in dns])
