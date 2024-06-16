# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
from uuid import UUID

import structlog
from fastramqpi.ramqp import AMQPSystem

from .types import DN

logger = structlog.stdlib.get_logger()


# TODO: Eliminate this and process_dn
async def publish_dns(
    ldap_amqpsystem: AMQPSystem,
    dns: list[DN],
) -> None:
    logger.info("Registered change for LDAP object(s)", dns=dns)
    await asyncio.gather(*[ldap_amqpsystem.publish_message("dn", dn) for dn in dns])


async def publish_uuid(
    ldap_amqpsystem: AMQPSystem,
    uuids: list[UUID],
) -> None:
    logger.info("Registered change for LDAP object(s)", uuids=uuids)
    await asyncio.gather(
        *[ldap_amqpsystem.publish_message("uuid", uuid) for uuid in uuids]
    )
