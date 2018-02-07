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

from mora import lora
from .common import (create_organisationsfunktion_payload,
                     ensure_bounds, inactivate_old_interval,
                     update_payload, inactivate_org_funktion)
from . import keys
from . import mapping

blueprint = flask.Blueprint('leave', __name__, static_url_path='',
                            url_prefix='/service')


def create_leave(employee_uuid, req):
    # TODO: Validation
    c = lora.Connector()

    org_uuid = c.bruger.get(
        employee_uuid)['relationer']['tilhoerer'][0]['uuid']
    leave_type_uuid = req.get(keys.LEAVE_TYPE).get('uuid')
    valid_from = req.get(keys.VALID_FROM)
    valid_to = req.get(keys.VALID_TO, 'infinity')

    bvn = str(uuid.uuid4())

    leave = create_organisationsfunktion_payload(
        funktionsnavn=keys.LEAVE_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        funktionstype=leave_type_uuid,
    )

    c.organisationfunktion.create(leave)


def edit_leave(employee_uuid, req):
    leave_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=leave_uuid)

    data = req.get('data')
    new_from = data.get(keys.VALID_FROM)
    new_to = data.get(keys.VALID_TO, 'infinity')

    payload = dict()
    payload['note'] = 'Rediger orlov'

    original_data = req.get('original')
    if original_data:
        # We are performing an update
        old_from = original_data.get(keys.VALID_FROM)
        old_to = original_data.get(keys.VALID_TO)
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

    if keys.LEAVE_TYPE in data.keys():
        update_fields.append((
            mapping.ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(keys.LEAVE_TYPE).get('uuid')},
        ))

    payload = update_payload(new_from, new_to, update_fields, original,
                             payload)

    bounds_fields = list(
        mapping.LEAVE_FIELDS.difference({x[0] for x in update_fields}))
    payload = ensure_bounds(new_from, new_to, bounds_fields, original, payload)

    c.organisationfunktion.update(payload, leave_uuid)


def terminate_leave(leave_uuid, enddate):
    """
    Terminate the given leave at the given date

    :param leave_uuid: An engagement UUID
    :param enddate: The date of termination
    """
    c = lora.Connector(effective_date=enddate)

    orgfunk = c.organisationfunktion.get(leave_uuid)

    # Create inactivation object
    startdate = [
        g['virkning']['from'] for g in
        orgfunk['tilstande']['organisationfunktiongyldighed']
        if g['gyldighed'] == 'Aktiv'
    ][0]

    payload = inactivate_org_funktion(startdate, enddate, "Afslut orlov")
    c.organisationfunktion.update(payload, leave_uuid)
