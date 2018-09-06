#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''Details
-------

This section describes how to read employee and
organisational unit metadata, referred to as *details* within this
API.

For details on how to create and edit these metadata, refer to the sections on
creating and editing relations for employees and organisational units:

* :http:post:`/service/e/(uuid:employee_uuid)/create`
* :http:post:`/service/e/(uuid:employee_uuid)/edit`
* :http:post:`/service/ou/(uuid:unitid)/create`
* :http:post:`/service/ou/(uuid:unitid)/edit`


'''

import collections
import functools
import itertools
import operator

import flask

from .. import mapping
from . import address
from .. import common
from . import employee
from . import facet
from . import orgunit
from .. import util
from .. import settings
from .. import exceptions

blueprint = flask.Blueprint('details', __name__, static_url_path='',
                            url_prefix='/service')

DetailType = collections.namedtuple('DetailType', [
    'search',
    'scope',
    'relation_types',
])

DETAIL_TYPES = {
    'e': DetailType('tilknyttedebrugere', 'bruger',
                    employee.RELATION_TYPES),
    'ou': DetailType('tilknyttedeenheder', 'organisationenhed',
                     orgunit.RELATION_TYPES),
}


@blueprint.route('/<any("e", "ou"):type>/<uuid:id>/details/')
def list_details(type, id):
    '''List the available 'detail' types under this entry.

    .. :quickref: Detail; List

    **Example response**:

    .. sourcecode:: json

      {
        "address": false,
        "association": false,
        "engagement": true,
        "it": false,
        "leave": true,
        "manager": false,
        "role": false
      }

    The value above informs you that at least one entry exists for each of
    'engagement' and 'leave' either in the past, present or future.
    '''

    c = common.get_connector(virkningfra='-infinity',
                             virkningtil='infinity')

    info = DETAIL_TYPES[type]
    search = {
        info.search: id,
    }
    scope = getattr(c, info.scope)

    r = {
        functype: bool(
            c.organisationfunktion(funktionsnavn=funcname, **search),
        )
        for functype, funcname in mapping.FUNCTION_KEYS.items()
    }

    reg = scope.get(id)

    for relname, cls in info.relation_types.items():
        r[relname] = bool(cls(scope).has(reg))

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

    :queryparam date at: Show details valid at this point in time,
        in ISO-8601 format.
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

    **Example association response**:

    .. sourcecode:: json

      [
        {
          "address": {
            "href": "https://www.openstreetmap.org/"
                    "?mlon=12.57924839&mlat=55.68113676&zoom=16",
            "name": "Pilestr\u00e6de 43, 3., 1112 K\u00f8benhavn K",
            "uuid": "0a3f50a0-23c9-32b8-e044-0003ba298018"
          },
          "address_type": {
            "example": "<UUID>",
            "name": "Adresse",
            "scope": "DAR",
            "user_key": "Adresse",
            "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
          },
          "association_type": {
            "example": null,
            "name": "Medlem",
            "scope": null,
            "user_key": "medl",
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
          },
          "job_function": {
            "example": null,
            "name": "Hund",
            "scope": null,
            "user_key": "hund",
            "uuid": "c2b23c43-87c6-48bb-a99c-53396bfa99fb"
          },
          "org_unit": {
            "name": "Humanistisk fakultet",
            "user_key": "hum",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
          },
          "person": {
            "name": "Fedtmule",
            "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
          },
          "uuid": "30cd25e1-b21d-46fe-b299-1c1265e9be66",
          "validity": {
            "from": "2017-01-01T00:00:00+01:00",
            "to": "2018-01-01T00:00:00+01:00"
          }
        }
      ]

    **Example IT response**:

    .. sourcecode:: json

      [
        {
          "name": "Active Directory",
          "user_name": "Fedtmule",
          "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
          "validity": {
            "from": "2002-02-14T00:00:00+01:00",
            "to": null
          }
        }
      ]

    **Example address response**:

    .. sourcecode:: json

     [
        {
          "name": "Christiansborg Slotsplads 1, 1218 København K",
          "uuid": "bae093df-3b06-4f23-90a8-92eabedb3622"
          "href": "https://www.openstreetmap.org/"
              "?mlon=12.58176945&mlat=55.67563739&zoom=16",
          "address_type": {
            "scope": "DAR"
          },
          "validity": {
            "from": "2002-02-14T00:00:00+01:00",
            "to": null
          },
        },
        {
          "name": "goofy@example.com",
          "href": "mailto:goofy@example.com",
          "urn": "urn:mailto:goofy@example.com"
          "address_type": {
            "example": "test@example.com",
            "name": "Emailadresse",
            "scope": "EMAIL",
            "user_key": "Email",
            "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
          },
          "validity": {
            "from": "2002-02-14T00:00:00+01:00",
            "to": null
          },
        },
        {
          "name": "goofy@example.com",
          "href": "mailto:goofy@example.com",
          "urn": "urn:mailto:goofy@example.com"
          "address_type": {
            "example": "test@example.com",
            "name": "Emailadresse",
            "scope": "EMAIL",
            "user_key": "Email",
            "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
          },
          "validity": {
            "from": "2002-02-14T00:00:00+01:00",
            "to": null
          },
        }
      ]

    **Example org_unit response**:

    An array of objects as returned by :http:get:`/service/ou/(uuid:unitid)/`.

    .. sourcecode:: json

      [
        {
          "name": "Afdeling for Fortidshistorik",
          "user_key": "frem",
          "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48"
          "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
          },
          "org_unit_type": {
            "example": null,
            "name": "Afdeling",
            "scope": null,
            "user_key": "afd",
            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
          },
          "parent": {
            "name": "Historisk Institut",
            "user_key": "hist",
            "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa"
          },
          "validity": {
            "from": "2018-01-01T00:00:00+01:00",
            "to": "2019-01-01T00:00:00+01:00"
          }
        }
      ]

    **Example manager response**:

    .. sourcecode:: json

      [
        {
          "address": {
            "href": "mailto:ceo@example.com",
            "name": "ceo@example.com",
            "urn": "urn:mailto:ceo@example.com"
          },
          "address_type": {
            "example": "test@example.com",
            "name": "Emailadresse",
            "scope": "EMAIL",
            "user_key": "Email",
            "uuid": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0"
          },
          "manager_level": {
            "example": null,
            "name": "Institut",
            "scope": null,
            "user_key": "inst",
            "uuid": "ca76a441-6226-404f-88a9-31e02e420e52"
          },
          "manager_type": {
            "example": null,
            "name": "Afdeling",
            "scope": null,
            "user_key": "afd",
            "uuid": "32547559-cfc1-4d97-94c6-70b192eff825"
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
          "responsibility": [
            {
              "example": null,
              "name": "Fakultet",
              "scope": null,
              "user_key": "fak",
              "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"
            }
          ],
          "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
          "validity": {
            "from": "2017-01-01T00:00:00+01:00",
            "to": null
          }
        }
      ]

    '''

    c = common.get_connector()

    info = DETAIL_TYPES[type]
    search = {
        info.search: id,
    }
    scope = getattr(c, info.scope)

    if function in info.relation_types:
        return info.relation_types[function](scope).get(id)

    # ensure that we report an error correctly
    if function not in mapping.FUNCTION_KEYS:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_INVALID_FUNCTION_TYPE)

    search.update(
        limit=int(flask.request.args.get('limit', 0)) or
        settings.DEFAULT_PAGE_SIZE,
        start=int(flask.request.args.get('start', 0)),
        funktionsnavn=mapping.FUNCTION_KEYS[function],
    )

    # TODO: the logic encoded in the functions below belong in the
    # 'mapping' module, as part of e.g. FieldTuples

    def get_address(effect):
        try:
            rels = effect['relationer']['adresser']
        except KeyError:
            return

        yield from map(functools.partial(address.get_one_address,
                                         c, class_cache=class_cache),
                       rels)

    def get_address_type(effect):
        try:
            rels = effect['relationer']['adresser']
        except KeyError:
            return

        yield from map(operator.itemgetter('objekttype'), rels)

    def get_employee_id(effect):
        try:
            yield from effect['relationer']['tilknyttedebrugere']
        except:
            pass

    def get_unit_id(effect):
        # 'Leave' objects do not contains this relation, so we need to guard
        #  ourselves here
        try:
            yield from effect['relationer']['tilknyttedeenheder']
        except (KeyError, IndexError):
            pass

    def get_type_id(effect):
        try:
            yield from effect['relationer']['organisatoriskfunktionstype']
        except (KeyError, IndexError):
            pass

    def get_title_id(effect):
        try:
            yield from effect['relationer']['opgaver']
        except (KeyError, IndexError):
            pass

    def get_responsibility(effect):
        try:
            yield from filter(mapping.RESPONSIBILITY_FIELD.filter_fn,
                              effect['relationer']['opgaver'])
        except (KeyError, IndexError):
            pass

    def get_manager_level(effect):
        try:
            yield from filter(mapping.MANAGER_LEVEL_FIELD.filter_fn,
                              effect['relationer']['opgaver'])
        except (KeyError, IndexError):
            pass

    #
    # all these caches might be overkill when just listing one
    # engagement, but they are frequently helpful when listing all
    # engagements for a unit
    #
    # we fetch the types preemptively so that we may rely on
    # get_all(), and fetch them in as few requests as possible
    #
    class_cache = {}
    user_cache = {}
    unit_cache = {}

    # the values are cache, getter, cachegetter, aslist
    #
    # if 'cachegetter' is specified, we cache something other than the
    # actual value
    #
    # aslist means that we expect multiple values for that field, and
    # return them as a list rather than a single object; otherwise, we
    # just return the first hit
    converters = {
        'engagement': {
            mapping.PERSON: (user_cache, get_employee_id, None, False),
            mapping.ORG_UNIT: (unit_cache, get_unit_id, None, False),
            mapping.JOB_FUNCTION: (class_cache, get_title_id, None, False),
            mapping.ENGAGEMENT_TYPE: (class_cache, get_type_id, None, False),
        },
        'association': {
            mapping.PERSON: (user_cache, get_employee_id, None, False),
            mapping.ORG_UNIT: (unit_cache, get_unit_id, None, False),
            mapping.JOB_FUNCTION: (class_cache, get_title_id, None, False),
            mapping.ASSOCIATION_TYPE: (class_cache, get_type_id, None, False),
            mapping.ADDRESS: (class_cache, get_address, get_address_type,
                              False),
        },
        'role': {
            mapping.PERSON: (user_cache, get_employee_id, None, False),
            mapping.ORG_UNIT: (unit_cache, get_unit_id, None, False),
            mapping.ROLE_TYPE: (class_cache, get_type_id, None, False),
        },
        'leave': {
            mapping.PERSON: (user_cache, get_employee_id, None, False),
            mapping.LEAVE_TYPE: (class_cache, get_type_id, None, False),
        },
        'manager': {
            mapping.PERSON: (user_cache, get_employee_id, None, False),
            mapping.ORG_UNIT: (unit_cache, get_unit_id, None, False),
            mapping.RESPONSIBILITY: (class_cache, get_responsibility, None,
                                     True),
            mapping.MANAGER_LEVEL: (class_cache, get_manager_level, None,
                                    False),
            mapping.MANAGER_TYPE: (class_cache, get_type_id, None, False),
            mapping.ADDRESS: (class_cache, get_address, get_address_type,
                              False),
        }
    }

    # first, extract all the effects
    function_effects = [
        (start, end, funcid, effect)
        for funcid, funcobj in c.organisationfunktion.get_all(**search)
        for start, end, effect in c.organisationfunktion.get_effects(
            funcobj,
            {
                'relationer': (
                    'opgaver',
                    'adresser',
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
        )
        if util.is_reg_valid(effect)
    ]

    def as_values(vs):
        if not vs:
            return

        for v in vs:
            if isinstance(v, str):
                yield v
            else:
                yield util.get_uuid(v)

    # extract all object IDs
    for cache, getter, cachegetter, aslist in converters[function].values():
        for start, end, funcid, effect in function_effects:
            for v in as_values((cachegetter or getter)(effect)):
                cache[v] = None

    # fetch and convert each object once, rather than multiple times
    class_cache.update({
        classid: facet.get_one_class(c, classid, classobj)
        for classid, classobj in c.klasse.get_all(uuid=class_cache)
    })

    user_cache.update({
        userid: employee.get_one_employee(c, userid, user)
        for userid, user in
        c.bruger.get_all(uuid=user_cache)
    })

    unit_cache.update({
        unitid: orgunit.get_one_orgunit(
            c, unitid, unit, details=orgunit.UnitDetails.MINIMAL,
        )
        for unitid, unit in
        c.organisationenhed.get_all(uuid=unit_cache)
    })

    def get_one(effect, cache, getter, cachegetter, aslist):
        values = getter(effect)

        if cache and not cachegetter:
            values = (cache[util.get_uuid(v)] for v in values)

        if aslist:
            return list(values)
        else:
            # TODO: what if we get multiple?
            return next(values, None)

    # finally, gather it all in the appropriate objects
    def convert(start, end, funcid, effect):
        func = {
            key: get_one(effect, *args)
            for key, args in converters[function].items()
        }

        func[mapping.VALIDITY] = {
            mapping.FROM: util.to_iso_time(start),
            mapping.TO: util.to_iso_time(end),
        }
        func[mapping.UUID] = funcid

        return func

    def sort_key(obj):
        time_from = obj[mapping.VALIDITY][mapping.FROM]
        name = util.get_obj_value(obj, (mapping.PERSON, mapping.NAME))
        if name is None: # This happens if the manager position is vacant
            name = ' '
        org_unit = util.get_obj_value(obj, (mapping.ORG_UNIT, mapping.NAME))
        return_tuple = (time_from, name, org_unit)
        return return_tuple

    return flask.jsonify(sorted(
        itertools.starmap(convert, function_effects),
        key=sort_key
    ))
