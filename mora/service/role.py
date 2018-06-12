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

import flask

from .. import lora
from .. import validator
from . import common, keys, mapping
from .common import (create_organisationsfunktion_payload,
                     ensure_bounds, inactivate_old_interval,
                     update_payload)

blueprint = flask.Blueprint('roles', __name__, static_url_path='',
                            url_prefix='/service')


def create_role(employee_uuid, req):
    c = lora.Connector()

    org_unit_uuid = common.get_mapping_uuid(req, keys.ORG_UNIT, required=True)
    org_uuid = c.organisationenhed.get(
        org_unit_uuid)['relationer']['tilhoerer'][0]['uuid']
    role_type_uuid = common.get_mapping_uuid(req, keys.ROLE_TYPE,
                                             required=True)
    valid_from, valid_to = common.get_validities(req)

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, keys.ROLE_KEY)

    # Validation
    validator.is_date_range_in_org_unit_range(org_unit_uuid, valid_from,
                                              valid_to)
    validator.is_date_range_in_employee_range(employee_uuid, valid_from,
                                              valid_to)

    return create_organisationsfunktion_payload(
        funktionsnavn=keys.ROLE_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=role_type_uuid,
    )


def edit_role(employee_uuid, req):
    role_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=role_uuid)

    data = req.get('data')
    new_from, new_to = common.get_validities(data)

    # Get org unit uuid for validation purposes
    org_unit = common.get_obj_value(
        original, mapping.ASSOCIATED_ORG_UNIT_FIELD.path)[-1]
    org_unit_uuid = common.get_uuid(org_unit)

    payload = dict()
    payload['note'] = 'Rediger rolle'

    original_data = req.get('original')
    if original_data:
        # We are performing an update
        old_from, old_to = common.get_validities(original_data)
        payload = inactivate_old_interval(
            old_from, old_to, new_from, new_to, payload,
            ('tilstande', 'organisationfunktiongyldighed')
        )

    update_fields = list()

    # Always update gyldighed
    update_fields.append((
        mapping.ORG_FUNK_GYLDIGHED_FIELD,
        {'gyldighed': "Aktiv"}
    ))

    if keys.ROLE_TYPE in data:
        update_fields.append((
            mapping.ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(keys.ROLE_TYPE).get('uuid')},
        ))

    if keys.ORG_UNIT in data:
        org_unit_uuid = data.get(keys.ORG_UNIT).get('uuid')
        update_fields.append((
            mapping.ASSOCIATED_ORG_UNIT_FIELD,
            {'uuid': org_unit_uuid},
        ))

    payload = update_payload(new_from, new_to, update_fields, original,
                             payload)

    bounds_fields = list(
        mapping.ROLE_FIELDS.difference({x[0] for x in update_fields}))
    payload = ensure_bounds(new_from, new_to, bounds_fields, original, payload)

    validator.is_date_range_in_org_unit_range(org_unit_uuid, new_from,
                                              new_to)
    validator.is_date_range_in_employee_range(employee_uuid, new_from,
                                              new_to)

    c.organisationfunktion.update(payload, role_uuid)
