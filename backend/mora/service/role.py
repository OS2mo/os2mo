#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Roles
-----

This section describes how to interact with employee roles.

'''

from . import handlers
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from .. import validator


class RoleRequestHandler(handlers.OrgFunkRequestHandler):
    __slots__ = ()

    role_type = 'role'
    function_key = mapping.ROLE_KEY

    def prepare_create(self, req):
        c = lora.Connector()

        org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT,
                                              required=True)

        employee = util.checked_get(req, mapping.PERSON, {}, required=True)
        employee_uuid = util.get_uuid(employee, required=True)

        valid_from, valid_to = util.get_validities(req)

        # Validation
        validator.is_date_range_in_org_unit_range(org_unit_uuid, valid_from,
                                                  valid_to)
        validator.is_date_range_in_employee_range(employee, valid_from,
                                                  valid_to)

        org_unit = c.organisationenhed.get(org_unit_uuid)
        org_uuid = util.get_obj_uuid(org_unit, mapping.BELONGS_TO_FIELD.path)

        role_type_uuid = util.get_mapping_uuid(req, mapping.ROLE_TYPE,
                                               required=True)

        bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, mapping.ROLE_KEY)

        role = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ROLE_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[employee_uuid],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid],
            funktionstype=role_type_uuid,
        )

        self.payload = role
        self.uuid = util.get_uuid(req, required=False)

    def prepare_edit(self, req: dict):
        role_uuid = req.get('uuid')
        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        original = c.organisationfunktion.get(uuid=role_uuid)

        if not original:
            raise exceptions.HTTPException(exceptions.ErrorCodes.E_NOT_FOUND,
                                           uuid=role_uuid)

        data = req.get('data')
        new_from, new_to = util.get_validities(data)

        payload = dict()
        payload['note'] = 'Rediger rolle'

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

        if mapping.ROLE_TYPE in data:
            update_fields.append((
                mapping.ORG_FUNK_TYPE_FIELD,
                {'uuid': data.get(mapping.ROLE_TYPE).get('uuid')},
            ))

        if mapping.ORG_UNIT in data:
            org_unit_uuid = util.get_mapping_uuid(data, mapping.ORG_UNIT)
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

            update_fields.append((
                mapping.USER_FIELD,
                {'uuid': employee_uuid},
            ))
        else:
            employee = util.get_obj_value(
                original, mapping.USER_FIELD.path)[-1]

        payload = common.update_payload(new_from, new_to, update_fields,
                                        original,
                                        payload)

        bounds_fields = list(
            mapping.ROLE_FIELDS.difference({x[0] for x in update_fields}))
        payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                       original, payload)

        validator.is_date_range_in_org_unit_range(org_unit_uuid, new_from,
                                                  new_to)
        validator.is_date_range_in_employee_range(employee, new_from,
                                                  new_to)

        self.payload = payload
        self.uuid = role_uuid
