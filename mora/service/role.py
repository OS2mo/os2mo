# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Roles
-----

This section describes how to interact with employee roles.

"""

import uuid

from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from . import handlers
from . import org
from .validation import validator


class RoleBindingRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.ROLEBINDING
    function_key = mapping.ROLEBINDING_KEY

    async def prepare_create(self, req):
        tilknyttedeenheder = []

        org_unit = util.checked_get(req, mapping.ORG_UNIT, {})
        ituser = util.checked_get(req, mapping.IT, {}, required=True)

        valid_from, valid_to = util.get_validities(req)

        if org_unit:
            tilknyttedeenheder.append(util.get_uuid(org_unit, required=True))
            await validator.is_date_range_in_org_unit_range(
                org_unit, valid_from, valid_to
            )

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        role_uuid = util.get_mapping_uuid(req, mapping.ROLEBINDING_TYPE, required=True)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        role = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ROLEBINDING_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=tilknyttedeenheder,
            tilknyttedefunktioner=[ituser],
            funktionstype=role_uuid,
        )

        self.payload = role
        self.uuid = func_id

    async def prepare_edit(self, req: dict):
        role_uuid = req["uuid"]

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=role_uuid)

        if not original:
            exceptions.ErrorCodes.E_NOT_FOUND(uuid=role_uuid)

        data = req["data"]
        new_from, new_to = util.get_validities(data)

        payload = {"note": "Rediger rollebinding"}

        original_data = req.get("original")
        if original_data:
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
        except (TypeError, LookupError):
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

        if mapping.ROLEBINDING_TYPE in data:
            update_fields.append(
                (
                    mapping.ORG_FUNK_TYPE_FIELD,
                    {"uuid": data.get(mapping.ROLEBINDING_TYPE).get("uuid")},
                )
            )

        if mapping.ORG_UNIT in data:
            update_fields.append(
                (
                    mapping.ASSOCIATED_ORG_UNIT_FIELD,
                    {"uuid": (util.get_mapping_uuid(data, mapping.ORG_UNIT))},
                )
            )

        if mapping.IT in data:
            update_fields.append(
                (
                    mapping.ASSOCIATED_FUNCTION_FIELD,
                    {"uuid": util.get_mapping_uuid(data, mapping.IT)},
                )
            )

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.ROLE_FIELDS.difference({x[0] for x in update_fields})
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )

        self.payload = payload
        self.uuid = role_uuid
