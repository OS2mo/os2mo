# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from typing import Annotated

import structlog
from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastramqpi.main import FastRAMQPI
from fastramqpi.ramqp import AMQPSystem
from fastramqpi.ramqp.amqp import Router
from fastramqpi.ramqp.depends import get_payload_as_type
from fastramqpi.ramqp.depends import rate_limit
from fastramqpi.ramqp.mo import MOAMQPSystem
from fastramqpi.ramqp.utils import RejectMessage
from fastramqpi.ramqp.utils import RequeueMessage

from . import depends
from .config import SLEEP_ON_ERROR
from .depends import DataLoader
from .depends import LDAPAMQPSystem
from .depends import Settings
from .depends import SyncTool
from .depends import logger_bound_message_id
from .depends import request_id
from .exceptions import NoObjectsReturnedException
from .exceptions import amqp_reject_on_failure
from .exceptions import http_reject_on_failure
from .types import LDAPUUID

logger = structlog.stdlib.get_logger()


ldap_amqp_router = Router()
ldap2mo_router = APIRouter(prefix="/ldap2mo")

PayloadUUID = Annotated[LDAPUUID, Depends(get_payload_as_type(LDAPUUID))]


@ldap2mo_router.post("/uuid")
@http_reject_on_failure
async def http_process_uuid(
    settings: Settings,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    uuid: Annotated[LDAPUUID, Body()],
) -> None:
    await handle_uuid(settings, sync_tool, dataloader, uuid)


@ldap_amqp_router.register("uuid")
async def process_uuid(
    settings: Settings,
    ldap_amqpsystem: LDAPAMQPSystem,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    uuid: PayloadUUID,
) -> None:
    try:
        await amqp_reject_on_failure(handle_uuid)(settings, sync_tool, dataloader, uuid)
    except RequeueMessage:  # pragma: no cover
        # NOTE: This is a hack to cycle messages because quorum queues do not work
        # NOTE: We intentionally publish to this specific queue instead of the exchange,
        #       as we may otherwise trigger both this handler AND the reconcile handler
        #       and if both handlers end up failing, we have an exponential growth in
        #       the number of unhandled messages.
        await asyncio.sleep(SLEEP_ON_ERROR)
        queue_prefix = settings.ldap_amqp.queue_prefix
        queue_name = f"{queue_prefix}_process_uuid"
        await ldap_amqpsystem.publish_message_to_queue(queue_name, uuid)


async def handle_uuid(
    settings: Settings,
    sync_tool: SyncTool,
    dataloader: DataLoader,
    uuid: LDAPUUID,
) -> None:
    logger.info("Received LDAP AMQP event", uuid=uuid)

    if uuid in settings.ldap_uuids_to_ignore:
        logger.warning("LDAP event ignored due to ignore-list", ldap_uuid=uuid)
        return

    try:
        dn = await dataloader.ldapapi.get_ldap_dn(uuid)
    except NoObjectsReturnedException as exc:
        logger.exception("LDAP UUID could not be found", uuid=uuid)
        raise RejectMessage("LDAP UUID could not be found") from exc

    # Ignore changes to non-employee objects
    ldap_object_classes = await dataloader.ldapapi.get_attribute_by_dn(
        dn, "objectClass"
    )

    # TODO: Eliminate this branch by handling employees as any other object
    employee_object_class = settings.ldap_object_class
    if employee_object_class in ldap_object_classes:
        logger.info("Handling employee", ldap_object_classes=ldap_object_classes)
        await sync_tool.import_single_user(dn)

    for object_class in settings.conversion_mapping.ldap_to_mo_any:
        if object_class in ldap_object_classes:
            logger.info(
                "Handling LDAP event",
                object_class=object_class,
                ldap_object_classes=ldap_object_classes,
            )
            await sync_tool.import_single_object_class(object_class, dn)


@ldap2mo_router.post("/reconcile")
@http_reject_on_failure
async def http_reconcile_uuid(
    settings: Settings,
    dataloader: DataLoader,
    amqpsystem: depends.AMQPSystem,
    uuid: Annotated[LDAPUUID, Body()],
) -> None:
    await handle_ldap_reconciliation(settings, dataloader, amqpsystem, uuid)


@ldap_amqp_router.register("uuid")
async def reconcile_uuid(
    settings: Settings,
    ldap_amqpsystem: LDAPAMQPSystem,
    dataloader: DataLoader,
    amqpsystem: depends.AMQPSystem,
    uuid: PayloadUUID,
) -> None:
    try:
        await amqp_reject_on_failure(handle_ldap_reconciliation)(
            settings, dataloader, amqpsystem, uuid
        )
    except RequeueMessage:  # pragma: no cover
        # NOTE: This is a hack to cycle messages because quorum queues do not work
        # NOTE: We intentionally publish to this specific queue instead of the exchange,
        #       as we may otherwise trigger both this handler AND the reconcile handler
        #       and if both handlers end up failing, we have an exponential growth in
        #       the number of unhandled messages.
        await asyncio.sleep(SLEEP_ON_ERROR)
        queue_prefix = settings.ldap_amqp.queue_prefix
        queue_name = f"{queue_prefix}_reconcile_uuid"
        await ldap_amqpsystem.publish_message_to_queue(queue_name, uuid)


async def handle_ldap_reconciliation(
    settings: Settings,
    dataloader: DataLoader,
    amqpsystem: MOAMQPSystem,
    uuid: LDAPUUID,
) -> None:
    logger.info("Received LDAP AMQP event (Reconcile)", uuid=uuid)

    if uuid in settings.ldap_uuids_to_ignore:
        logger.warning("LDAP event ignored due to ignore-list", ldap_uuid=uuid)
        return

    try:
        dn = await dataloader.ldapapi.get_ldap_dn(uuid)
    except NoObjectsReturnedException as exc:
        logger.exception("LDAP UUID could not be found", uuid=uuid)
        raise RejectMessage("LDAP UUID could not be found") from exc

    person_uuid = await dataloader.find_mo_employee_uuid(dn)
    if person_uuid is None:
        return
    # We handle reconciliation by seeding events into the normal processing queue
    queue_prefix = settings.fastramqpi.amqp.queue_prefix
    queue_name = f"{queue_prefix}_process_person"
    await amqpsystem.publish_message_to_queue(queue_name, person_uuid)  # type: ignore


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
