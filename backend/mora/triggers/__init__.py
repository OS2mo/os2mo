# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any

from structlog import get_logger

from ..exceptions import ErrorCodes
from ..mapping import EventType
from ..mapping import RequestType

logger = get_logger()


async def register(app):
    """Call register on our internal trigger modules."""
    from mora.triggers.internal import amqp_trigger
    from mora.triggers.internal import http_trigger

    trigger_modules = [amqp_trigger, http_trigger]

    for trigger_module in trigger_modules:
        logger.debug("Registering trigger", trigger_module=trigger_module)
        try:
            await trigger_module.register(app)
        except Exception:  # pragma: no cover
            logger.exception(
                "Exception during register call", trigger_module=trigger_module
            )
            raise


class Trigger:
    """Trigger registry, retrieval, and decorator methods"""

    registry: dict[
        str,
        dict[
            RequestType,
            dict[
                EventType,
                set[
                    # TODO: Replace dict[str, Any] with MOTriggerPayload
                    Callable[[dict[str, Any]], None]
                ],
            ],
        ],
    ] = {}

    class Error(Exception):
        def __init__(self, message, **extra):
            super().__init__(message)
            self.extra = extra

    # mapping
    EMPLOYEE_UUID = "employee_uuid"
    ORG_UNIT_UUID = "org_unit_uuid"
    UUID = "uuid"
    ROLE_TYPE = "role_type"
    REQUEST_TYPE = "request_type"
    EVENT_TYPE = "event_type"
    REQUEST = "request"
    RESULT = "result"

    @classmethod
    async def run(cls, trigger_dict):
        """Find the relevant set of trigger functions and trigger them in turn.

        The relevant set is found by lookup into the registry using role, request and
        event-type.
        """
        triggers = (
            cls.registry.get(trigger_dict[cls.ROLE_TYPE], {})
            .get(trigger_dict[cls.REQUEST_TYPE], {})
            .get(trigger_dict[cls.EVENT_TYPE], set())
        )
        results = []
        for t in triggers:
            try:
                results.append(await t(trigger_dict))
            except cls.Error as e:
                ErrorCodes.E_INTEGRATION_ERROR(str(e), **e.extra)
            except Exception as e:
                ErrorCodes.E_INTEGRATION_ERROR(str(e))
        return results

    @classmethod
    def on(cls, role_type: str, request_type: RequestType, event_type: EventType):
        """Add the decorated trigger function to relevant set of functions.

        The relevant set is found by lookup into the registry using role, request and
        event-type.
        """
        assert request_type in RequestType
        assert event_type in EventType

        registry = (
            cls.registry.setdefault(role_type, {})
            .setdefault(request_type, {})
            .setdefault(event_type, set())
        )

        def decorator(function):
            "ensure function in registry"
            registry.add(function)
            return function

        return decorator
