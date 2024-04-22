# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Annotated

import structlog
from fastapi import Depends
from fastramqpi.main import FastRAMQPI
from fastramqpi.ramqp import AMQPSystem
from fastramqpi.ramqp.amqp import Router
from fastramqpi.ramqp.depends import get_payload_as_type
from fastramqpi.ramqp.depends import rate_limit
from fastramqpi.ramqp.utils import RejectMessage

from .config import LDAPAMQPConnectionSettings
from .depends import logger_bound_message_id
from .depends import SyncTool
from .exceptions import NoObjectsReturnedException

logger = structlog.stdlib.get_logger()


ldap_amqp_router = Router()

# Try errors again after a short period of time
delay_on_error = 10

PayloadDN = Annotated[str, Depends(get_payload_as_type(str))]


@ldap_amqp_router.register("dn")
async def process_dn(
    sync_tool: SyncTool,
    dn: PayloadDN,
) -> None:
    # TODO: Convert payload to entityUUID / ADGUID?

    logger.info("Received LDAP AMQP event", dn=dn)
    try:
        await sync_tool.import_single_user(dn)
    except NoObjectsReturnedException as exc:
        # TODO: Stop rejecting these and actually handle it within the code
        logger.exception("Throwing away message due to bad code")
        raise RejectMessage(f"DN could not be found: {dn}") from exc


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
        ],
    )
    fastramqpi.add_context(ldap_amqpsystem=ldap_amqpsystem)
    # Needs to run after SyncTool
    # TODO: Implement a dependency graph?
    fastramqpi.add_lifespan_manager(ldap_amqpsystem, priority)
    ldap_amqpsystem.router.registry.update(ldap_amqp_router.registry)
    ldap_amqpsystem.context = fastramqpi._context
