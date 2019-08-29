#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import enum
import logging
import importlib
import traceback
import functools

logger = logging.getLogger("triggers")


def register(app):
    for m in app.config.get("TRIGGER_MODULES", []):
        try:
            trigger_module = importlib.import_module(m)
            trigger_module.register(app)
        except Exception:
            logger.error("trigger code or registration error for %s", m)
            raise


class Trigger:
    """ Trigger registry, retrieval, and decorator methods
    """
    registry = {}

    @enum.unique
    class Event(enum.Enum):
        """ EventType for trigger registry
        """
        ON_BEFORE, ON_AFTER = range(2)

    @classmethod
    def run(cls, trigger_dict):
        """find relevant triggers for supplied
        role type, request type, and event type
        and call each triggerfunction with the argument
        """
        triggers = cls.registry.get(
            trigger_dict["role_type"], {}
        ).get(
            trigger_dict["request_type"], {}
        ).get(
            trigger_dict["event_type"], []
        )
        for t in triggers:
            t(trigger_dict)

    @classmethod
    def on(cls, role_type, request_type, event_type):
        """find relevant registry-list for supplied
        role type, request type, and event type
        then append this trigger function to the list
        """
        registry = cls.registry.setdefault(
            role_type, {}
        ).setdefault(
            request_type, {}
        ).setdefault(
            event_type, []
        )

        def decorator(function):
            "ensure function in registry"
            if function not in registry:
                registry.append(function)

            @functools.wraps(function)
            def wrapper(trigger_dict):
                "call wrapped function with arg"
                return function(trigger_dict)
            return wrapper
        return decorator
