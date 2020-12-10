# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

'''
Associations
------------

This section describes how to interact with employee associations.

'''
import uuid

from . import handlers
from . import org
from .validation import validator
from .. import common, conf_db
from .. import lora
from .. import mapping
from .. import util


class AssociationRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = 'association'
    function_key = mapping.ASSOCIATION_KEY

    @staticmethod
    def substitute_is_needed(association_type_uuid: str) -> bool:
        """
        checks whether the chosen association needs a substitute
        """
        substitute_roles: str = conf_db.get_configuration()[conf_db.SUBSTITUTE_ROLES]
        if substitute_roles == '':
            # no role need substitute
            return False

        if association_type_uuid in substitute_roles.split(','):
            # chosen role does need substitute
            return True
        else:
            return False

    def prepare_create(self, req):
        org_unit = util.checked_get(req, mapping.ORG_UNIT,
                                    {}, required=True)
        org_unit_uuid = util.get_uuid(org_unit, required=True)

        dynamic_classes = util.checked_get(req, mapping.CLASSES, [])
        dynamic_classes = list(map(util.get_uuid, dynamic_classes))

        employee = util.checked_get(req, mapping.PERSON, {}, required=True)
        employee_uuid = util.get_uuid(employee, required=True)

        org_uuid = org.get_configured_organisation(
            util.get_mapping_uuid(req, mapping.ORG, required=False))["uuid"]

        association_type_uuid = util.get_mapping_uuid(
            req,
            mapping.ASSOCIATION_TYPE,
            required=True)

        valid_from, valid_to = util.get_validities(req)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        primary = util.get_mapping_uuid(req, mapping.PRIMARY)

        substitute_uuid = util.get_mapping_uuid(req, mapping.SUBSTITUTE)

        # Validation
        # remove substitute if not needed
        if substitute_uuid:  # substitute is specified
            validator.is_substitute_allowed(association_type_uuid)

        validator.is_date_range_in_org_unit_range(org_unit, valid_from,
                                                  valid_to)
        validator.is_date_range_in_employee_range(employee, valid_from,
                                                  valid_to)
        validator.does_employee_have_existing_association(employee_uuid,
                                                          org_unit_uuid,
                                                          valid_from)
        validator.is_substitute_self(employee_uuid=employee_uuid,
                                     substitute_uuid=substitute_uuid)

        association = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ASSOCIATION_KEY,
            primær=primary,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[employee_uuid],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid],
            tilknyttedeklasser=dynamic_classes,
            tilknyttedefunktioner=[substitute_uuid] if substitute_uuid else [],
            funktionstype=association_type_uuid,
            integration_data=req.get(mapping.INTEGRATION_DATA),
        )

        self.payload = association
        self.uuid = func_id
        self.trigger_dict.update({
            "employee_uuid": employee_uuid,
            "org_unit_uuid": org_unit_uuid,
        })

    def prepare_edit(self, req: dict):
        association_uuid = req.get('uuid')
        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        original = c.organisationfunktion.get(uuid=association_uuid)

        data = req.get('data')
        new_from, new_to = util.get_validities(data)

        # Get org unit uuid for validation purposes
        org_unit = mapping.ASSOCIATED_ORG_UNIT_FIELD(original)[0]

        payload = dict()
        payload['note'] = 'Rediger tilknytning'

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

        if mapping.ASSOCIATION_TYPE in data:
            association_type_uuid = (data.get(mapping.ASSOCIATION_TYPE).get('uuid'))
            update_fields.append((
                mapping.ORG_FUNK_TYPE_FIELD,
                {'uuid': association_type_uuid},
            ))

            if not util.is_substitute_allowed(association_type_uuid):
                update_fields.append(
                    (mapping.ASSOCIATED_FUNCTION_FIELD, {'uuid': '', 'urn': ''})
                )

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

        if mapping.PERSON in data:
            employee = data.get(mapping.PERSON)
            employee_uuid = employee.get('uuid')

            update_fields.append((mapping.USER_FIELD, {'uuid': employee_uuid}))
        else:
            employee = util.get_obj_value(
                original, mapping.USER_FIELD.path)[-1]
            employee_uuid = util.get_uuid(employee)

        if mapping.SUBSTITUTE in data and data.get(mapping.SUBSTITUTE):
            substitute = data.get(mapping.SUBSTITUTE)
            substitute_uuid = substitute.get('uuid')
            validator.is_substitute_self(employee_uuid=employee_uuid,
                                         substitute_uuid=substitute_uuid)

            if not substitute_uuid:
                update_fields.append(
                    (mapping.ASSOCIATED_FUNCTION_FIELD, {'uuid': '', 'urn': ''})
                )
            else:
                association_type_uuid = util.get_mapping_uuid(
                    data,
                    mapping.ASSOCIATION_TYPE,
                    required=True
                )
                validator.is_substitute_allowed(association_type_uuid)
                update_fields.append(
                    (mapping.ASSOCIATED_FUNCTION_FIELD, {'uuid': substitute_uuid})
                )

        if mapping.PRIMARY in data and data.get(mapping.PRIMARY):
            primary = util.get_mapping_uuid(data, mapping.PRIMARY)

            update_fields.append((mapping.PRIMARY_FIELD, {'uuid': primary}))

        for clazz in util.checked_get(data, mapping.CLASSES, []):
            update_fields.append(
                (mapping.ORG_FUNK_CLASSES_FIELD, {"uuid": util.get_uuid(clazz)})
            )

        payload = common.update_payload(new_from, new_to, update_fields,
                                        original,
                                        payload)

        bounds_fields = list(
            mapping.ASSOCIATION_FIELDS.difference(
                {x[0] for x in update_fields}))
        payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                       original, payload)

        # Validation
        validator.is_date_range_in_org_unit_range(org_unit, new_from,
                                                  new_to)
        validator.is_date_range_in_employee_range(employee, new_from,
                                                  new_to)
        validator.does_employee_have_existing_association(employee_uuid,
                                                          org_unit_uuid,
                                                          new_from,
                                                          association_uuid)

        self.payload = payload
        self.uuid = association_uuid
        self.trigger_dict.update({
            "employee_uuid": employee_uuid,
            "org_unit_uuid": org_unit_uuid,
        })
