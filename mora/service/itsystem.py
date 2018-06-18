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
import werkzeug

from mora.exceptions import ErrorCodes
from .. import exceptions
from .. import util

from . import common
from . import keys

blueprint = flask.Blueprint('itsystem', __name__, static_url_path='',
                            url_prefix='/service')


def get_relation_for(obj, *, fallback=None):
    rel = {
        'uuid': common.get_uuid(obj, fallback),
        'objekttype': 'itsystem',
    }

    validity = common.get_validity_effect(obj, fallback)

    if validity is not None:
        rel['virkning'] = validity

    return rel


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


class ITSystems(common.AbstractRelationDetail):
    def has(self, reg):
        return (
            self.scope.path == 'organisation/bruger' and
            reg and reg.get('relationer') and
            reg['relationer'].get('tilknyttedeitsystemer') and
            any(util.is_uuid(rel.get('uuid'))
                for rel in reg['relationer']['tilknyttedeitsystemer'])
        )

    def get(self, id):
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
            "from": "2016-01-01T00:00:00+00:00",
            "to": "2018-01-01T00:00:00+00:00",
          }

        :<jsonarr string name:
            The name of the IT system in question.
        :<jsonarr string user_name:
            The user name on the IT system, sort of.
        :<jsonarr string uuid: Machine-friendly UUID.
        :<jsonarr string validity: The validity times of the object.

        :status 200: Always.

        **Example response**:

        .. sourcecode:: json

          [
            {
              "name": "Lokal Rammearkitektur",
              "user_name": "Fedtmule",
              "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
              "validity": {
                  "from": "2016-01-01T00:00:00+01:00",
                  "to": "2018-01-01T00:00:00+01:00"
              },
            },
            {
              "name": "Active Directory",
              "user_name": "Fedtmule",
              "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
              "validity": {
                  "from": "2002-02-14T00:00:00+01:00",
                  "to": null
              },
            }
          ]

        '''

        if self.scope.path != 'organisation/bruger':
            raise werkzeug.exceptions.NotFound('no IT systems on units, yet!')

        c = self.scope.connector

        system_cache = common.cache(c.itsystem.get)

        def convert(start, end, effect):
            rels = effect['relationer']

            for systemrel in rels.get('tilknyttedeitsystemer', []):
                if not c.is_effect_relevant(systemrel['virkning']):
                    continue

                try:
                    attrs = effect['attributter']['brugeregenskaber'][0]
                    systemid = systemrel['uuid']

                    system_attrs = (
                        system_cache[systemid]
                        ['attributter']['itsystemegenskaber'][0]
                    )
                except (TypeError, LookupError):
                    continue

                yield {
                    "uuid": systemid,

                    "name": system_attrs['itsystemnavn'],
                    "user_name": attrs['brugernavn'],

                    keys.VALIDITY: common.get_effect_validity(systemrel),
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

    @staticmethod
    def get_relation_for(req, *, fallback=None):
        systemobj = common.checked_get(req, keys.ITSYSTEM, {}, required=True)

        return 'tilknyttedeitsystemer', get_relation_for(systemobj,
                                                         fallback=req)

    def create(self, id, req):
        original = self.scope.get(
            uuid=id,
            virkningfra='-infinity',
            virkningtil='infinity',
        )

        if not original:
            raise exceptions.HTTPException(ErrorCodes.E_USER_NOT_FOUND)

        relname, rel = self.get_relation_for(req)

        payload = {
            'relationer': {
                relname: original['relationer'].get(relname, []) + [rel],
            },
            'note': 'Tilføj IT-system',
        }

        self.scope.update(payload, id)

    def edit(self, id, req):
        original = self.scope.get(
            uuid=id,
            virkningfra='-infinity',
            virkningtil='infinity',
        )

        old_entry = req.get('original')

        if not old_entry:
            raise exceptions.HTTPException(ErrorCodes.V_ORIGINAL_REQUIRED)

        # We are performing an update of a pre-existing effect
        relname = 'tilknyttedeitsystemer'
        old_rel = get_relation_for(old_entry)

        new_entry = req['data']
        new_rel = get_relation_for(new_entry, fallback=old_entry)

        old_rels = original['relationer'].get(relname) or []

        payload = {
            'relationer': {
                relname: common.replace_relation_value(old_rels,
                                                       old_rel, new_rel),
            },
            'note': 'Rediger IT-system',
        }

        self.scope.update(payload, id)
