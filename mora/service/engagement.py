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

import collections
import itertools

import flask

from mora import lora
from . import common, employee, facet, keys, mapping, org, itsystem
from .common import (create_organisationsfunktion_payload,
                     ensure_bounds, inactivate_old_interval,
                     update_payload)
from .. import util

blueprint = flask.Blueprint('engagements', __name__, static_url_path='',
                            url_prefix='/service')

RELATION_TYPE_MODULES = {
    'it': itsystem.ITSystems,
}


@blueprint.route('/<any("e", "ou"):type>/<uuid:id>/details/')
def list_details(type, id):
    '''List the available 'detail' types under this entry.

    **Example response**:

    .. sourcecode:: json

      {
        "association": false,
        "engagement": true,
        "role": false,
        "leave": true
      }

    The value above informs you that 'association', 'engagement', 'role' and
    'leave' are valid for this entry, and that no entry exists at any time
    for 'association' and 'role', whereas 'engagement' and 'leave' have at
    least one entry either in the past, present or future.

    '''
    c = common.get_connector()

    r = []

    if type == 'e':
        search = dict(tilknyttedebrugere=id)
        scope = c.bruger
    else:
        assert type == 'ou', 'bad type ' + type
        search = dict(tilknyttedeenheder=id)
        scope = c.organisationenhed

    search.update(virkningfra='-infinity', virkningtil='infinity')

    r = {
        functype: bool(
            c.organisationfunktion(funktionsnavn=funcname, **search),
        )
        for functype, funcname in keys.FUNCTION_KEYS.items()
    }

    reg = scope.get(id)

    for relname, cls in RELATION_TYPE_MODULES.items():
        r[relname] = bool(cls.has(type, reg))

    return flask.jsonify(r)


