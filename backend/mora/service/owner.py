# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

"""Owner
-------

This section describes how to interact with owners.

"""
import uuid
from datetime import datetime
from typing import Any, Dict, NoReturn, Optional, Tuple

import mora.async_util

from .. import common, lora, mapping, util
from ..common import parse_owner_inference_priority_str
from ..exceptions import ErrorCodes
from ..mapping import OwnerInferencePriority
from ..triggers import Trigger
from . import handlers, org
from .validation import validator


class OwnerRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.OWNER
    function_key = mapping.OWNER

    @staticmethod
    def raise_unexpected_input(obj: Dict) -> NoReturn:
        """
        tiny wrapper, just convenience
        :param obj: used to construct error msg, could be e.g. received request
        :return:
        """
        raise ErrorCodes.E_INVALID_INPUT(
            f"Must supply at most one of {mapping.ORG_UNIT} UUID, "
            f"{mapping.PERSON} UUID",
            obj=obj,
        )

    def extract_info_owner_info(
        self, req
    ) -> Tuple[
        Optional[Dict[str, Any]],
        Optional[Dict[str, Any]],
        Optional[Dict[str, Any]],
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[OwnerInferencePriority],
    ]:
        """
        Parsing owner-spec
        :param req: Specification of an owner
        :return: Tuple of essential values, parsed from req
        """
        org_unit = util.checked_get(req, mapping.ORG_UNIT, {}, required=False)
        org_unit_uuid = util.get_uuid(org_unit, required=False)

        owned_person = util.checked_get(req, mapping.PERSON, {}, required=False)
        owned_person_uuid = util.get_uuid(owned_person, required=False)

        owner = util.checked_get(req, mapping.OWNER, {}, required=False)
        owner_uuid = util.get_uuid(owner, required=False)

        if not (bool(owned_person_uuid) ^ bool(org_unit_uuid)):  # xor
            self.raise_unexpected_input(req)

        inference_priority_str = req.get(mapping.OWNER_INFERENCE_PRIORITY, None)
        inference_priority = None
        if inference_priority_str is not None:
            if owned_person_uuid is None:
                raise ErrorCodes.E_INVALID_INPUT(
                    f"When {mapping.OWNER_INFERENCE_PRIORITY} is filled, "
                    f"{mapping.PERSON} is required and missing!",
                    obj=req,
                )

            if owner_uuid is not None:
                raise ErrorCodes.E_INVALID_INPUT(
                    f"Cannot combine {mapping.OWNER} with "
                    f"{mapping.OWNER_INFERENCE_PRIORITY}, "
                    f"as there is nothing to infer!",
                    obj=req,
                )

            # logically ok, try parsing
            inference_priority = parse_owner_inference_priority_str(
                inference_priority_str
            )
        return (
            org_unit,
            owned_person,
            owner,
            org_unit_uuid,
            owner_uuid,
            owned_person_uuid,
            inference_priority,
        )

    @staticmethod
    def calc_triggers(
        owned_person_uuid: Optional[str],
        org_unit_uuid: Optional[str],
        req: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Determine what to trigger
        :param owned_person_uuid: candidate owned_person_uuid
        :param org_unit_uuid:
        :param req:
        :return:
        """
        if owned_person_uuid:
            return {Trigger.EMPLOYEE_UUID: owned_person_uuid}
        if org_unit_uuid:
            return {Trigger.ORG_UNIT_UUID: owned_person_uuid}

        OwnerRequestHandler.raise_unexpected_input(req)

    @staticmethod
    def validate(
        validity_from: datetime,
        validity_to: datetime,
        org_unit: Optional[Dict[str, Any]],
        owned_person: Optional[Dict[str, Any]],
        owner: Optional[Dict[str, Any]],
    ):
        """
        validate parsed input - raise on error
        :param validity_from: validity from date
        :param validity_to: validity from date
        :param org_unit: potential org_unit
        :param owned_person: potential owned_person
        :param owner: potential owner
        :return:
        """
        if org_unit:
            mora.async_util.async_to_sync(validator.is_date_range_in_org_unit_range)(
                org_unit, validity_from, validity_to
            )

        if owned_person:
            mora.async_util.async_to_sync(validator.is_date_range_in_employee_range)(
                owned_person, validity_from, validity_to
            )

        if owner:
            mora.async_util.async_to_sync(validator.is_date_range_in_employee_range)(
                owner, validity_from, validity_to
            )

    @staticmethod
    async def avalidate(
        validity_from: datetime,
        validity_to: datetime,
        org_unit: Optional[Dict[str, Any]],
        owned_person: Optional[Dict[str, Any]],
        owner: Optional[Dict[str, Any]],
    ):
        """
        validate parsed input - raise on error
        :param validity_from: validity from date
        :param validity_to: validity from date
        :param org_unit: potential org_unit
        :param owned_person: potential owned_person
        :param owner: potential owner
        :return:
        """
        if org_unit:
            await validator.is_date_range_in_org_unit_range(
                org_unit, validity_from, validity_to
            )

        if owned_person:
            await validator.is_date_range_in_employee_range(
                owned_person, validity_from, validity_to
            )

        if owner:
            await validator.is_date_range_in_employee_range(
                owner, validity_from, validity_to
            )

    async def prepare_create(self, req: Dict):
        """To create a vacant owner, set employee_uuid to None
        and set a value org_unit_uuid"""

        (
            org_unit,
            owned_person,
            owner,
            org_unit_uuid,
            owner_uuid,
            owned_person_uuid,
            inference_priority,
        ) = self.extract_info_owner_info(req=req)

        valid_from, valid_to = util.get_validities(req)

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        # Validation
        await self.avalidate(
            org_unit=org_unit,
            owned_person=owned_person,
            owner=owner,
            validity_from=valid_from,
            validity_to=valid_to,
        )
        owner = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.OWNER,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[owned_person_uuid] if owned_person_uuid else [],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid] if org_unit_uuid else [],
            tilknyttedepersoner=[owner_uuid],
            integration_data=req.get(mapping.INTEGRATION_DATA),
            udvidelse_attributter={mapping.EXTENSION_1: inference_priority.value}
            if inference_priority is not None
            else None,
        )

        self.payload = owner
        self.uuid = func_id

        self.trigger_dict.update(
            self.calc_triggers(
                owned_person_uuid=owned_person_uuid,
                org_unit_uuid=org_unit_uuid,
                req=req,
            )
        )

    def prepare_edit(self, req: dict):
        raise NotImplementedError("Use aprepare_edit instead")

    async def aprepare_edit(self, req: dict):
        func_uuid = req.get("uuid")
        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=func_uuid)

        data = req.get("data")
        (
            org_unit,
            owned_person,
            owner,
            org_unit_uuid,
            owner_uuid,
            owned_person_uuid,
            inference_priority,
        ) = self.extract_info_owner_info(req=data)

        new_from, new_to = util.get_validities(data)

        payload = dict()
        payload["note"] = f"Rediger {self.role_type}"

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

        update_fields = list()

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

        if org_unit_uuid:
            update_fields.append(
                (
                    mapping.ASSOCIATED_ORG_UNIT_FIELD,
                    {"uuid": org_unit_uuid},
                )
            )

        if inference_priority is not None:
            update_fields.append(
                (
                    mapping.ORG_FUNK_UDVIDELSER_FIELD,
                    {mapping.EXTENSION_1: inference_priority.value},
                )
            )
        else:
            update_fields.append(
                (
                    mapping.ORG_FUNK_UDVIDELSER_FIELD,
                    {mapping.EXTENSION_1: ""},
                )
            )

        if owner_uuid:
            update_payload = {
                "uuid": owner_uuid,
            }
        else:
            update_payload = {"uuid": "", "urn": ""}

        update_fields.append(
            (
                mapping.EMPLOYEE_PERSON_FIELD,
                update_payload,
            )
        )

        if owned_person_uuid:
            update_fields.append(
                (
                    mapping.USER_FIELD,
                    {"uuid": owned_person_uuid},
                )
            )
        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.OWNER_FIELDS.difference({x[0] for x in update_fields})
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )

        self.validate(
            org_unit=org_unit,
            owned_person=owned_person,
            owner=owner,
            validity_from=new_from,
            validity_to=new_to,
        )

        self.payload = payload
        self.uuid = func_uuid

        self.trigger_dict.update(
            self.calc_triggers(
                owned_person_uuid=owned_person_uuid,
                org_unit_uuid=org_unit_uuid,
                req=req,
            )
        )
