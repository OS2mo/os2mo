# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

'''
EngagementAssociations
----------------------

This section describes how to interact with employee associations.

'''
import uuid
from typing import Any, Dict

import mora.async_util
from . import handlers
from . import org
from .validation import validator
from .. import common
from .. import lora
from .. import mapping
from .. import util


class EngagementAssociationRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.ENGAGEMENT_ASSOCIATION_KEY
    function_key = mapping.ENGAGEMENT_ASSOCIATION_KEY

    def prepare_create(self, req: Dict[Any, Any]):
        """
        To create a vacant association, set employee_uuid to None and set a
        value org_unit_uuid
        :param req: request as received by flask
        :return:
        """
        org_unit = util.checked_get(req, mapping.ORG_UNIT,
                                    {}, required=True)
        org_unit_uuid = util.get_uuid(org_unit, required=True)

        # dynamic_classes = util.checked_get(req, mapping.CLASSES, [])
        # dynamic_classes = list(map(util.get_uuid, dynamic_classes))

        # employee = util.checked_get(req, mapping.PERSON, {})
        # employee_uuid = util.get_uuid(employee, required=False)

        engagement = util.checked_get(req, mapping.ENGAGEMENT, {})
        engagement_uuid = util.get_uuid(engagement, required=False)

        org_uuid = (mora.async_util.async_to_sync(org.get_configured_organisation)(
            util.get_mapping_uuid(req, mapping.ORG, required=False)))["uuid"]

        association_type_uuid = util.get_mapping_uuid(
            req,
            mapping.ENGAGEMENT_ASSOCIATION_TYPE,
            required=True)

        valid_from, valid_to = util.get_validities(req)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        # substitute_uuid = util.get_mapping_uuid(req, mapping.SUBSTITUTE)

        # Validation
        # remove substitute if not needed
        # if substitute_uuid:  # substitute is specified
        #     validator.is_substitute_allowed(association_type_uuid)

        mora.async_util.async_to_sync(validator.is_date_range_in_org_unit_range)(
            org_unit,
            valid_from,
            valid_to)
        if engagement:
            mora.async_util.async_to_sync(validator.is_date_range_in_engagement_range)(
                engagement,
                valid_from,
                valid_to)
        if engagement_uuid:
            mora.async_util.async_to_sync(
                validator.does_engagement_have_existing_association)(
                engagement_uuid,
                org_unit_uuid,
                valid_from)
            # validator.is_substitute_self(employee_uuid=employee_uuid,
            #                              substitute_uuid=substitute_uuid)

        association = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ENGAGEMENT_ASSOCIATION_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid],
            # tilknyttedeklasser=dynamic_classes,
            tilknyttedefunktioner=[common.associated_orgfunc(
                uuid=engagement_uuid,
                orgfunc_type=mapping.MoOrgFunk.ENGAGEMENT
            )],
            funktionstype=association_type_uuid,
            integration_data=req.get(mapping.INTEGRATION_DATA),
        )

        self.payload = association
        self.uuid = func_id
        self.trigger_dict.update({
            # "employee_uuid": employee_uuid,
            "org_unit_uuid": org_unit_uuid,
        })

    def prepare_edit(self, req: Dict[Any, Any]):
        """
        To edit into a vacant association, set employee_uuid to None and set a
        value org_unit_uuid
        :param req: request as received by flask
        :return:
        """
        association_uuid = req.get('uuid')
        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        original = mora.async_util.async_to_sync(c.organisationfunktion.get)(
            uuid=association_uuid)

        data = req.get('data')
        new_from, new_to = util.get_validities(data)

        payload = dict()
        payload['note'] = f'Rediger {mapping.ENGAGEMENT_ASSOCIATION_KEY}'

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

        if mapping.ENGAGEMENT_ASSOCIATION_TYPE in data:
            association_type_uuid = (
                data.get(mapping.ENGAGEMENT_ASSOCIATION_TYPE).get('uuid'))
            update_fields.append((
                mapping.ORG_FUNK_TYPE_FIELD,
                {'uuid': association_type_uuid},
            ))

        if mapping.ORG_UNIT in data:
            org_unit_uuid = data.get(mapping.ORG_UNIT).get('uuid')

            update_fields.append((
                mapping.ASSOCIATED_ORG_UNIT_FIELD,
                {'uuid': org_unit_uuid},
            ))
        else:
            org_unit_uuid = util.get_obj_uuid(
                original,
                mapping.ASSOCIATED_ORG_UNIT_FIELD.path,
            )

        engagement = {}
        if mapping.ENGAGEMENT in data:
            engagement = data.get(mapping.ENGAGEMENT, {})
            if engagement:
                engagement_uuid = engagement.get('uuid')
                update_payload = common.to_lora_obj(common.associated_orgfunc(
                    uuid=engagement_uuid,
                    orgfunc_type=mapping.MoOrgFunk.ENGAGEMENT
                ))

                # else:  # allow missing, e.g. vacant association
                #     employee_uuid = util.get_mapping_uuid(data, mapping.PERSON)
                #     update_payload = {
                #         'uuid': '',
                #         'urn': ''
                #     }
                update_fields.append((
                    mapping.USER_FIELD,
                    update_payload,
                ))
            # update_fields.append((mapping.USER_FIELD, {'uuid': employee_uuid}))

        payload = common.update_payload(new_from, new_to, update_fields,
                                        original,
                                        payload)

        bounds_fields = list(
            mapping.ENGAGEMENT_ASSOCIATION_FIELDS.difference(
                {x[0] for x in update_fields}))
        payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                       original, payload)

        # Validation
        if engagement:
            mora.async_util.async_to_sync(validator.is_date_range_in_engagement_range)(
                engagement,
                new_from,
                new_to)

        if engagement:
            mora.async_util.async_to_sync(
                validator.does_engagement_have_existing_association)(
                engagement_uuid,
                org_unit_uuid,
                new_from,
                association_uuid)

        self.payload = payload
        self.uuid = association_uuid
        self.trigger_dict.update({
            # "employee_uuid": employee_uuid,
            "org_unit_uuid": org_unit_uuid,
        })
