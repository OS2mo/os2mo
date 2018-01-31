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

from .. import util

from . import common

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
            key=(lambda v: util.parsedatetime(v['valid_from']))
        ),
    )
