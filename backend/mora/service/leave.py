#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Leave
-----

This section describes how to interact with employee leave.

'''
import uuid

import flask

from .. import lora
from .. import validator
from .. import mapping
from .. import common
from .. import util

blueprint = flask.Blueprint('leave', __name__, static_url_path='',
                            url_prefix='/service')


def create_leave(req, *, employee_uuid=None, org_unit_uuid=None):
    c = lora.Connector()

    org_uuid = c.bruger.get(
        employee_uuid)['relationer']['tilhoerer'][0]['uuid']
    leave_type_uuid = util.get_mapping_uuid(req, mapping.LEAVE_TYPE,
                                            required=True)
    valid_from, valid_to = util.get_validities(req)
    bvn = str(uuid.uuid4())

    # Validation
    validator.is_date_range_in_employee_range(employee_uuid, valid_from,
                                              valid_to)
    validator.does_employee_have_active_engagement(employee_uuid, valid_from,
                                                   valid_to)

    leave = common.create_organisationsfunktion_payload(
        funktionsnavn=mapping.LEAVE_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        funktionstype=leave_type_uuid,
    )

    c.organisationfunktion.create(leave)


def edit_leave(req, *, employee_uuid=None, org_unit_uuid=None):
    leave_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=leave_uuid)

    data = req.get('data')
    new_from, new_to = util.get_validities(data)

    payload = dict()
    payload['note'] = 'Rediger orlov'

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

    if mapping.LEAVE_TYPE in data:
        update_fields.append((
            mapping.ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(mapping.LEAVE_TYPE).get('uuid')},
        ))

    payload = common.update_payload(new_from, new_to, update_fields, original,
                                    payload)

    bounds_fields = list(
        mapping.LEAVE_FIELDS.difference({x[0] for x in update_fields}))
    payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                   original, payload)

    validator.is_date_range_in_employee_range(employee_uuid, new_from,
                                              new_to)
    validator.does_employee_have_active_engagement(employee_uuid, new_from,
                                                   new_to)

    c.organisationfunktion.update(payload, leave_uuid)
