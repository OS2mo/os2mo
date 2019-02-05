#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Reading details
---------------

This section describes how to read employee and
organisational unit metadata, referred to as *details* within this
API.

For details on how to create and edit these metadata, refer to the sections on
creating and editing relations for employees and organisational units:

* :http:post:`/service/details/create`
* :http:post:`/service/details/edit`


'''

from __future__ import generator_stop

import collections
import itertools

import flask

from . import address
from . import employee
from . import facet
from . import handlers
from . import itsystem
from . import orgunit
from .. import common
from .. import exceptions
from .. import mapping
from .. import settings
from .. import util

blueprint = flask.Blueprint('detail_reading', __name__, static_url_path='',
                            url_prefix='/service')

DetailType = collections.namedtuple('DetailType', [
    'search',
    'scope',
])

DETAIL_TYPES = {
    'e': DetailType('tilknyttedebrugere', 'bruger'),
    'ou': DetailType('tilknyttedeenheder', 'organisationenhed'),
}


@blueprint.route('/<any("e", "ou"):type>/<uuid:id>/details/')
@util.restrictargs()
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
        for functype, funcname in handlers.FUNCTION_KEYS.items()
    }

    reg = scope.get(id)

    r['org_unit'] = bool(orgunit.OrgUnitRequestHandler.has(scope, reg))

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
    the notable exception being addresses.

    All requests contain validity objects on the following form:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "from": "2016-01-01",
        "to": "2017-12-31",
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
                    "from": "2017-01-01",
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
            "from": "2017-01-01",
            "to": "2017-12-31"
          }
        }
      ]

    **Example IT response**:

    :<jsonarr object itsystem:
        See :http:get:`/service/o/(uuid:orgid)/it/`.
    :<jsonarr object org_unit:
        See :http:get:`/service/ou/(uuid:unitid)/`.
    :<jsonarr object person:
        See :http:get:`/service/e/(uuid:id)/`.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string user_key: Typically the account name.
    :<jsonarr string validity: The validity times of the object.

    .. sourcecode:: json

      [
        {
          "itsystem": {
            "name": "Active Directory",
            "reference": null,
            "system_type": null,
            "user_key": "AD",
            "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
            "validity": {
              "from": "2002-02-14",
              "to": null
            }
          },
          "org_unit": null,
          "person": {
            "name": "Anders And",
            "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
          },
          "user_key": "donald",
          "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
          "validity": {
            "from": "2017-01-01",
            "to": "2018-09-30"
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
            "from": "2002-02-14",
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
            "from": "2002-02-14",
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
            "from": "2002-02-14",
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
            "from": "2018-01-01",
            "to": "2018-12-31"
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
            "from": "2017-01-01",
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

    cls = handlers.get_handler_for_role_type(function)

    if issubclass(cls, handlers.ReadingRequestHandler):
        return cls.get(c, type, id)

    # ensure that we report an error correctly
    if function not in handlers.FUNCTION_KEYS:
        exceptions.ErrorCodes.E_UNKNOWN_ROLE_TYPE(type=function)

    search.update(
        limit=int(flask.request.args.get('limit', 0)) or
        settings.DEFAULT_PAGE_SIZE,
        start=int(flask.request.args.get('start', 0)),
        funktionsnavn=handlers.FUNCTION_KEYS[function],
    )

    # TODO: the logic encoded in the functions below belong in the
    # 'mapping' module, as part of e.g. FieldTuples
    def get_address(effect):
        return [
            address.get_one_address(addr)
            for addr in mapping.SINGLE_ADDRESS_FIELD(effect)
        ]

    def get_user_key(effect):
        return [
            prop['brugervendtnoegle']
            for prop in mapping.ORG_FUNK_EGENSKABER_FIELD(effect)
        ]

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
    function_cache = {}
    itsystem_cache = {}
    address_type_cache = {}

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
            mapping.PERSON: (
                user_cache, mapping.USER_FIELD, None, False,
            ),
            mapping.ORG_UNIT: (
                unit_cache, mapping.ASSOCIATED_ORG_UNIT_FIELD, None, False,
            ),
            mapping.JOB_FUNCTION: (
                class_cache, mapping.JOB_FUNCTION_FIELD, None, False,
            ),
            mapping.ENGAGEMENT_TYPE: (
                class_cache, mapping.ORG_FUNK_TYPE_FIELD, None, False,
            ),
        },
        'related_unit': {
            mapping.ORG_UNIT: (
                unit_cache, mapping.ASSOCIATED_ORG_UNIT_FIELD, None, True,
            ),
        },
        'association': {
            mapping.PERSON: (
                user_cache, mapping.USER_FIELD, None, False,
            ),
            mapping.ORG_UNIT: (
                unit_cache, mapping.ASSOCIATED_ORG_UNIT_FIELD, None, False,
            ),
            mapping.JOB_FUNCTION: (
                class_cache, mapping.JOB_FUNCTION_FIELD, None, False,
            ),
            mapping.ASSOCIATION_TYPE: (
                class_cache, mapping.ORG_FUNK_TYPE_FIELD, None, False,
            ),
            mapping.ADDRESS: (
                function_cache, mapping.FUNCTION_ADDRESS_FIELD, None, False,
            ),
        },
        'role': {
            mapping.PERSON: (
                user_cache, mapping.USER_FIELD, None, False,
            ),
            mapping.ORG_UNIT: (
                unit_cache, mapping.ASSOCIATED_ORG_UNIT_FIELD, None, False,
            ),
            mapping.ROLE_TYPE: (
                class_cache, mapping.ORG_FUNK_TYPE_FIELD, None, False,
            ),
        },
        'leave': {
            mapping.PERSON: (
                user_cache, mapping.USER_FIELD, None, False,
            ),
            mapping.LEAVE_TYPE: (
                class_cache, mapping.ORG_FUNK_TYPE_FIELD, None, False,
            ),
        },
        'manager': {
            mapping.PERSON: (
                user_cache, mapping.USER_FIELD, None, False,
            ),
            mapping.ORG_UNIT: (
                unit_cache, mapping.ASSOCIATED_ORG_UNIT_FIELD, None, False,
            ),
            mapping.RESPONSIBILITY: (
                class_cache, mapping.RESPONSIBILITY_FIELD, None, True,
            ),
            mapping.MANAGER_LEVEL: (
                class_cache, mapping.MANAGER_LEVEL_FIELD, None, False,
            ),
            mapping.MANAGER_TYPE: (
                class_cache, mapping.ORG_FUNK_TYPE_FIELD, None, False,
            ),
            mapping.ADDRESS: (
                function_cache, mapping.FUNCTION_ADDRESS_FIELD, None, True,
            ),
        },
        'it': {
            mapping.PERSON: (
                user_cache, mapping.USER_FIELD, None, False,
            ),
            mapping.ORG_UNIT: (
                unit_cache, mapping.ASSOCIATED_ORG_UNIT_FIELD, None, False,
            ),
            mapping.ITSYSTEM: (
                itsystem_cache, mapping.SINGLE_ITSYSTEM_FIELD, None, False,
            ),
            mapping.USER_KEY: (
                None, get_user_key, None, False,
            ),
        },
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
                    'tilknyttedefunktioner',
                    'organisatoriskfunktionstype',
                    'tilknyttedeenheder',
                    'tilknyttedebrugere',
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
                    'tilknyttedeorganisationer',
                    'tilknyttedeitsystemer',
                ),
            },
        )
        if util.is_reg_valid(effect)
    ]

    def as_values(vs):
        if vs is None:
            return

        for v in vs:
            yield v.get('uuid', None)

    # extract all object IDs
    for cache, getter, cachegetter, aslist in converters[function].values():
        if cache is not None:
            for start, end, funcid, effect in function_effects:
                for v in as_values((cachegetter or getter)(effect)):
                    cache[v] = None

    # fetch and convert each object once, rather than multiple times
    #

    # handle cross-function links first, the only instance being this
    # detail referring to an address
    address_functions = collections.OrderedDict(
        c.organisationfunktion.get_all(uuid=function_cache)
    )

    # extract address type ids from address functions
    class_cache.update({
        typerel['uuid']: None
        for funcid, funcobj in address_functions.items()
        for typerel in mapping.ADDRESS_TYPE_FIELD(funcobj)
    })

    # fetch all classes
    class_cache.update({
        classid: facet.get_one_class(c, classid, classobj)
        for classid, classobj in c.klasse.get_all(uuid=class_cache)
    })

    def is_empty_lora_object(obj):
        empty = not (obj.get('relationer') or
                     obj.get('attributter') or
                     obj.get('tilstande'))

        return bool(empty)

    function_cache.update({
        funcid: {
            mapping.UUID: funcid,
            mapping.ADDRESS_TYPE: class_cache.get(
                mapping.ADDRESS_TYPE_FIELD(funcobj)[0]['uuid']),
            **address.get_one_address(funcobj),
        }
        for funcid, funcobj in address_functions.items()
        if not is_empty_lora_object(funcobj)
    })

    # inject the classes back into the address type cache
    address_type_cache.update({
        funcid: class_cache[typerel['uuid']]
        for funcid, funcobj in address_functions.items()
        for typerel in mapping.ADDRESS_TYPE_FIELD(funcobj)
    })

    # fetch everything else
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

    itsystem_cache.update({
        systemid: itsystem.get_one_itsystem(
            c, systemid, system,
        )
        for systemid, system in
        c.itsystem.get_all(uuid=itsystem_cache)
    })

    # fetch and convert each object once, rather than multiple times

    def get_one(effect, cache, getter, cachegetter, aslist):
        values = getter(effect)

        if values is None:
            return None

        if cache and not cachegetter:
            values = [
                cache[v['uuid']]
                for v in values
                if 'uuid' in v
            ]

        if aslist:
            return values
        elif values:
            assert len(values) == 1, 'we got multiple where one was expected!?'

            return values[0]
        else:
            return None

    # finally, gather it all in the appropriate objects
    def convert(start, end, funcid, effect):
        func = {
            key: get_one(effect, *args)
            for key, args in converters[function].items()
        }

        func[mapping.VALIDITY] = {
            mapping.FROM: util.to_iso_date(start),
            mapping.TO: util.to_iso_date(end, is_end=True),
        }
        func[mapping.UUID] = funcid

        return func

    def sort_key(obj):
        return (obj[mapping.VALIDITY][mapping.FROM],
                # Set default value for person name if no person
                # is accociated with this position
                util.get_obj_value(obj, (mapping.PERSON, mapping.NAME),
                                   default=' '),
                util.get_obj_value(obj, (mapping.ORG_UNIT, mapping.NAME)))

    return flask.jsonify(sorted(
        itertools.starmap(convert, function_effects),
        key=sort_key
    ))
