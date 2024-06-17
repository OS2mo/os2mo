# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import Depends
from fastramqpi.main import FastRAMQPI
from fastramqpi.ramqp import AMQPSystem
from fastramqpi.ramqp.amqp import Router
from fastramqpi.ramqp.depends import get_payload_as_type
from fastramqpi.ramqp.depends import rate_limit
from fastramqpi.ramqp.utils import RejectMessage
from fastramqpi.ramqp.utils import RequeueMessage

from .config import LDAPAMQPConnectionSettings
from .depends import DataLoader
from .depends import LDAPAMQPSystem
from .depends import logger_bound_message_id
from .depends import request_id
from .depends import SyncTool
from .exceptions import NoObjectsReturnedException
from .ldap_emit import publish_uuid
from .types import DN

logger = structlog.stdlib.get_logger()


ldap_amqp_router = Router()

# Try errors again after a short period of time
delay_on_error = 10

PayloadDN = Annotated[DN, Depends(get_payload_as_type(DN))]
PayloadUUID = Annotated[UUID, Depends(get_payload_as_type(UUID))]


# TODO: Eliminate this and publish_dns
@ldap_amqp_router.register("dn")
async def process_dn(
    ldap_amqpsystem: LDAPAMQPSystem,
    dataloader: DataLoader,
    dn: PayloadDN,
) -> None:
    logger.info("Received LDAP AMQP event", dn=dn)
    try:
        uuid = await dataloader.get_ldap_unique_ldap_uuid(dn)
    except NoObjectsReturnedException as exc:
        logger.exception("DN could not be found", dn=dn)
        raise RejectMessage("DN could not be found") from exc

    await publish_uuid(ldap_amqpsystem, [uuid])


@ldap_amqp_router.register("uuid")
async def process_uuid(
    sync_tool: SyncTool,
    dataloader: DataLoader,
    uuid: PayloadUUID,
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
    except Exception as exc:
        logger.exception("Unable to synchronize DN to MO", dn=dn, uuid=uuid)
        raise RequeueMessage("Unable to synchronize DN to MO") from exc


def configure_ldap_amqpsystem(
    fastramqpi: FastRAMQPI, settings: LDAPAMQPConnectionSettings, priority: int
) -> None:
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
    # Needs to run after SyncTool
    # TODO: Implement a dependency graph?
    fastramqpi.add_lifespan_manager(ldap_amqpsystem, priority)
    ldap_amqpsystem.router.registry.update(ldap_amqp_router.registry)
    ldap_amqpsystem.context = fastramqpi._context
