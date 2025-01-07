# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
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
from fastramqpi.ramqp.utils import RequeueMessage

from .depends import DataLoader
from .depends import LDAPAMQPSystem
from .depends import LdapConverter
from .depends import Settings
from .depends import SyncTool
from .depends import logger_bound_message_id
from .depends import request_id
from .exceptions import NoObjectsReturnedException
from .exceptions import amqp_reject_on_failure
from .exceptions import http_reject_on_failure
from .ldap import get_ldap_object
from .ldap_emit import publish_uuids

logger = structlog.stdlib.get_logger()


ldap_amqp_router = Router()
ldap2mo_router = APIRouter(prefix="/ldap2mo")

PayloadUUID = Annotated[UUID, Depends(get_payload_as_type(UUID))]


@ldap2mo_router.post("/uuid")
@http_reject_on_failure
async def http_process_uuid(
    settings: Settings,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    converter: LdapConverter,
    uuid: Annotated[UUID, Body()],
) -> None:
    await handle_uuid(settings, sync_tool, dataloader, converter, uuid)


@ldap_amqp_router.register("uuid")
async def process_uuid(
    settings: Settings,
    ldap_amqpsystem: LDAPAMQPSystem,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    converter: LdapConverter,
    uuid: PayloadUUID,
) -> None:
    try:
        await amqp_reject_on_failure(handle_uuid)(
            settings, sync_tool, dataloader, converter, uuid
        )
    except RequeueMessage:  # pragma: no cover
        # NOTE: This is a hack to cycle messages because quorum queues do not work
        await asyncio.sleep(30)
        await publish_uuids(ldap_amqpsystem, [uuid])


async def handle_uuid(
    settings: Settings,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    converter: LdapConverter,
    uuid: UUID,
) -> None:
    # TODO: Sync from MO to LDAP to overwrite bad manual changes

    logger.info("Received LDAP AMQP event", uuid=uuid)

    if uuid in settings.ldap_uuids_to_ignore:  # pragma: no cover
        logger.warning("LDAP event ignored due to ignore-list", ldap_uuid=uuid)
        return

    try:
        dn = await dataloader.ldapapi.get_ldap_dn(uuid)
    except NoObjectsReturnedException as exc:
        logger.exception("LDAP UUID could not be found", uuid=uuid)
        raise RejectMessage("LDAP UUID could not be found") from exc

    # Ignore changes to non-employee objects
    ldap_object = await get_ldap_object(
        dataloader.ldapapi.ldap_connection, dn, attributes=["objectClass"]
    )
    ldap_object_classes = ldap_object.objectClass  # type: ignore[attr-defined]
    employee_object_class = converter.settings.ldap_object_class
    if employee_object_class not in ldap_object_classes:
        logger.info(
            "Ignoring change: not Employee objectClass",
            ldap_object_classes=ldap_object_classes,
        )
        return

    await sync_tool.import_single_user(dn)


def configure_ldap_amqpsystem(fastramqpi: FastRAMQPI, settings: Settings) -> AMQPSystem:
    logger.info("Initializing LDAP AMQP system")
    ldap_amqpsystem = AMQPSystem(
        settings=settings.ldap_amqp,
        router=ldap_amqp_router,
        dependencies=[
            Depends(rate_limit(10)),
            Depends(logger_bound_message_id),
            Depends(request_id),
        ],
    )
    fastramqpi.add_context(ldap_amqpsystem=ldap_amqpsystem)
    if settings.listen_to_changes_in_ldap:
        ldap_amqpsystem.router.registry.update(ldap_amqp_router.registry)
    ldap_amqpsystem.context = fastramqpi._context
    return ldap_amqpsystem
