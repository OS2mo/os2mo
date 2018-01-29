#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''
Engagements
-----------

This section describes how to interact with employee engagements.

'''

import flask

from .. import util

from . import common
from . import employee
from . import facet
from . import org

blueprint = flask.Blueprint('engagements', __name__, static_url_path='',
                            url_prefix='/service')


@blueprint.route('/<any("e", "ou"):type>/<uuid:id>/details/engagement')
@util.restrictargs('at', 'validity')
def get_engagement(type, id):
    '''Obtain the list of engagements corresponding to a user or
    organisational unit.

    .. :quickref: Engagement; List

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam string validity: Only show *past*, *present* or
        *future* values -- which the default being to show *present*
        values.

    :param type: 'ou' for querying a unit; 'e' for querying an
        employee.
    :param uuid id: The UUID to query, i.e. the ID of the employee or
        unit.

    :<jsonarr object job_function:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object type:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object org_unit:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string valid_from: The from date, in ISO 8601.
    :<jsonarr string valid_to: The to date, in ISO 8601.

    :status 200: Always.

    **Example response**:

    .. sourcecode:: json

      [
            {
                "job_function": {
                    "example": null,
                    "name": "Fakultet",
                    "scope": null,
                    "user_key": "fak",
                    "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
                },
                "org_unit": {
                    "name": "Humanistisk fakultet",
                    "user_key": "hum",
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                },
                "person": {
                    "cpr_no": "1111111111",
                    "name": "Anders And",
                    "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
                },
                "type": {
                    "example": null,
                    "name": "Afdeling",
                    "scope": null,
                    "user_key": "afd",
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                "valid_from": "2017-01-01T00:00:00+01:00",
                "valid_to": null
            }
        ]

    '''

    c = common.get_connector()

    if type == 'e':
        search = dict(tilknyttedebrugere=id)
    else:
        assert type == 'ou', 'bad type ' + type
        search = dict(tilknyttedeenheder=id)

    search['funktionsnavn'] = 'Engagement'

    # all these caches are overkill when just listing one engagement,
    # but frequently helpful when listing all engagements for a unit
    class_cache = common.cache(facet.get_class)

    user_cache = common.cache(employee.get_employee, raw=True)

    unit_cache = common.cache(org.get_orgunit,
                              details=org.UnitDetails.MINIMAL,
                              raw=True)

    def _convert_engagement(funcid, start, end, effect):
        rels = effect['relationer']

        emplid = rels['tilknyttedebrugere'][-1]['uuid']

        unitid = rels['tilknyttedeenheder'][-1]['uuid']

        try:
            typeid = rels['organisatoriskfunktionstype'][-1]['uuid']
        except (KeyError, IndexError):
            typeid = None

        try:
            titleid = rels['opgaver'][-1]['uuid']
        except (KeyError, IndexError):
            titleid = None

        r = {
            "uuid": funcid,

            "person": user_cache[emplid],
            "org_unit": unit_cache[unitid],
            "job_function": titleid and class_cache[titleid],
            "type": typeid and class_cache[typeid],

            "valid_from": util.to_iso_time(start),
            "valid_to": util.to_iso_time(end),
        }

        return r

    return flask.jsonify([
        _convert_engagement(funcid, start, end, effect)

        for funcid in c.organisationfunktion(**search)
        for start, end, effect in c.organisationfunktion.get_effects(
            funcid,
            {
                'relationer': (
                    'opgaver',
                    'organisatoriskfunktionstype',
                    'tilknyttedeenheder',
                ),
                'tilstande': (
                    'organisationfunktiongyldighed',
                ),
            },
            {
                'attributter': (
                    'organisationfunktionegenskaber',
                ),
                'relationer': (
                    'tilhoerer',
                    'tilknyttedebrugere',
                    'tilknyttedeorganisationer',
                ),
            },
            virkningfra='-infinity',
            virkningtil='infinity',
        )
        if effect.get('tilstande')
                 .get('organisationfunktiongyldighed')[0]
                 .get('gyldighed') == 'Aktiv'
    ])
