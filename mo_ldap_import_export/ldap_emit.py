# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio

import structlog
from fastramqpi.ramqp import AMQPSystem

from .types import LDAPUUID

logger = structlog.stdlib.get_logger()


async def publish_uuids(
    ldap_amqpsystem: AMQPSystem,
    uuids: list[LDAPUUID],
) -> None:
    if not uuids:
        return None
    logger.info("Registered change for LDAP object(s)", uuids=uuids)
    await asyncio.gather(
        *[ldap_amqpsystem.publish_message("uuid", uuid) for uuid in uuids]
    )
