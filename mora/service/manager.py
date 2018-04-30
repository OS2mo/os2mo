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
from . import common
from . import keys
from . import mapping
from .. import lora

blueprint = flask.Blueprint('manager', __name__, static_url_path='',
                            url_prefix='/service')


def create_manager(employee_uuid, req):
    # TODO: Validation
    c = lora.Connector()

    org_unit_uuid = req.get(keys.ORG_UNIT).get('uuid')
    org_uuid = c.organisationenhed.get(
        org_unit_uuid)['relationer']['tilhoerer'][0]['uuid']
    address_obj = common.checked_get(req, keys.ADDRESS, {})
    manager_type_uuid = common.get_obj_value(req, (keys.MANAGER_TYPE, 'uuid'))
    responsibility_uuid = common.get_obj_value(req,
                                               (keys.RESPONSIBILITY, 'uuid'))
    manager_level_uuid = common.get_obj_value(req,
                                              (keys.MANAGER_LEVEL, 'uuid'))

    opgaver = list()

    if responsibility_uuid:
        opgaver.append({
            'objekttype': 'lederansvar',
            'uuid': responsibility_uuid
        })

    if manager_level_uuid:
        opgaver.append({
            'objekttype': 'lederniveau',
            'uuid': manager_level_uuid
        })

    # TODO: Figure out what to do with this
    # location_uuid = req.get(keys.LOCATION).get('uuid')
    valid_from = common.get_valid_from(req)
    valid_to = common.get_valid_to(req)

    bvn = str(uuid.uuid4())

    manager = common.create_organisationsfunktion_payload(
        funktionsnavn=keys.MANAGER_KEY,
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

    c.organisationfunktion.create(manager)


def edit_manager(employee_uuid, req):
    manager_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=manager_uuid)

    data = req.get('data')
    new_from = common.get_valid_from(data)
    new_to = common.get_valid_to(data)

    payload = dict()
    payload['note'] = 'Rediger leder'

    original_data = req.get('original')
    if original_data:
        # We are performing an update
        old_from = common.get_valid_from(original_data)
        old_to = common.get_valid_to(original_data)
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

    if keys.MANAGER_TYPE in data.keys():
        update_fields.append((
            mapping.ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(keys.MANAGER_TYPE).get('uuid')},
        ))

    if keys.ORG_UNIT in data.keys():
        update_fields.append((
            mapping.ASSOCIATED_ORG_UNIT_FIELD,
            {'uuid': data.get(keys.ORG_UNIT).get('uuid')},
        ))

    if keys.RESPONSIBILITY in data.keys():
        update_fields.append((
            mapping.RESPONSIBILITY_FIELD,
            {
                'objekttype': 'lederansvar',
                'uuid': data.get(keys.RESPONSIBILITY).get('uuid')
            },
        ))

    if keys.MANAGER_LEVEL in data.keys():
        update_fields.append((
            mapping.MANAGER_LEVEL_FIELD,
            {
                'objekttype': 'lederniveau',
                'uuid': data.get(keys.MANAGER_LEVEL).get('uuid')
            },
        ))

    if data.get(keys.ADDRESS):
        address_obj = data.get(keys.ADDRESS) or original_data[keys.ADDRESS]

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

    c.organisationfunktion.update(payload, manager_uuid)
