#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''
IT Systems
----------

This section describes how to interact with IT systems.

'''

import itertools
import uuid

import flask

from . import handlers
from . import org
from .validation import validator
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..triggers import Trigger

blueprint = flask.Blueprint('itsystem', __name__, static_url_path='',
                            url_prefix='/service')


class ItsystemRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = 'it'
    function_key = mapping.ITSYSTEM_KEY

    def prepare_create(self, req):
        c = lora.Connector()

        systemid = util.get_mapping_uuid(req, mapping.ITSYSTEM, required=True)
        system = c.itsystem.get(systemid)

        if not system:
            exceptions.ErrorCodes.E_NOT_FOUND()

        org_unit = util.checked_get(req, mapping.ORG_UNIT, {}, required=False)
        org_unit_uuid = util.get_uuid(org_unit, required=False)

        employee = util.checked_get(req, mapping.PERSON, {}, required=False)
        employee_uuid = util.get_uuid(employee, required=False)

        org_uuid = org.get_configured_organisation(
            util.get_mapping_uuid(req, mapping.ORG, required=False))["uuid"]

        valid_from, valid_to = util.get_validities(req)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, func_id)

        # Validation
        if org_unit:
            validator.is_date_range_in_org_unit_range(org_unit,
                                                      valid_from,
                                                      valid_to)

        if employee:
            validator.is_date_range_in_employee_range(employee, valid_from,
                                                      valid_to)

        # TODO: validate that the date range is in
        # the validity of the IT system!

        func = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ITSYSTEM_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            tilknyttedebrugere=[employee_uuid] if employee_uuid else [],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid] if org_unit_uuid else [],
            tilknyttedeitsystemer=[systemid],
            integration_data=req.get(mapping.INTEGRATION_DATA),
        )

        self.payload = func
        self.uuid = func_id
        self.trigger_dict.update({
            Trigger.EMPLOYEE_UUID: employee_uuid,
            Trigger.ORG_UNIT_UUID: org_unit_uuid
        })

    def prepare_edit(self, req: dict):
        function_uuid = util.get_uuid(req)

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        original = c.organisationfunktion.get(uuid=function_uuid)

        if not original:
            exceptions.ErrorCodes.E_NOT_FOUND()

        data = req.get('data')
        new_from, new_to = util.get_validities(data)

        payload = {
            'note': 'Rediger IT-system',
        }

        original_data = req.get('original')
        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from, old_to, new_from, new_to, payload,
                ('tilstande', 'organisationfunktiongyldighed')
            )

        update_fields = [
            # Always update gyldighed
            (
                mapping.ORG_FUNK_GYLDIGHED_FIELD,
                {'gyldighed': "Aktiv"}
            ),
        ]

        if mapping.ITSYSTEM in data:
            update_fields.append((
                mapping.SINGLE_ITSYSTEM_FIELD,
                {'uuid': util.get_mapping_uuid(data, mapping.ITSYSTEM)},
            ))

        if data.get(mapping.PERSON):
            update_fields.append((
                mapping.USER_FIELD,
                {
                    'uuid':
                        util.get_mapping_uuid(data, mapping.PERSON),
                },
            ))

        if data.get(mapping.ORG_UNIT):
            update_fields.append((
                mapping.ASSOCIATED_ORG_UNIT_FIELD,
                {
                    'uuid':
                        util.get_mapping_uuid(data, mapping.ORG_UNIT),
                },
            ))

        try:
            attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):
            attributes = {}
        new_attributes = {}

        if mapping.USER_KEY in data:
            new_attributes['brugervendtnoegle'] = util.checked_get(
                data, mapping.USER_KEY, "")

        if new_attributes:
            update_fields.append((
                mapping.ORG_FUNK_EGENSKABER_FIELD,
                {
                    **attributes,
                    **new_attributes
                },
            ))

        payload = common.update_payload(new_from, new_to, update_fields,
                                        original,
                                        payload)

        bounds_fields = list(mapping.ITSYSTEM_FIELDS.difference(
            {x[0] for x in update_fields},
        ))
        payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                       original,
                                       payload)

        self.payload = payload
        self.uuid = function_uuid
        self.trigger_dict.update({
            Trigger.ORG_UNIT_UUID: (
                mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original)
            ),
            Trigger.EMPLOYEE_UUID: (
                util.get_mapping_uuid(data, mapping.PERSON) or
                mapping.USER_FIELD.get_uuid(original)
            )
        })


@blueprint.route('/o/<uuid:orgid>/it/')
@util.restrictargs('at')
def list_it_systems(orgid: uuid.UUID):
    '''List the IT systems available within the given organisation.

    :param uuid orgid: Restrict search to this organisation.

    .. :quickref: IT system; List available systems

    :>jsonarr string uuid: The universally unique identifier of the system.
    :>jsonarr string name: The name of the system.
    :>jsonarr string system_type: The type of the system.
    :>jsonarr string user_key: A human-readable unique key for the system.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Lokal Rammearkitektur",
          "system_type": null,
          "user_key": "LoRa",
          "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697"
        },
        {
          "name": "Active Directory",
          "system_type": null,
          "user_key": "AD",
          "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb"
        }
      ]

    '''

    c = common.get_connector()

    def convert(systemid, system):
        attrs = system['attributter']['itsystemegenskaber'][0]

        return {
            'uuid': systemid,
            'name': attrs.get('itsystemnavn'),
            'system_type': attrs.get('itsystemtype'),
            'user_key': attrs['brugervendtnoegle'],
        }

    return flask.jsonify(
        list(itertools.starmap(convert,
                               c.itsystem.get_all(tilhoerer=orgid))),
    )


def get_one_itsystem(c, systemid, system=None):
    '''Obtain the list of engagements corresponding to a user.

    .. :quickref: IT system; Get by user

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam string validity: Only show *past*, *present* or
        *future* values -- which the default being to show *present*
        values.

    :param uuid id: The UUID to query, i.e. the ID of the employee or
        unit.

    All requests contain validity objects on the following form:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "from": "2016-01-01",
        "to": "2017-12-31",
      }

    :<jsonarr string name:
        The name of the IT system in question.
    :<jsonarr string user_key:
        Short, unique key identifying the IT-system in question.
    :<jsonarr string reference:
        Optional string describing the elements of the IT system.
    :<jsonarr string system_type:
        Optional string describing the system_type of the IT system.
    :<jsonarr string name:
        The name of the IT system in question.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string validity: The validity times of the object.

    :status 200: Always.

    **Example response**:

    .. sourcecode:: json

      [
        {
          "name": "Lokal Rammearkitektur",
          "reference": null,
          "system_type": null,
          "user_key": "LoRa",
          "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
          "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
          },
        },
        {
          "name": "Active Directory",
          "reference": null,
          "system_type": null,
          "user_key": "AD",
          "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
          "validity": {
            "from": "2002-02-14",
            "to": null
          },
        }
      ]

    '''

    if 'only_primary_uuid' in flask.request.args:
        return {
            mapping.UUID: systemid
        }

    if not system:
        system = c.itsystem.get(systemid)

        if not system or not util.is_reg_valid(system):
            return None

    system_attrs = system['attributter']['itsystemegenskaber'][0]

    return {
        "uuid": systemid,

        "name": system_attrs.get('itsystemnavn'),
        "reference": system_attrs.get('konfigurationreference'),
        "system_type": system_attrs.get('itsystemtype'),
        "user_key": system_attrs.get('brugervendtnoegle'),

        mapping.VALIDITY: util.get_effect_validity(
            system['tilstande']['itsystemgyldighed'][0],
        ),
    }
