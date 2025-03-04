# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from datetime import datetime
from functools import partial
from itertools import product
from typing import Literal
from uuid import UUID

from fastramqpi.ramqp import AMQPSystem
from fastramqpi.ramqp.mo import PayloadType
from structlog import get_logger

from mora import config
from mora import exceptions
from mora import mapping
from mora import triggers
from mora import util
from mora.graphapi.versions.latest.health import register_health_endpoint

logger = get_logger()


def to_datetime(trigger_dict: dict) -> datetime:
    request = trigger_dict[triggers.Trigger.REQUEST]
    if trigger_dict[triggers.Trigger.REQUEST_TYPE] == mapping.RequestType.EDIT:
        request = request["data"]
    try:
        return util.get_valid_from(request)
    except exceptions.HTTPException:
        return util.get_valid_to(request)


async def amqp_sender(amqp_system: AMQPSystem, trigger_dict: dict) -> None:
    object_type = trigger_dict[triggers.Trigger.ROLE_TYPE].lower()
    request_type = trigger_dict[triggers.Trigger.REQUEST_TYPE].lower()

    def dispatch(
        service_type: Literal["employee", "org_unit"], service_uuid: UUID
    ) -> None:
        routing_key = f"{service_type}.{object_type}.{request_type}"
        payload = PayloadType(
            uuid=service_uuid,
            object_uuid=UUID(trigger_dict["uuid"]),
            time=to_datetime(trigger_dict),
        )
        logger.debug(
            "Registering AMQP publish message task",
            routing_key=routing_key,
            payload=payload,
        )
        asyncio.create_task(
            amqp_system.publish_message(
                routing_key,
                # PayloadType is an Annotated type (to allow dependency injection).
                # This adds the property __orig_class__ to the dict, for some reason,
                # but only in pydantic v1.0. Remove when we get pydantic v2.0.
                payload.dict(exclude={"__orig_class__"}),
            )
        )

    if trigger_dict.get(triggers.Trigger.EMPLOYEE_UUID):
        dispatch(
            "employee",
            UUID(trigger_dict[triggers.Trigger.EMPLOYEE_UUID]),
        )

    if trigger_dict.get(triggers.Trigger.ORG_UNIT_UUID):
        dispatch(
            "org_unit",
            UUID(trigger_dict[triggers.Trigger.ORG_UNIT_UUID]),
        )


async def register(app) -> bool:
    """Register an ON_AFTER triggers for all ROLE_TYPEs and RequestTypes.

    This method:
    * Checks the configuration of the module.
    * Establishes an AMQP connection to check credentials
    * Registers the AMQP trigger for all types.
    """
    settings = config.get_settings()
    if not settings.amqp_enable:
        logger.debug("AMQP Triggers not enabled!")
        return False

    # Start AMQP system
    amqp_system = AMQPSystem(settings.amqp)
    await amqp_system.start()

    # Register healthcheck
    @register_health_endpoint
    async def amqp() -> bool | None:
        """Check if AMQP connection is open.

        Returns:
            Optional[bool]: True if open, False if not open or an error occurs.
                None if AMQP support is disabled.
        """
        if not config.get_settings().amqp_enable:  # pragma: no cover
            return None

        return amqp_system.healthcheck()

    # Register trigger on everything
    ROLE_TYPES = [
        mapping.EMPLOYEE,
        mapping.ORG_UNIT,
        *mapping.RELATION_TRANSLATIONS.keys(),
    ]
    trigger_combinations = product(
        ROLE_TYPES, mapping.RequestType, [mapping.EventType.ON_AFTER]
    )
    sender = partial(amqp_sender, amqp_system)
    for combi in trigger_combinations:
        triggers.Trigger.on(*combi)(sender)
    return True
