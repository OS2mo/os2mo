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
from ..util import ensure_list
from . import facet
from . import handlers
from . import org
from .address_handler import base
from .validation import validator

router = APIRouter()


class AddressRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.ADDRESS
    function_key = mapping.ADDRESS_KEY

    async def prepare_create(self, req):
        org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT, required=False)

        employee_uuid = util.get_mapping_uuid(req, mapping.PERSON, required=False)

        engagement_uuid = util.get_mapping_uuid(req, mapping.ENGAGEMENT, required=False)
        it_user_uuid = util.get_mapping_uuid(req, mapping.IT, required=False)

        tilknyttedefunktioner = []
        if engagement_uuid:
            tilknyttedefunktioner.append(
                common.associated_orgfunc(
                    uuid=engagement_uuid, orgfunc_type=mapping.MoOrgFunk.ENGAGEMENT
                )
            )
        if it_user_uuid:
            tilknyttedefunktioner.append(
                common.associated_orgfunc(
                    uuid=it_user_uuid, orgfunc_type=mapping.MoOrgFunk.IT
                )
            )

        number_of_uuids = len(
            list(
                filter(
                    lambda x: x is not None,
                    [org_unit_uuid, employee_uuid],
                )
            )
        )

        if number_of_uuids != 1:
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                f"Must supply exactly one {mapping.ORG_UNIT} or {mapping.PERSON} UUID",
                obj=req,
            )

        valid_from, valid_to = util.get_validities(req)

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        address_type_uuid = util.get_mapping_uuid(
            req, mapping.ADDRESS_TYPE, required=True
        )

        c = lora.Connector()
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        type_obj = await facet.get_one_class(
            c, address_type_uuid, only_primary_uuid=only_primary_uuid
        )

        scope = util.checked_get(type_obj, "scope", "", required=True)

        handler = await base.get_handler_for_scope(scope).from_request(req)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = req.get("user_key") or handler.name or func_id

        # Validation
        if org_unit_uuid:
            await validator.is_date_range_in_org_unit_range(
                req[mapping.ORG_UNIT], valid_from, valid_to
            )

        if employee_uuid:
            await validator.is_date_range_in_employee_range(
                req[mapping.PERSON], valid_from, valid_to
            )

        lora_addr = handler.get_lora_address()
        addresses = ensure_list(lora_addr)

        func = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ADDRESS_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            funktionstype=address_type_uuid,
            adresser=addresses,
            tilknyttedebrugere=[employee_uuid] if employee_uuid else [],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid] if org_unit_uuid else [],
            tilknyttedefunktioner=tilknyttedefunktioner,
            opgaver=handler.get_lora_properties(),
        )

        self.payload = func
        self.uuid = func_id
        self.trigger_dict.update(
            {Trigger.EMPLOYEE_UUID: employee_uuid, Trigger.ORG_UNIT_UUID: org_unit_uuid}
        )

    async def prepare_edit(self, req: dict):
        function_uuid = util.get_uuid(req)

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=function_uuid)

        if not original:
            exceptions.ErrorCodes.E_NOT_FOUND()

        # Get org unit uuid for validation purposes
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original)

        # Get employee uuid for validation purposes
        employee_uuid = mapping.USER_FIELD.get_uuid(original)

        data = req.get("data")
        new_from, new_to = util.get_validities(data)

        payload = {
            "note": "Rediger Adresse",
        }

        number_of_uuids = len(
            list(
                filter(
                    lambda x: x is not None,
                    [
                        data.get(mapping.PERSON),
                        data.get(mapping.ORG_UNIT),
                    ],
                )
            )
        )

        if number_of_uuids > 1:
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                f"Must supply at most one of {mapping.ORG_UNIT} or {mapping.PERSON} UUID",
                obj=req,
            )

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

        if mapping.PERSON in data:
            employee_uuid = util.get_mapping_uuid(data, mapping.PERSON)
            update_fields.append(
                (
                    mapping.USER_FIELD,
                    {
                        "uuid": employee_uuid,
                    },
                )
            )

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

        if mapping.ENGAGEMENT in data:
            update_fields.append(
                (
                    mapping.ASSOCIATED_FUNCTION_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.ENGAGEMENT),
                        mapping.OBJECTTYPE: mapping.ENGAGEMENT,
                    },
                )
            )

        if mapping.IT in data:
            update_fields.append(
                (
                    mapping.ASSOCIATED_FUNCTION_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.IT),
                        mapping.OBJECTTYPE: mapping.IT,
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

        if mapping.VALUE in data:
            address_type_uuid = util.get_mapping_uuid(
                data, mapping.ADDRESS_TYPE, required=True
            )
            only_primary_uuid = util.get_args_flag("only_primary_uuid")

            type_obj = await facet.get_one_class(
                c, address_type_uuid, only_primary_uuid=only_primary_uuid
            )
            scope = util.checked_get(type_obj, "scope", "", required=True)

            handler = await base.get_handler_for_scope(scope).from_request(data)
            lora_addr = handler.get_lora_address()
            if isinstance(lora_addr, list):
                update_fields.extend(
                    map(lambda x: (mapping.ADDRESSES_FIELD, x), lora_addr)
                )

            else:
                update_fields.append(
                    (
                        mapping.SINGLE_ADDRESS_FIELD,
                        lora_addr,
                    )
                )

            update_fields.append(
                (mapping.ADDRESS_TYPE_FIELD, {"uuid": address_type_uuid})
            )

            for prop in handler.get_lora_properties():
                update_fields.append((mapping.VISIBILITY_FIELD, prop))

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.ADDRESS_FIELDS.difference(
                {x[0] for x in update_fields},
            )
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )
        self.payload = payload
        self.uuid = function_uuid
        self.trigger_dict.update(
            {Trigger.ORG_UNIT_UUID: org_unit_uuid, Trigger.EMPLOYEE_UUID: employee_uuid}
        )

        if employee_uuid:
            await validator.is_date_range_in_employee_range(
                {"uuid": employee_uuid}, new_from, new_to
            )
