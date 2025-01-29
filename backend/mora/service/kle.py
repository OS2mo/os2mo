# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid

from fastapi import APIRouter

from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..triggers import Trigger
from . import handlers
from . import org
from .validation import validator

router = APIRouter()


class KLERequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.KLE
    function_key = mapping.KLE_KEY

    async def prepare_create(self, req):
        org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT, required=False)

        valid_from, valid_to = util.get_validities(req)

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        kle_aspects = util.checked_get(
            req, mapping.KLE_ASPECT, [], required=True, can_be_empty=False
        )

        opgaver = [{"uuid": util.get_uuid(kle_type)} for kle_type in kle_aspects]

        kle_annotation_uuid = util.get_mapping_uuid(
            req, mapping.KLE_NUMBER, required=True
        )

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        # Validation
        if org_unit_uuid:
            await validator.is_date_range_in_org_unit_range(
                req[mapping.ORG_UNIT], valid_from, valid_to
            )

        func = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.KLE_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            funktionstype=kle_annotation_uuid,
            tilknyttedebrugere=[],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid],
            opgaver=opgaver,
        )

        self.payload = func
        self.uuid = func_id
        self.trigger_dict.update({Trigger.ORG_UNIT_UUID: org_unit_uuid})

    async def prepare_edit(self, req: dict):
        function_uuid = util.get_uuid(req)

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=function_uuid)

        if not original:
            exceptions.ErrorCodes.E_NOT_FOUND()

        # Get org unit uuid for validation purposes
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original)

        data = req.get("data")
        new_from, new_to = util.get_validities(data)

        payload = {
            "note": "Rediger KLE",
        }

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

        update_fields = [
            # Always update gyldighed
            (mapping.ORG_FUNK_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}),
        ]

        if mapping.ORG_UNIT in data:
            org_unit_uuid = util.get_mapping_uuid(data, mapping.ORG_UNIT)

            update_fields.append(
                (
                    mapping.ASSOCIATED_ORG_UNIT_FIELD,
                    {
                        "uuid": org_unit_uuid,
                    },
                )
            )

        for aspect in util.checked_get(
            data, mapping.KLE_ASPECT, [], can_be_empty=False
        ):
            update_fields.append(
                (
                    mapping.KLE_ASPECT_FIELD,
                    {
                        "uuid": util.get_uuid(aspect),
                    },
                )
            )

        if mapping.KLE_NUMBER in data:
            update_fields.append(
                (
                    mapping.ORG_FUNK_TYPE_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.KLE_NUMBER),
                    },
                )
            )

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

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.KLE_FIELDS.difference(
                {x[0] for x in update_fields},
            )
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )

        self.payload = payload
        self.uuid = function_uuid
        self.trigger_dict.update(
            {
                Trigger.ORG_UNIT_UUID: org_unit_uuid,
            }
        )
