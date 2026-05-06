# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Leave
-----

This section describes how to interact with employee leave.

"""

import uuid

from .. import common
from .. import lora
from .. import mapping
from .. import util
from ..triggers import Trigger
from . import handlers
from . import org
from .validation import validator


class LeaveRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.LEAVE
    function_key = mapping.LEAVE_KEY

    async def prepare_create(self, req):
        employee = util.checked_get(req, mapping.PERSON, {}, required=True)
        employee_uuid = util.get_uuid(employee, required=True)

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        leave_type_uuid = util.get_mapping_uuid(req, mapping.LEAVE_TYPE, required=True)

        engagement_uuid = util.get_mapping_uuid(req, mapping.ENGAGEMENT)
        valid_from, valid_to = util.get_validities(req)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        # Validation
        await validator.is_date_range_in_employee_range(employee, valid_from, valid_to)
        await validator.does_employee_have_active_engagement(
            employee_uuid, valid_from, valid_to
        )

        leave = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.LEAVE_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[employee_uuid],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedefunktioner=[engagement_uuid],
            funktionstype=leave_type_uuid,
        )

        self.payload = leave
        self.uuid = func_id
        self.trigger_dict[Trigger.EMPLOYEE_UUID] = employee_uuid

    async def prepare_edit(self, req: dict):
        leave_uuid = req.get("uuid")
        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=leave_uuid)

        data = req.get("data")
        new_from, new_to = util.get_validities(data)

        payload = {"note": "Rediger orlov"}

        original_data = req.get("original")
        if original_data:  # pragma: no cover
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from,
                old_to,
                new_from,
                new_to,
                payload,
                ("tilstande", "organisationfunktiongyldighed"),
            )

        update_fields = []

        # Always update gyldighed
        update_fields.append((mapping.ORG_FUNK_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}))

        try:
            attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):  # pragma: no cover
            attributes = {}
        new_attributes = {}

        if mapping.USER_KEY in data:
            new_attributes["brugervendtnoegle"] = util.checked_get(
                data, mapping.USER_KEY, ""
            )

        if new_attributes:
            update_fields.append(
                (
                    mapping.ORG_FUNK_EGENSKABER_FIELD,
                    {**attributes, **new_attributes},
                )
            )

        if mapping.LEAVE_TYPE in data:
            update_fields.append(
                (
                    mapping.ORG_FUNK_TYPE_FIELD,
                    {"uuid": util.get_mapping_uuid(data, mapping.LEAVE_TYPE)},
                )
            )

        if mapping.ENGAGEMENT in data:
            update_fields.append(
                (
                    mapping.ASSOCIATED_FUNCTION_FIELD,
                    {"uuid": util.get_mapping_uuid(data, mapping.ENGAGEMENT)},
                )
            )

        if mapping.PERSON in data:
            employee = data.get(mapping.PERSON)
            employee_uuid = util.get_mapping_uuid(data, mapping.PERSON)

            update_fields.append(
                (
                    mapping.USER_FIELD,
                    {"uuid": employee_uuid},
                )
            )
        else:
            employee = util.get_obj_value(original, mapping.USER_FIELD.path)[-1]
            employee_uuid = util.get_obj_uuid(original, mapping.USER_FIELD.path)

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.LEAVE_FIELDS.difference({x[0] for x in update_fields})
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )

        await validator.is_date_range_in_employee_range(employee, new_from, new_to)

        await validator.does_employee_have_active_engagement(
            employee_uuid, new_from, new_to
        )

        self.payload = payload
        self.uuid = leave_uuid
        self.trigger_dict[Trigger.EMPLOYEE_UUID] = employee_uuid
