#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''Engagements
-----------

This section describes how to interact with engagements linking
employees and organisational units.

'''
import uuid

from .. import common
from .. import lora
from .. import mapping
from .. import util
from .. import validator


def validate_create_engagement(req: dict):
    c = lora.Connector()

    org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT,
                                          required=True)

    valid_from, valid_to = util.get_validities(req)

    employee = util.checked_get(req, mapping.PERSON, {}, required=True)
    employee_uuid = util.get_uuid(employee, required=True)
    validator.is_date_range_in_employee_range(employee, valid_from,
                                              valid_to)

    validator.is_date_range_in_org_unit_range(org_unit_uuid, valid_from,
                                              valid_to)

    org_unit = c.organisationenhed.get(org_unit_uuid)

    org_uuid = org_unit['relationer']['tilhoerer'][0]['uuid']
    job_function_uuid = util.get_mapping_uuid(req, mapping.JOB_FUNCTION)
    engagement_type_uuid = util.get_mapping_uuid(req,
                                                 mapping.ENGAGEMENT_TYPE,
                                                 required=True)

    bvn = str(uuid.uuid4())

    engagement = common.create_organisationsfunktion_payload(
        funktionsnavn=mapping.ENGAGEMENT_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=engagement_type_uuid,
        opgaver=[{'uuid': job_function_uuid}] if job_function_uuid else []
    )

    return {
        'type': 'engagement',
        'payload': engagement
    }


def create_engagement(req: dict):
    c = lora.Connector()

    payload = req['payload']

    return c.organisationfunktion.create(payload)


def validate_edit_engagement(req: dict):
    engagement_uuid = util.get_uuid(req)

    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=engagement_uuid)

    # Get org unit uuid for validation purposes
    org_unit = util.get_obj_value(
        original, mapping.ASSOCIATED_ORG_UNIT_FIELD.path)[-1]
    org_unit_uuid = util.get_uuid(org_unit)

    # Get employee uuid for validation purposes
    employee = util.get_obj_value(
        original, mapping.USER_FIELD.path)[-1]
    employee_uuid = util.get_uuid(employee)

    data = req.get('data')
    new_from, new_to = util.get_validities(data)

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
        org_unit_uuid = data.get(mapping.ORG_UNIT).get('uuid')
        update_fields.append((
            mapping.ASSOCIATED_ORG_UNIT_FIELD,
            {'uuid': org_unit_uuid},
        ))

    payload = common.update_payload(new_from, new_to, update_fields, original,
                                    payload)

    bounds_fields = list(
        mapping.ENGAGEMENT_FIELDS.difference({x[0] for x in update_fields}))
    payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                   original, payload)

    validator.is_date_range_in_org_unit_range(org_unit_uuid, new_from,
                                              new_to)
    validator.is_date_range_in_employee_range(employee, new_from,
                                              new_to)

    return {
        'type': 'engagement',
        'uuid': engagement_uuid,
        'payload': payload
    }


def edit_engagement(req: dict):
    c = lora.Connector()

    payload = req['payload']
    engagement_uuid = req['uuid']

    return c.organisationfunktion.update(payload, engagement_uuid)
