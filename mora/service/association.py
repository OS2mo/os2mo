#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Associations
------------

This section describes how to interact with employee associations.

'''

import flask

from .. import lora
from .. import validator
from . import address
from . import common
from . import keys
from . import mapping
from .common import (create_organisationsfunktion_payload, ensure_bounds,
                     inactivate_old_interval, update_payload)

blueprint = flask.Blueprint('associations', __name__, static_url_path='',
                            url_prefix='/service')


def create_association(employee_uuid, req):
    c = lora.Connector()

    org_unit_uuid = common.get_mapping_uuid(req, keys.ORG_UNIT, required=True)
    org_uuid = c.organisationenhed.get(
        org_unit_uuid)['relationer']['tilhoerer'][0]['uuid']
    job_function_uuid = common.get_mapping_uuid(req, keys.JOB_FUNCTION)
    association_type_uuid = common.get_mapping_uuid(req, keys.ASSOCIATION_TYPE,
                                                    required=True)
    address_obj = common.checked_get(req, keys.ADDRESS, {})
    valid_from = common.get_valid_from(req)
    valid_to = common.get_valid_to(req)

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, keys.ASSOCIATION_KEY)

    # Validation
    validator.is_date_range_in_org_unit_range(org_unit_uuid, valid_from,
                                              valid_to)
    validator.is_date_range_in_employee_range(employee_uuid, valid_from,
                                              valid_to)

    association = create_organisationsfunktion_payload(
        funktionsnavn=keys.ASSOCIATION_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=association_type_uuid,
        opgaver=[{'uuid': job_function_uuid}] if job_function_uuid else None,
        adresser=[
            address.get_relation_for(address_obj),
        ] if address_obj else None,
    )

    c.organisationfunktion.create(association)


def edit_association(employee_uuid, req):
    association_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=association_uuid)

    data = req.get('data')
    new_from = common.get_valid_from(data)
    new_to = common.get_valid_to(data)

    # Get org unit uuid for validation purposes
    org_unit = common.get_obj_value(
        original, mapping.ASSOCIATED_ORG_UNIT_FIELD.path)[-1]
    org_unit_uuid = common.get_uuid(org_unit)

    payload = dict()
    payload['note'] = 'Rediger tilknytning'

    original_data = req.get('original')
    if original_data:
        # We are performing an update
        old_from = common.get_valid_from(original_data)
        old_to = common.get_valid_to(original_data)
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

    if keys.JOB_FUNCTION in data.keys():
        update_fields.append((
            mapping.JOB_FUNCTION_FIELD,
            {'uuid': data.get(keys.JOB_FUNCTION).get('uuid')}
        ))

    if keys.ASSOCIATION_TYPE in data.keys():
        update_fields.append((
            mapping.ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(keys.ASSOCIATION_TYPE).get('uuid')},
        ))

    if keys.ORG_UNIT in data.keys():
        org_unit_uuid = data.get(keys.ORG_UNIT).get('uuid')
        update_fields.append((
            mapping.ASSOCIATED_ORG_UNIT_FIELD,
            {'uuid': org_unit_uuid},
        ))

    if data.get(keys.ADDRESS):
        address_obj = data.get(keys.ADDRESS) or original_data[keys.ADDRESS]

        update_fields.append((
            mapping.SINGLE_ADDRESS_FIELD,
            address.get_relation_for(address_obj),
        ))

    payload = update_payload(new_from, new_to, update_fields, original,
                             payload)

    bounds_fields = list(
        mapping.ASSOCIATION_FIELDS.difference({x[0] for x in update_fields}))
    payload = ensure_bounds(new_from, new_to, bounds_fields, original, payload)

    validator.is_date_range_in_org_unit_range(org_unit_uuid, new_from,
                                              new_to)
    validator.is_date_range_in_employee_range(employee_uuid, new_from,
                                              new_to)

    c.organisationfunktion.update(payload, association_uuid)
