#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

"""Manager
-------

This section describes how to interact with employee manager roles.

"""
import uuid

import flask

from . import address
from .. import common
from .. import lora
from .. import mapping
from .. import util
from .. import validator

blueprint = flask.Blueprint('manager', __name__, static_url_path='',
                            url_prefix='/service')


def create_manager(req):
    """ To create a vacant manager postition, set employee_uuid to None
    and set a value org_unit_uuid """
    c = lora.Connector()

    org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT,
                                          required=True)

    employee_uuid = util.get_mapping_uuid(req, mapping.PERSON,
                                          required=False)

    org_uuid = (
        c.organisationenhed.get(org_unit_uuid)
        ['relationer']['tilhoerer'][0]['uuid']
    )

    address_obj = util.checked_get(req, mapping.ADDRESS, {})
    manager_type_uuid = util.get_mapping_uuid(req, mapping.MANAGER_TYPE)
    manager_level_uuid = util.get_mapping_uuid(req, mapping.MANAGER_LEVEL)

    responsibilities = util.checked_get(req, mapping.RESPONSIBILITY, [])

    opgaver = [
        {
            'objekttype': 'lederansvar',
            'uuid': util.get_uuid(responsibility)
        }
        for responsibility in responsibilities
    ]

    if manager_level_uuid:
        opgaver.append({
            'objekttype': 'lederniveau',
            'uuid': manager_level_uuid
        })

    # TODO: Figure out what to do with this
    # location_uuid = req.get(mapping.LOCATION).get('uuid')
    valid_from, valid_to = util.get_validities(req)

    bvn = str(uuid.uuid4())

    # Validation
    validator.is_date_range_in_org_unit_range(org_unit_uuid, valid_from,
                                              valid_to)

    if employee_uuid:
        validator.is_date_range_in_employee_range(employee_uuid, valid_from,
                                                  valid_to)

    manager = common.create_organisationsfunktion_payload(
        funktionsnavn=mapping.MANAGER_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=manager_type_uuid,
        opgaver=opgaver,
        adresser=[
            address.get_relation_for(address_obj),
        ] if address_obj else None,
    )

    return c.organisationfunktion.create(manager)


def edit_manager(req):
    manager_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=manager_uuid)

    data = req.get('data')
    new_from, new_to = util.get_validities(data)

    # Get org unit uuid for validation purposes
    org_unit_uuid = util.get_obj_uuid(
        original, mapping.ASSOCIATED_ORG_UNIT_FIELD.path)

    payload = dict()
    payload['note'] = 'Rediger leder'

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

    if mapping.MANAGER_TYPE in data:
        update_fields.append((
            mapping.ORG_FUNK_TYPE_FIELD,
            {'uuid': util.get_mapping_uuid(data, mapping.MANAGER_TYPE)},
        ))

    if mapping.ORG_UNIT in data:
        update_fields.append((
            mapping.ASSOCIATED_ORG_UNIT_FIELD,
            {'uuid': util.get_mapping_uuid(data, mapping.ORG_UNIT)},
        ))

    if mapping.PERSON in data:
        employee_uuid = util.get_mapping_uuid(data, mapping.PERSON)

        update_fields.append((
            mapping.USER_FIELD,
            {'uuid': employee_uuid} if employee_uuid else {},
        ))
    else:
        employee_uuid = util.get_obj_uuid(original, mapping.USER_FIELD.path)

    for responsibility in util.checked_get(data, mapping.RESPONSIBILITY, []):
        update_fields.append((
            mapping.RESPONSIBILITY_FIELD,
            {
                'objekttype': 'lederansvar',
                'uuid': util.get_uuid(responsibility),
            },
        ))

    if mapping.MANAGER_LEVEL in data:
        update_fields.append((
            mapping.MANAGER_LEVEL_FIELD,
            {
                'objekttype': 'lederniveau',
                'uuid': util.get_mapping_uuid(data, mapping.MANAGER_LEVEL),
            },
        ))

    if data.get(mapping.ADDRESS):
        address_obj = (
            data.get(mapping.ADDRESS) or original_data[mapping.ADDRESS]
        )

        update_fields.append((
            mapping.SINGLE_ADDRESS_FIELD,
            address.get_relation_for(address_obj),
        ))

    payload = common.update_payload(new_from, new_to, update_fields, original,
                                    payload)

    bounds_fields = list(
        mapping.MANAGER_FIELDS.difference({x[0] for x in update_fields}))
    payload = common.ensure_bounds(new_from, new_to, bounds_fields, original,
                                   payload)

    validator.is_date_range_in_org_unit_range(org_unit_uuid, new_from,
                                              new_to)

    if employee_uuid:
        validator.is_date_range_in_employee_range(employee_uuid, new_from,
                                                  new_to)

    validator.is_distinct_responsibility(update_fields)

    return c.organisationfunktion.update(payload, manager_uuid)
