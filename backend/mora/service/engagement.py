# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0


'''Engagements
-----------

This section describes how to interact with engagements linking
employees and organisational units.

'''
import uuid

from . import handlers
from . import org
from .validation import validator
from .. import common
from .. import lora
from .. import mapping
from .. import util
from ..triggers import Trigger


class EngagementRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = 'engagement'
    function_key = mapping.ENGAGEMENT_KEY

    def prepare_create(self, req):
        org_unit = util.checked_get(req, mapping.ORG_UNIT,
                                    {}, required=True)
        org_unit_uuid = util.get_uuid(org_unit, required=True)

        valid_from, valid_to = util.get_validities(req)

        employee = util.checked_get(req, mapping.PERSON, {}, required=True)
        employee_uuid = util.get_uuid(employee, required=True)
        validator.is_date_range_in_employee_range(employee, valid_from,
                                                  valid_to)

        validator.is_date_range_in_org_unit_range(org_unit, valid_from,
                                                  valid_to)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        primary = util.get_mapping_uuid(req, mapping.PRIMARY)

        org_uuid = org.get_configured_organisation(
            util.get_mapping_uuid(req, mapping.ORG, required=False))["uuid"]

        job_function_uuid = util.get_mapping_uuid(req,
                                                  mapping.JOB_FUNCTION)
        engagement_type_uuid = util.get_mapping_uuid(req,
                                                     mapping.ENGAGEMENT_TYPE,
                                                     required=True)

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
            opgaver=[{'uuid': job_function_uuid}] if job_function_uuid else [],
            integration_data=req.get(mapping.INTEGRATION_DATA),
            udvidelse_attributter=extension_attributes
        )

        self.payload = payload
        self.uuid = func_id
        self.trigger_dict.update({
            Trigger.EMPLOYEE_UUID: employee_uuid,
            Trigger.ORG_UNIT_UUID: org_unit_uuid
        })

    def prepare_edit(self, req: dict):
        engagement_uuid = util.get_uuid(req)

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        original = c.organisationfunktion.get(uuid=engagement_uuid)

        # Get org unit uuid for validation purposes
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original)

        # Get employee uuid for validation purposes
        employee_uuid = mapping.USER_FIELD.get_uuid(original)

        data = util.checked_get(req, 'data', {}, required=True)
        new_from, new_to = util.get_validities(data)

        try:
            exts = mapping.ORG_FUNK_UDVIDELSER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):
            exts = {}

        payload = dict()
        payload['note'] = 'Rediger engagement'

        original_data = req.get('original')
        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from, old_to, new_from, new_to, payload,
                ('tilstande', 'organisationfunktiongyldighed')
            )

        update_fields = list()

        # Always update gyldighed
        update_fields.append((
            mapping.ORG_FUNK_GYLDIGHED_FIELD,
            {'gyldighed': "Aktiv"}
        ))

        try:
            attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):
            attributes = {}
        new_attributes = {}

        if mapping.USER_KEY in data:
            new_attributes['brugervendtnoegle'] = util.checked_get(
                data, mapping.USER_KEY, "")

        if new_attributes:
            update_fields.append((
                mapping.ORG_FUNK_EGENSKABER_FIELD,
                {
                    **attributes,
                    **new_attributes
                },
            ))

        if mapping.JOB_FUNCTION in data:
            update_fields.append((
                mapping.JOB_FUNCTION_FIELD,
                {'uuid': data.get(mapping.JOB_FUNCTION).get('uuid')}
            ))

        if mapping.ENGAGEMENT_TYPE in data:
            update_fields.append((
                mapping.ORG_FUNK_TYPE_FIELD,
                {'uuid': data.get(mapping.ENGAGEMENT_TYPE).get('uuid')},
            ))

        if mapping.ORG_UNIT in data:
            org_unit_uuid = util.get_mapping_uuid(data, mapping.ORG_UNIT,
                                                  required=True)
            update_fields.append((mapping.ASSOCIATED_ORG_UNIT_FIELD,
                                  {'uuid': org_unit_uuid}))

        if mapping.PRIMARY in data and data.get(mapping.PRIMARY):
            primary = util.get_mapping_uuid(data, mapping.PRIMARY)

            update_fields.append((mapping.PRIMARY_FIELD, {'uuid': primary}))

        # Attribute extensions
        new_extensions = {}

        if mapping.FRACTION in data:
            fraction = util.checked_get(data, mapping.FRACTION, default=100)

            new_extensions['fraktion'] = fraction

        fields = self.get_extension_attribute_fields(data)
        new_extensions.update(fields)

        if new_extensions:
            update_fields.append((
                mapping.ORG_FUNK_UDVIDELSER_FIELD,
                {
                    **exts,
                    **new_extensions
                },
            ))

        payload = common.update_payload(new_from, new_to, update_fields,
                                        original, payload)

        bounds_fields = list(
            mapping.ENGAGEMENT_FIELDS.difference(
                {x[0] for x in update_fields}))
        payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                       original, payload)

        validator.is_date_range_in_org_unit_range({'uuid': org_unit_uuid},
                                                  new_from, new_to)
        validator.is_date_range_in_employee_range({'uuid': employee_uuid},
                                                  new_from, new_to)

        self.payload = payload
        self.uuid = engagement_uuid
        self.trigger_dict.update({
            Trigger.EMPLOYEE_UUID: employee_uuid,
            Trigger.ORG_UNIT_UUID: org_unit_uuid
        })

    @staticmethod
    def get_extension_attribute_fields(req: dict) -> dict:
        """
        Filters all but the generic attribute extension fields, and returns
        them mapped to the LoRa data moedl
        :param extensions: A dict of all request values
        :return: A dict of mapped attribute extension fields
        """
        return {
            lora_key: util.checked_get(req, mo_key, "")
            for mo_key, lora_key in mapping.EXTENSION_ATTRIBUTE_MAPPING
            if mo_key in req
        }