@blueprint.route(
    '/<any("e", "ou"):type>/<uuid:id>/details/<function>',
)
@util.restrictargs('at', 'validity', 'start', 'limit')
def get_engagement(type, id, function):
    '''Obtain the list of engagements corresponding to a user or
    organisational unit.

    .. :quickref: Engagement; List

    All requests contain validity objects on the following form:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "from": "2016-01-01T00:00:00+00:00",
        "to": "2018-01-01T00:00:00+00:00",
      }

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam string validity: Only show *past*, *present* or
        *future* values -- which the default being to show *present*
        values.
    :queryparam int start: Index of first item for paging.
    :queryparam int limit: Maximum items.

    :param type: 'ou' for querying a unit; 'e' for querying an
        employee.
    :param uuid id: The UUID to query, i.e. the ID of the employee or
        unit.
    :param function: See :http:get:`/service/(any:type)/(uuid:id)/details/`
        for the available values for this field.

    :<jsonarr object job_function:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object type:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object org_unit:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string validity: The validity times of the object.

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
                    "name": "Anders And",
                    "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
                },
                "engagement_type": {
                    "example": null,
                    "name": "Afdeling",
                    "scope": null,
                    "user_key": "afd",
                    "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
                },
                "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                "validity": {
                    "from": "2017-01-01T00:00:00+01:00",
                    "to": null
                },
            }
        ]

    '''

    if function in RELATION_TYPE_MODULES:
        return RELATION_TYPE_MODULES[function].get(type, id)

    c = common.get_connector()

    if type == 'e':
        search = dict(tilknyttedebrugere=id)
    else:
        assert type == 'ou', 'bad type ' + type
        search = dict(tilknyttedeenheder=id)

    # ensure that we report an error correctly
    if function not in keys.FUNCTION_KEYS:
        raise ValueError('invalid function type {!r}'.format(function))

    search.update(
        limit=int(flask.request.args.get('limit', 0)) or 20,
        start=int(flask.request.args.get('start', 0)),
        funktionsnavn=keys.FUNCTION_KEYS[function],
    )

    #
    # all these caches might be overkill when just listing one
    # engagement, but they are frequently helpful when listing all
    # engagements for a unit
    #
    # we fetch the types preemptively so that we may rely on
    # get_all(), and fetch them in as few requests as possible
    #
    functions = collections.OrderedDict(
        c.organisationfunktion.get_all(**search),
    )

    def get_employee_id(effect):
        return effect['relationer']['tilknyttedebrugere'][-1]['uuid']

    def get_unit_id(effect):
        # 'Leave' objects do not contains this relation, so we need to guard
        #  ourselves here
        try:
            return effect['relationer']['tilknyttedeenheder'][-1]['uuid']
        except (KeyError, IndexError):
            return None

    def get_type_id(effect):
        try:
            rels = effect['relationer']
            return rels['organisatoriskfunktionstype'][-1]['uuid']
        except (KeyError, IndexError):
            return None

    def get_title_id(effect):
        try:
            return effect['relationer']['opgaver'][-1]['uuid']
        except (KeyError, IndexError):
            return None

    def convert_engagement(funcid, effect):
        return {
            "uuid": funcid,

            keys.PERSON: user_cache[get_employee_id(effect)],
            keys.ORG_UNIT: unit_cache[get_unit_id(effect)],
            keys.JOB_FUNCTION: class_cache[get_title_id(effect)],
            keys.ENGAGEMENT_TYPE: class_cache[get_type_id(effect)],
        }

    def convert_association(funcid, effect):
        return {
            "uuid": funcid,

            keys.PERSON: user_cache[get_employee_id(effect)],
            keys.ORG_UNIT: unit_cache[get_unit_id(effect)],
            keys.JOB_FUNCTION: class_cache[get_title_id(effect)],
            keys.ASSOCIATION_TYPE: class_cache[get_type_id(effect)],
        }

    def convert_role(funcid, effect):
        return {
            "uuid": funcid,

            keys.PERSON: user_cache[get_employee_id(effect)],
            keys.ORG_UNIT: unit_cache[get_unit_id(effect)],
            keys.ROLE_TYPE: class_cache[get_type_id(effect)],
        }

    def convert_leave(funcid, effect):
        return {
            "uuid": funcid,

            keys.PERSON: user_cache[get_employee_id(effect)],
            keys.LEAVE_TYPE: class_cache[get_type_id(effect)],
        }

    def add_validity(start, end, func):
        func[keys.VALIDITY] = {
            keys.FROM: util.to_iso_time(start),
            keys.TO: util.to_iso_time(end),
        }
        return func

    converters = {
        'engagement': convert_engagement,
        'association': convert_association,
        'role': convert_role,
        'leave': convert_leave,
    }

    class_cache = {
        classid: classid and facet.get_one_class(c, classid, classobj)
        for classid, classobj in c.klasse.get_all(
            uuid=itertools.chain(
                map(get_title_id, functions.values()),
                map(get_type_id, functions.values()),
            )
        )
    }

    user_cache = {
        userid: employee.get_one_employee(c, userid, user)
        for userid, user in
        c.bruger.get_all(uuid={
            get_employee_id(v) for v in functions.values()
        })
    }

    unit_cache = {
        unitid: org.get_one_orgunit(
            c, unitid, unit, details=org.UnitDetails.MINIMAL,
        )
        for unitid, unit in
        c.organisationenhed.get_all(
            uuid=map(get_unit_id,
                     functions.values()),
        )
    }

    class_cache[None] = user_cache[None] = unit_cache[None] = None

    return flask.jsonify([
        add_validity(
            start, end,
            converters[function](funcid, effect)
        )

        for funcid, funcobj in functions.items()
        for start, end, effect in c.organisationfunktion.get_effects(
            funcobj,
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


def create_engagement(employee_uuid, req):
    # TODO: Validation

    c = lora.Connector()

    org_unit_uuid = req.get(keys.ORG_UNIT).get('uuid')
    org_uuid = c.organisationenhed.get(
        org_unit_uuid)['relationer']['tilhoerer'][0]['uuid']
    job_function_uuid = req.get(keys.JOB_FUNCTION).get('uuid')
    engagement_type_uuid = req.get(keys.ENGAGEMENT_TYPE).get('uuid')
    valid_from = common.get_valid_from(req)
    valid_to = common.get_valid_to(req)

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, keys.ENGAGEMENT_KEY)

    engagement = create_organisationsfunktion_payload(
        funktionsnavn=keys.ENGAGEMENT_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=engagement_type_uuid,
        opgaver=[job_function_uuid]
    )

    c.organisationfunktion.create(engagement)


def edit_engagement(employee_uuid, req):
    engagement_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=engagement_uuid)

    data = req.get('data')
    new_from = common.get_valid_from(data)
    new_to = common.get_valid_to(data)

    payload = dict()
    payload['note'] = 'Rediger engagement'

    original_data = req.get('original')
    if original_data:
        # We are performing an update
        old_from = common.get_valid_from(original_data)
        old_to = common.get_valid_to(original_data)
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

    if keys.JOB_FUNCTION in data.keys():
        update_fields.append((
            mapping.JOB_FUNCTION_FIELD,
            {'uuid': data.get(keys.JOB_FUNCTION).get('uuid')}
        ))

    if keys.ENGAGEMENT_TYPE in data.keys():
        update_fields.append((
            mapping.ORG_FUNK_TYPE_FIELD,
            {'uuid': data.get(keys.ENGAGEMENT_TYPE).get('uuid')},
        ))

    if keys.ORG_UNIT in data.keys():
        update_fields.append((
            mapping.ORG_UNIT_FIELD,
            {'uuid': data.get(keys.ORG_UNIT).get('uuid')},
        ))

    payload = update_payload(new_from, new_to, update_fields, original,
                             payload)

    bounds_fields = list(
        mapping.ENGAGEMENT_FIELDS.difference({x[0] for x in update_fields}))
    payload = ensure_bounds(new_from, new_to, bounds_fields, original, payload)

    c.organisationfunktion.update(payload, engagement_uuid)
