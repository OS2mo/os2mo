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
from .common import (create_organisationsfunktion_payload, ensure_bounds,
                     inactivate_old_interval, inactivate_org_funktion,
                     update_payload)
from .keys import (ASSOCIATION_KEY, ASSOCIATION_TYPE, JOB_FUNCTION, LOCATION,
                   ORG_UNIT, VALID_FROM, VALID_TO)
from .mapping import (ADDRESSES_FIELD, ASSOCIATION_FIELDS, JOB_FUNCTION_FIELD,
                      ORG_FUNK_GYLDIGHED_FIELD, ORG_FUNK_TYPE_FIELD,
                      ORG_UNIT_FIELD)

blueprint = flask.Blueprint('associations', __name__, static_url_path='',
                            url_prefix='/service')


def create_association(employee_uuid, req):
    # TODO: Validation
    c = lora.Connector()

    org_unit_uuid = req.get(ORG_UNIT).get('uuid')
    org_uuid = c.organisationenhed.get(
        org_unit_uuid)['relationer']['tilhoerer'][0]['uuid']
    job_title_uuid = req.get(JOB_FUNCTION).get('uuid') if req.get(
        JOB_FUNCTION) else None
    association_type_uuid = req.get(ASSOCIATION_TYPE).get('uuid')
    location_uuid = req.get(LOCATION).get('uuid')
    valid_from = req.get(VALID_FROM)
    valid_to = req.get(VALID_TO, 'infinity')

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, ASSOCIATION_KEY)

    association = create_organisationsfunktion_payload(
        funktionsnavn=ASSOCIATION_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=association_type_uuid,
        opgaver=[job_title_uuid] if job_title_uuid else None,
        adresser=[location_uuid]
    )

    c.organisationfunktion.create(association)


def edit_association(employee_uuid, req):
    association_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=association_uuid)

    data = req.get('data')
    new_from = data.get('valid_from')
    new_to = data.get('valid_to', 'infinity')

    payload = dict()
    payload['note'] = 'Rediger tilknytning'

    original_data = req.get('original')
    if original_data:
        # We are performing an update
        old_from = original_data.get('valid_from')
        old_to = original_data.get('valid_to')
        payload = inactivate_old_interval(
            old_from, old_to, new_from, new_to, payload,
            ('tilstande', 'organisationfunktiongyldighed')
        )

    update_fields = list()

    # Always update gyldighed
    update_fields.append((
        ORG_FUNK_GYLDIGHED_FIELD,
        {'gyldighed': "Aktiv"}
    ))

    if JOB_FUNCTION in data.keys():
        update_fields.append((
            JOB_FUNCTION_FIELD,
            {'uuid': data.get(JOB_FUNCTION).get('uuid')}
        ))

    if ASSOCIATION_TYPE in data.keys():
        update_fields.append((
            ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(ASSOCIATION_TYPE).get('uuid')},
        ))

    if ORG_UNIT in data.keys():
        update_fields.append((
            ORG_UNIT_FIELD,
            {'uuid': data.get(ORG_UNIT).get('uuid')},
        ))

    if LOCATION in data.keys():
        update_fields.append((
            ADDRESSES_FIELD,
            {'uuid': data.get(LOCATION).get('uuid')},
        ))

    payload = update_payload(new_from, new_to, update_fields, original,
                             payload)

    bounds_fields = list(
        ASSOCIATION_FIELDS.difference({x[0] for x in update_fields}))
    payload = ensure_bounds(new_from, new_to, bounds_fields, original, payload)

    c.organisationfunktion.update(payload, association_uuid)


def terminate_association(association_uuid, enddate):
    """
    Terminate the given association at the given date

    :param association_uuid: An engagement UUID
    :param enddate: The date of termination
    """
    c = lora.Connector(effective_date=enddate)

    orgfunk = c.organisationfunktion.get(association_uuid)

    # Create inactivation object
    startdate = [
        g['virkning']['from'] for g in
        orgfunk['tilstande']['organisationfunktiongyldighed']
        if g['gyldighed'] == 'Aktiv'
    ][0]

    payload = inactivate_org_funktion(startdate, enddate, "Afslut tilknytning")
    c.organisationfunktion.update(payload, association_uuid)
