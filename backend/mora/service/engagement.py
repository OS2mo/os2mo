# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Engagements
-----------

This section describes how to interact with engagements linking
employees and organisational units.

"""

import uuid
from itertools import chain

from more_itertools import partition
from more_itertools import repeatfunc
from more_itertools import take

from .. import common
from .. import lora
from .. import mapping
from .. import util
from ..triggers import Trigger
from . import handlers
from . import org
from .address import AddressRequestHandler
from .validation import validator


class EngagementRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.ENGAGEMENT
    function_key = mapping.ENGAGEMENT_KEY

    async def prepare_create(self, req):
        org_unit = util.checked_get(req, mapping.ORG_UNIT, {}, required=True)
        org_unit_uuid = util.get_uuid(org_unit, required=True)

        valid_from, valid_to = util.get_validities(req)

        employee = util.checked_get(req, mapping.PERSON, {}, required=True)
        employee_uuid = util.get_uuid(employee, required=True)
        await validator.is_date_range_in_employee_range(employee, valid_from, valid_to)

        await validator.is_date_range_in_org_unit_range(org_unit, valid_from, valid_to)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        primary = util.get_mapping_uuid(req, mapping.PRIMARY)

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        job_function_uuid = util.get_mapping_uuid(req, mapping.JOB_FUNCTION)
        engagement_type_uuid = util.get_mapping_uuid(
            req, mapping.ENGAGEMENT_TYPE, required=True
        )

        extension_attributes = self.get_extension_attribute_fields(req)

        payload = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ENGAGEMENT_KEY,
            primær=primary,
            fraktion=req.get(mapping.FRACTION),
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[employee_uuid],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid],
            funktionstype=engagement_type_uuid,
            opgaver=[{"uuid": job_function_uuid}] if job_function_uuid else [],
            udvidelse_attributter=extension_attributes,
        )

        # deal with addresses
        addresses = util.checked_get(req, mapping.ADDRESS, [])
        addr_ids = take(len(addresses), map(str, repeatfunc(uuid.uuid4)))

        for address_obj, addr_id in zip(addresses, addr_ids):  # pragma: no cover
            address_obj[mapping.ENGAGEMENT] = {
                mapping.UUID: func_id,
                mapping.OBJECTTYPE: mapping.ENGAGEMENT,
            }
            address_obj["uuid"] = addr_id
            if not address_obj.get("validity"):
                address_obj["validity"] = util.checked_get(req, mapping.VALIDITY, {})

        address_tasks = (
            AddressRequestHandler.construct(addr_obj, mapping.RequestType.CREATE)
            for addr_obj in addresses
        )
        self.addresses = [await task for task in address_tasks]
        self.payload = payload
        self.uuid = func_id
        self.trigger_dict.update(
            {Trigger.EMPLOYEE_UUID: employee_uuid, Trigger.ORG_UNIT_UUID: org_unit_uuid}
        )

    async def submit(self):
        if hasattr(self, "addresses"):
            for addr in self.addresses:
                await addr.submit()
        return await super().submit()

    async def prepare_edit(self, req: dict):
        engagement_uuid = util.get_uuid(req)

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=engagement_uuid)

        # Get org unit uuid for validation purposes
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original)

        # Get employee uuid for validation purposes
        employee_uuid = mapping.USER_FIELD.get_uuid(original)

        data = util.checked_get(req, "data", {}, required=True)
        new_from, new_to = util.get_validities(data)

        try:
            exts = max(
                mapping.ORG_FUNK_UDVIDELSER_FIELD(original),
                key=lambda x: x["from_date"],
            )
        except (ValueError, TypeError, LookupError):
            exts = {}

        payload = {"note": "Rediger engagement"}

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

        if mapping.JOB_FUNCTION in data:
            update_fields.append(
                (
                    mapping.JOB_FUNCTION_FIELD,
                    {"uuid": data.get(mapping.JOB_FUNCTION).get("uuid")},
                )
            )

        if mapping.ENGAGEMENT_TYPE in data:
            update_fields.append(
                (
                    mapping.ORG_FUNK_TYPE_FIELD,
                    {"uuid": data.get(mapping.ENGAGEMENT_TYPE).get("uuid")},
                )
            )

        if mapping.ORG_UNIT in data:
            org_unit_uuid = util.get_mapping_uuid(data, mapping.ORG_UNIT, required=True)
            update_fields.append(
                (mapping.ASSOCIATED_ORG_UNIT_FIELD, {"uuid": org_unit_uuid})
            )

        if mapping.PRIMARY in data and data.get(mapping.PRIMARY):
            primary = util.get_mapping_uuid(data, mapping.PRIMARY)

            update_fields.append((mapping.PRIMARY_FIELD, {"uuid": primary}))

        # Attribute extensions
        new_extensions = {}

        if mapping.FRACTION in data:
            fraction = util.checked_get(data, mapping.FRACTION, default=100)

            new_extensions["fraktion"] = fraction

        fields = self.get_extension_attribute_fields(data)
        new_extensions.update(fields)

        if new_extensions:
            update_fields.append(
                (
                    mapping.ORG_FUNK_UDVIDELSER_FIELD,
                    {**exts, **new_extensions},
                )
            )

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.ENGAGEMENT_FIELDS.difference({x[0] for x in update_fields})
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )

        await validator.is_date_range_in_employee_range(
            {"uuid": employee_uuid}, new_from, new_to
        )

        def to_edit_request(address_obj):  # pragma: no cover
            addr_uuid = address_obj.get(mapping.UUID)
            addr_handler = AddressRequestHandler(
                {
                    "data": {**address_obj, "validity": data.get(mapping.VALIDITY)},
                    "uuid": address_obj.get(mapping.UUID),
                },
                mapping.RequestType.EDIT,
            )
            return addr_uuid, addr_handler

        def to_create_request(address_obj) -> tuple[str, AddressRequestHandler]:  # pragma: no cover
            addr_uuid = str(uuid.uuid4())
            addr_handler = AddressRequestHandler(
                {
                    mapping.UUID: addr_uuid,
                    mapping.ENGAGEMENT: {mapping.UUID: engagement_uuid},
                    mapping.VALIDITY: data.get(mapping.VALIDITY),
                    **address_obj,
                },
                mapping.RequestType.CREATE,
            )
            return addr_uuid, addr_handler

        addresses = util.checked_get(data, mapping.ADDRESS, [])
        create_addresses, edit_addresses = partition(
            lambda address_obj: mapping.UUID in address_obj, addresses
        )
        edit_requests = map(to_edit_request, edit_addresses)
        create_requests = map(to_create_request, create_addresses)

        self.addresses = []
        for addr_uuid, addr_handler in chain(
            edit_requests, create_requests
        ):  # pragma: no cover
            update_fields.append(
                (
                    mapping.ASSOCIATED_MANAGER_ADDRESSES_FIELD,
                    {"uuid": addr_uuid},
                )
            )
            self.addresses.append(addr_handler)

        self.payload = payload
        self.uuid = engagement_uuid
        self.trigger_dict.update(
            {Trigger.EMPLOYEE_UUID: employee_uuid, Trigger.ORG_UNIT_UUID: org_unit_uuid}
        )

    @staticmethod
    def get_extension_attribute_fields(req: dict) -> dict:
        """
        Filters all but the generic attribute extension fields, and returns
        them mapped to the LoRa data model
        :param extensions: A dict of all request values
        :return: A dict of mapped attribute extension fields
        """
        return {
            lora_key: util.checked_get(req, mo_key, "")
            for mo_key, lora_key in mapping.EXTENSION_ATTRIBUTE_MAPPING
            if mo_key in req
        }
