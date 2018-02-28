#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''Details
-------

This section describes how to interact with employee and
organisational unit metadata, referred to as *details* within this
API.

'''

import collections
import itertools

import flask

from . import common
from . import employee
from . import facet
from . import keys
from . import mapping
from . import orgunit
from . import itsystem
from . import address
from .. import util

blueprint = flask.Blueprint('details', __name__, static_url_path='',
                            url_prefix='/service')

RELATION_TYPE_MODULES = {
    'it': itsystem.ITSystems,
    'address': address.Addresses,
}


@blueprint.route('/<any("e", "ou"):type>/<uuid:id>/details/')
def list_details(type, id):
    '''List the available 'detail' types under this entry.

    .. :quickref: Detail; List

    **Example response**:

    .. sourcecode:: json

      {
        "association": false,
        "engagement": true,
        "role": false,
        "leave": true,
        "manager": false
      }

    The value above informs you that at least one entry exists for each of
    'engagement' and 'leave' either in the past, present or future.
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
def get_detail(type, id, function):
    '''Obtain the list of engagements, associations, roles, etc.
    corresponding to a user or organisational unit. See
    :http:get:`/service/(any:type)/(uuid:id)/details/` for the
    available list of endpoints.

    .. :quickref: Detail; Get

    Most of these endpoints are broadly similar to engagements, with
    the notable exception being IT systems.

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

    :status 200: Always.

    **Example engagement response**:

    :<jsonarr object job_function:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object type:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object org_unit:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string validity: The validity times of the object.

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

    **Example IT response**:

    .. sourcecode:: json

          [
              {
                  "address_type": {
                      "example": "<UUID>",
                      "name": "Lokation",
                      "scope": "DAR",
                      "user_key": "AdresseLokation",
                      "uuid": "031f93c3-6bab-462e-a998-87cad6db3128"
                  },
                  "from": "2018-01-01T00:00:00+01:00",
                  "href": "https://www.openstreetmap.org/"
                  "?mlon=12.57924839&mlat=55.68113676&zoom=16",
                  "pretty_value": "Pilestræde 43, 3., 1112 København K",
                  "raw_value": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                  "to": null
              }
          ]

    **Example address response**:

    .. sourcecode:: json

          [
              {
                  "address_type": {
                      "example": "<UUID>",
                      "name": "Lokation",
                      "scope": "DAR",
                      "user_key": "AdresseLokation",
                      "uuid": "031f93c3-6bab-462e-a998-87cad6db3128"
                  },
                  "from": "2018-01-01T00:00:00+01:00",
                  "href": "https://www.openstreetmap.org/"
                  "?mlon=12.57924839&mlat=55.68113676&zoom=16",
                  "pretty_value": "Pilestræde 43, 3., 1112 København K",
                  "raw_value": "0a3f50a0-23c9-32b8-e044-0003ba298018",
                  "to": null
              }
          ]

    '''

    if function in RELATION_TYPE_MODULES:
        return RELATION_TYPE_MODULES[function].get(type, id)
    elif type == 'ou' and function == 'info':
        return flask.redirect(flask.url_for('orgunit.get_org_unit', unitid=id))

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

    def get_responsibility(effect):
        try:
            return list(filter(mapping.RESPONSIBILITY_FIELD.filter_fn,
                               effect['relationer']['opgaver']))[-1]['uuid']
        except (KeyError, IndexError):
            return None

    def get_manager_level(effect):
        try:
            return list(filter(mapping.MANAGER_LEVEL_FIELD.filter_fn,
                               effect['relationer']['opgaver']))[-1]['uuid']
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

    def convert_manager(funcid, effect):
        return {
            "uuid": funcid,

            keys.PERSON: user_cache[get_employee_id(effect)],
            keys.ORG_UNIT: unit_cache[get_unit_id(effect)],
            keys.RESPONSIBILITY: class_cache[get_responsibility(effect)],
            keys.MANAGER_LEVEL: class_cache[get_manager_level(effect)],
            keys.MANAGER_TYPE: class_cache[get_type_id(effect)],
        }

    def add_validity(start, end, func):
        func[keys.VALIDITY] = {
            keys.FROM: util.to_iso_time(start),
            keys.TO: util.to_iso_time(end),
        }
        return func

    def get_classes(effect):
        rels = effect['relationer']
        return [obj.get('uuid') for obj in itertools.chain(
            rels.get('opgaver', []),
            rels.get('organisatoriskfunktionstype', [])
        )]

    converters = {
        'engagement': convert_engagement,
        'association': convert_association,
        'role': convert_role,
        'leave': convert_leave,
        'manager': convert_manager,
    }

    class_cache = {
        classid: classid and facet.get_one_class(c, classid, classobj)
        for classid, classobj in c.klasse.get_all(
            uuid=itertools.chain(*map(get_classes, functions.values())))
    }

    user_cache = {
        userid: employee.get_one_employee(c, userid, user)
        for userid, user in
        c.bruger.get_all(uuid={
            get_employee_id(v) for v in functions.values()
        })
    }

    unit_cache = {
        unitid: orgunit.get_one_orgunit(
            c, unitid, unit, details=orgunit.UnitDetails.MINIMAL,
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
