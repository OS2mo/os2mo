# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

from .. import util
from ..exceptions import ErrorCodes
from ..mapping import EventType, RequestType

logger = logging.getLogger("triggers")


def register(app):
    from mora.triggers.internal import amqp_trigger, http_trigger

    trigger_modules = [amqp_trigger, http_trigger]

    for trigger_module in trigger_modules:
        logger.debug("Registering trigger %s", trigger_module)
        try:
            trigger_module.register(app)
        except Exception:
            logger.exception("Exception during register call for %s", trigger_module)
            raise


class Trigger:
    """Trigger registry, retrieval, and decorator methods"""

    registry = {}

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
    def run(cls, trigger_dict):
        """find relevant triggers for supplied
        role type, request type, and event type
        and call each triggerfunction with the argument
        """
        # TODO: Lad return typen fra triggers ende i Arbejdsloggen?
        if util.get_args_flag("triggerless"):
            return
        triggers = (
            cls.registry.get(trigger_dict[cls.ROLE_TYPE], {})
            .get(trigger_dict[cls.REQUEST_TYPE], {})
            .get(trigger_dict[cls.EVENT_TYPE], [])
        )
        results = []
        for t in triggers:
            try:
                results.append(t(trigger_dict))
            except cls.Error as e:
                ErrorCodes.E_INTEGRATION_ERROR(str(e), **e.extra)
            except Exception as e:
                ErrorCodes.E_INTEGRATION_ERROR(str(e))
        return results

    @classmethod
    def on(cls, role_type, request_type: RequestType, event_type: EventType):
        """find relevant registry-list for supplied
        role type, request type, and event type
        then append this trigger function to the list
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
