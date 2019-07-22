#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


class Trigger:
    """ Trigger registry, retrieval, and decorator methods
    """
    registry={}

    @classmethod
    def get_triggers(cls, entity_type, request_type, event_type):
        "return a list of triggers - can be empty"
        return cls.registry.get(entity_type, {}
        ).get(request_type, {}
        ).get(event_type, []
        )

    @classmethod
    def on(cls, entity_type, request_type, event_type):
        "find relevant registry-list"
        registry = cls.registry.setdefault(entity_type, {}
        ).setdefault(request_type, {}
        ).setdefault(event_type, []
        )
        def decorator(function):
            "ensure function in registry"
            if not function in registry:
                registry.append(function)
            def wrapper(trigger_dict):
                "call wrapped function with arg"
                return function(trigger_dict)
            return wrapper
        return decorator

# current test code

@Trigger.on("orgunit","create","before")
def x(trigger_dict):
    import pprint
    pprint.pprint(trigger_dict)
    pprint.pprint(Trigger.registry)

for t in Trigger.get_triggers("orgunit","create","before"):
    t({"hello":"world"})
