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

from mora import lora
from . import common, keys, mapping
from .common import (create_organisationsfunktion_payload, ensure_bounds,
                     inactivate_old_interval, update_payload)

blueprint = flask.Blueprint('associations', __name__, static_url_path='',
                            url_prefix='/service')


def create_association(employee_uuid, req):
    # TODO: Validation
    c = lora.Connector()

    org_unit_uuid = req.get(keys.ORG_UNIT).get('uuid')
    org_uuid = c.organisationenhed.get(
        org_unit_uuid)['relationer']['tilhoerer'][0]['uuid']
    job_function_uuid = req.get(keys.JOB_FUNCTION).get('uuid') if req.get(
        keys.JOB_FUNCTION) else None
    association_type_uuid = req.get(keys.ASSOCIATION_TYPE).get('uuid')
    # location_uuid = req.get(LOCATION).get('uuid')
    valid_from = common.get_valid_from(req)
    valid_to = common.get_valid_to(req)

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, keys.ASSOCIATION_KEY)

    association = create_organisationsfunktion_payload(
        funktionsnavn=keys.ASSOCIATION_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=association_type_uuid,
        opgaver=[{'uuid': job_function_uuid}] if job_function_uuid else None
        # adresser=[location_uuid]
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
        update_fields.append((
            mapping.ASSOCIATED_ORG_UNIT_FIELD,
            {'uuid': data.get(keys.ORG_UNIT).get('uuid')},
        ))

    # if LOCATION in data.keys():
    #     update_fields.append((
    #         ADDRESSES_FIELD,
    #         {'uuid': data.get(LOCATION).get('uuid')},
    #     ))

    payload = update_payload(new_from, new_to, update_fields, original,
                             payload)

    bounds_fields = list(
        mapping.ASSOCIATION_FIELDS.difference({x[0] for x in update_fields}))
    payload = ensure_bounds(new_from, new_to, bounds_fields, original, payload)

    c.organisationfunktion.update(payload, association_uuid)
