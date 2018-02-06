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

import copy
import functools
import itertools
import uuid

import flask

from .. import lora
from .. import util

from . import common
from . import keys
from . import mapping

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
    :>jsonarr string type: The type of the system.
    :>jsonarr string user_key: A human-readable unique key for the system.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Lokal Rammearkitektur",
          "type": null,
          "user_key": "LoRa",
          "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697"
        },
        {
          "name": "Active Directory",
          "type": null,
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
            'type': attrs.get('itsystemtype'),
            'user_key': attrs['brugervendtnoegle'],
        }

    return flask.jsonify(
        list(itertools.starmap(convert,
                               c.itsystem.get_all(tilhoerer=orgid))),
    )


@blueprint.route('/e/<uuid:id>/details/it')
@util.restrictargs('at', 'validity')
def get_itsystem(id):
    '''Obtain the list of engagements corresponding to a user.

    .. :quickref: IT system; Get by user

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam string validity: Only show *past*, *present* or
        *future* values -- which the default being to show *present*
        values.

    :param uuid id: The UUID to query, i.e. the ID of the employee or
        unit.

    :<jsonarr string name:
        The name of the IT system in question.
    :<jsonarr string user_name:
        The user name on the IT system, sort of.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string valid_from: The from date, in ISO 8601.
    :<jsonarr string valid_to: The to date, in ISO 8601.

    :status 200: Always.

    **Example response**:

    .. sourcecode:: json

      [
        {
          "name": "Lokal Rammearkitektur",
          "user_name": "Fedtmule",
          "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
          "valid_from": "2016-01-01T00:00:00+01:00",
          "valid_to": "2018-01-01T00:00:00+01:00"
        },
        {
          "name": "Active Directory",
          "user_name": "Fedtmule",
          "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
          "valid_from": "2002-02-14T00:00:00+01:00",
          "valid_to": null
        }
      ]

    '''

    c = common.get_connector()

    system_cache = common.cache(c.itsystem.get)

    def convert(start, end, effect):
        attrs = effect['attributter']['brugeregenskaber'][0]

        for systemrel in effect['relationer'].get('tilknyttedeitsystemer', []):
            if not c.is_effect_relevant(systemrel['virkning']):
                continue
            systemid = systemrel['uuid']
            system = system_cache[systemid]

            system_attrs = system['attributter']['itsystemegenskaber'][0]

            yield {
                "uuid": systemid,

                "name": system_attrs['itsystemnavn'],
                "user_name": attrs['brugernavn'],

                "valid_from": util.to_iso_time(systemrel['virkning']['from']),
                "valid_to": util.to_iso_time(systemrel['virkning']['to']),
            }

    return flask.jsonify(
        sorted(
            itertools.chain.from_iterable(
                itertools.starmap(
                    convert,
                    c.bruger.get_effects(
                        id,
                        {
                            'relationer': (
                                'tilknyttedeitsystemer',
                            ),
                            'tilstande': (
                                'brugergyldighed',
                            ),
                        },
                        {
                            'attributter': (
                                'brugeregenskaber',
                            ),
                        },
                    ),
                ),
            ),
            key=common.get_valid_from,
        ),
    )


def validate_it(func):
    @functools.wraps(func)
    def wrapper(employee_uuid, req):
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        errors = []

        # TODO: cache anything from LoRA and reuse it in the actual request?

        if not req.get(keys.ITSYSTEM):
            errors.append('missing "itsystem"')
        else:
            if not util.is_uuid(req[keys.ITSYSTEM].get('uuid')):
                errors.append('missing or invalid "itsystem" UUID')

            elif not c.itsystem.get(uuid=req[keys.ITSYSTEM]['uuid']):
                errors.append('no such it system')

        if common.get_valid_from(req) == util.negative_infinity:
            errors.append('missing or invalid start date')

        if not c.bruger.get(uuid=employee_uuid):
            errors.append('no such user')

        # TODO: ensure effective time is within both user and itsystem

        if errors:
            # TODO: add granular, consistent and documented error reporting
            raise ValueError('; '.join(errors))

        return func(employee_uuid, req)

    return wrapper


@validate_it
def create_system(employee_uuid, req):
    systemid = req[keys.ITSYSTEM].get('uuid')
    valid_from = common.get_valid_from(req)
    valid_to = common.get_valid_to(req)

    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.bruger.get(uuid=employee_uuid)

    payload = common.update_payload(
        valid_from,
        valid_to,
        [(
            mapping.ITSYSTEMS_FIELD,
            {
                'uuid': systemid,
            }
        )],
        original,
        {
            'note': 'Tilføj IT-system',
        },
    )

    c.bruger.update(payload, employee_uuid)


def edit_system(employee_uuid, req):
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.bruger.get(uuid=employee_uuid)

    data = req.get('data')

    old_entry = req.get('original')
    old_rel = original['relationer'].get('tilknyttedeitsystemer', [])

    if not old_entry:
        raise ValueError('original required!')

    # We are performing an update of a pre-existing effect
    old_id = old_entry['uuid']
    old_from = common.get_valid_from(old_entry)
    old_to = common.get_valid_to(old_entry)

    new_entry = req['data']

    new_id = new_entry.get('uuid') or old_id
    new_from = common.get_valid_from(new_entry, old_entry)
    new_to = common.get_valid_to(new_entry, old_entry)

    new_rel = [
        rel
        for rel in old_rel
        if not (util.parsedatetime(rel['virkning']['from']) == old_from and
                util.parsedatetime(rel['virkning']['to']) == old_to and
                rel.get('uuid') == old_id)
    ]

    # FIXME: this should be a validation error!
    if len(new_rel) == len(old_rel):
        raise ValueError('original entry not found')

    replacement = copy.deepcopy(original)
    replacement['relationer']['tilknyttedeitsystemer'] = new_rel

    payload = common.update_payload(
        new_from,
        new_to,
        [(
            mapping.ITSYSTEMS_FIELD,
            {
                'uuid': new_id,
            }
        )],
        replacement,
        {
            'note': 'Rediger IT-system',
        },
    )

    c.bruger.update(payload, employee_uuid)
