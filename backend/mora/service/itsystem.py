#
# Copyright (c) 2017-2018, Magenta ApS
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

from ..exceptions import ErrorCodes
from .. import exceptions
from .. import mapping
from .. import util

from .. import common

blueprint = flask.Blueprint('itsystem', __name__, static_url_path='',
                            url_prefix='/service')


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


def create_itsystem(employee_uuid, req):
        systemobj = util.checked_get(req, mapping.ITSYSTEM, {},
                                     required=True)
        systemid = util.get_uuid(systemobj)

        original = self.scope.get(
            uuid=id,
            virkningfra='-infinity',
            virkningtil='infinity',
        )

        if not original:
            raise exceptions.HTTPException(ErrorCodes.E_NOT_FOUND)

        rels = original['relationer'].get('tilknyttedeitsystemer', [])

        start, end = util.get_validities(req)

        rels.append(self.get_relation_for(systemid, start, end))

        payload = {
            'relationer': {
                'tilknyttedeitsystemer': rels,
            },
            'note': 'Tilføj IT-system',
        }

        self.scope.update(payload, id)


def edit_itsystem(employee_uuid, req):
        original = self.scope.get(
            uuid=id,
            virkningfra='-infinity',
            virkningtil='infinity',
        )

        old_entry = req.get('original')
        old_rel = original['relationer'].get('tilknyttedeitsystemer', [])

        if not old_entry:
            raise exceptions.HTTPException(ErrorCodes.V_ORIGINAL_REQUIRED)

        # We are performing an update of a pre-existing effect
        old_rel = self.get_relation_for(
            util.get_uuid(old_entry),
            util.get_valid_from(old_entry),
            util.get_valid_to(old_entry),
        )

        new_entry = req['data']

        new_rel = self.get_relation_for(
            util.get_uuid(new_entry, old_entry),
            util.get_valid_from(new_entry, old_entry),
            util.get_valid_to(new_entry, old_entry),
        )

        payload = {
            'relationer': {
                'tilknyttedeitsystemer': common.replace_relation_value(
                    original['relationer'].get('tilknyttedeitsystemer') or [],
                    old_rel, new_rel,
                ),
            },
            'note': 'Rediger IT-system',
        }

        self.scope.update(payload, id)


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
    if not system:
        system = c.itsystem.get(systemid)

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
