# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastramqpi.main import FastRAMQPI
from fastramqpi.ramqp import AMQPSystem
from fastramqpi.ramqp.amqp import Router
from fastramqpi.ramqp.depends import get_payload_as_type
from fastramqpi.ramqp.depends import rate_limit
from fastramqpi.ramqp.utils import RejectMessage

from .config import LDAPAMQPConnectionSettings
from .depends import DataLoader
from .depends import LDAPAMQPSystem
from .depends import SyncTool
from .depends import logger_bound_message_id
from .depends import request_id
from .exceptions import NoObjectsReturnedException
from .exceptions import amqp_reject_on_failure
from .exceptions import http_reject_on_failure
from .ldap_emit import publish_uuids

logger = structlog.stdlib.get_logger()


ldap_amqp_router = Router()
ldap2mo_router = APIRouter(prefix="/ldap2mo")

# Try errors again after a short period of time
delay_on_error = 10

PayloadUUID = Annotated[UUID, Depends(get_payload_as_type(UUID))]


@ldap2mo_router.post("/uuid")
@http_reject_on_failure
async def http_process_uuid(
    ldap_amqpsystem: LDAPAMQPSystem,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    uuid: Annotated[UUID, Body()],
) -> None:
    await handle_uuid(ldap_amqpsystem, sync_tool, dataloader, uuid)


@ldap_amqp_router.register("uuid")
@amqp_reject_on_failure
async def process_uuid(
    ldap_amqpsystem: LDAPAMQPSystem,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    uuid: PayloadUUID,
) -> None:
    await handle_uuid(ldap_amqpsystem, sync_tool, dataloader, uuid)


async def handle_uuid(
    ldap_amqpsystem: LDAPAMQPSystem,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    uuid: UUID,
) -> None:
    # TODO: Sync from MO to LDAP to overwrite bad manual changes

    logger.info("Received LDAP AMQP event", uuid=uuid)
    try:
        dn = await dataloader.get_ldap_dn(uuid)
    except NoObjectsReturnedException as exc:
        logger.exception("LDAP UUID could not be found", uuid=uuid)
        raise RejectMessage("LDAP UUID could not be found") from exc

    try:
        await sync_tool.import_single_user(dn)
    except Exception:
        logger.exception("Unable to synchronize DN to MO", dn=dn, uuid=uuid)
        # NOTE: This is a hack to cycle messages because quorum queues do not work
        await asyncio.sleep(30)
        await publish_uuids(ldap_amqpsystem, [uuid])


def configure_ldap_amqpsystem(
    fastramqpi: FastRAMQPI, settings: LDAPAMQPConnectionSettings
) -> AMQPSystem:
    logger.info("Initializing LDAP AMQP system")
    ldap_amqpsystem = AMQPSystem(
        settings=settings,
        router=ldap_amqp_router,
        dependencies=[
            Depends(rate_limit(delay_on_error)),
            Depends(logger_bound_message_id),
            Depends(request_id),
        ],
    )
    fastramqpi.add_context(ldap_amqpsystem=ldap_amqpsystem)
    ldap_amqpsystem.router.registry.update(ldap_amqp_router.registry)
    ldap_amqpsystem.context = fastramqpi._context
    return ldap_amqpsystem
