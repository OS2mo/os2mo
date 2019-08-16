#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import logging
from mora import amqp
from mora import exceptions
from mora import util
from mora import mapping
from mora.triggers import Trigger
from mora.service.handlers import RequestType

logger = logging.getLogger("amqp")


def amqp_sender(trigger_dict):
    request = trigger_dict["request"]
    if trigger_dict["request_type"] == RequestType.EDIT:
        request = request['data']

    try:  # date = from or to
        date = util.get_valid_from(request)
    except exceptions.HTTPException:
        date = util.get_valid_to(request)
    action = {
        RequestType.CREATE: "create",
        RequestType.EDIT: "update",
        RequestType.TERMINATE: "delete",
    }[trigger_dict["request_type"]]

    amqp_messages = []

    if trigger_dict.get("employee_uuid"):
        amqp_messages.append((
            'employee',
            trigger_dict["role_type"],
            action,
            trigger_dict["employee_uuid"],
            date
        ))

    if trigger_dict.get("org_unit_uuid"):
        amqp_messages.append((
            'org_unit',
            trigger_dict["role_type"],
            action,
            trigger_dict["org_unit_uuid"],
            date
        ))

    for message in amqp_messages:
        amqp.publish_message(*message)


def register(app):
    """ Register amqp triggers on:
        any ROLE_TYPE
        any RequestType
        but only after submit (ON_AFTER)
    """

    ROLE_TYPES = [
        mapping.ORG_UNIT,
        mapping.EMPLOYEE,
        *mapping.RELATION_TRANSLATIONS.keys(),
    ]

    trigger_combinations = [
        (role_type, request_type, Trigger.Event.ON_AFTER)
        for role_type in ROLE_TYPES
        for request_type in RequestType
    ]

    for combi in trigger_combinations:
        Trigger.on(*combi)(amqp_sender)
