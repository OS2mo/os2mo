#
# Copyright (c) Magenta ApS
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
import json

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
@util.restrictargs('at', 'validity', 'start', 'limit', 'inherit_manager',
                   'calculate_primary', 'only_primary_uuid')
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
    :queryparam bool inherit_manager: Whether inheritance of managers should
        be performed. E.g. if a manager is not found for a given unit, the
        tree is searched upwards until a manager is found.
    :queryparam bool only_primary_uuid: If the response should only contain
        the UUIDs of the various related persons, org units and classes, as
        opposed to a full lookup containing the relevant names etc. This can
        lead to increased performance in some cases.

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
    :<jsonarr object engagement_type:
        See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr object org_unit:
        See :http:get:`/service/ou/(uuid:unitid)/`.
    :<jsonarr object person:
        See :http:get:`/service/e/(uuid:id)/`.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string validity: The validity times of the object.
    :<jsonarr boolean primary: Whether this is the one and only main
                               position for the relevant person.
    :<jsonarr integer fraction: An indication of how much this
        engagement constitutes the employee's overall employment

    .. sourcecode:: json

     [
       {
         "engagement_type": {
           "example": null,
           "name": "Ansat",
           "scope": "TEXT",
           "user_key": "Ansat",
           "uuid": "60315fce-995c-4874-ad7b-48b27aaafb25"
         },
         "job_function": {
           "example": null,
           "name": "Personalekonsulent",
           "scope": "TEXT",
           "user_key": "Personalekonsulent",
           "uuid": "c5d76586-32fe-41e8-b702-27636265d696"
         },
         "org_unit": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "person": {
           "name": "Martin F\u00e8vre Laustsen",
           "uuid": "7d5cdeec-8333-46e9-8a69-b4a2351f4d01"
         },
         "primary": true,
         "fraction": 20,
         "user_key": "2368360a-c860-458c-9725-d678c5efbf79",
         "uuid": "6467fbb0-dd62-48ae-90be-abdef7e66aa7",
         "validity": {
           "from": "1997-04-16",
           "to": null
         }
       }
     ]

    **Example association response**:

    .. sourcecode:: json

     [
       {
         "association_type": {
           "example": null,
           "name": "Formand",
           "scope": "TEXT",
           "user_key": "Formand",
           "uuid": "6968bcf7-e33f-41cd-a218-28d850d5f02d"
         },
         "org_unit": {
           "name": "Borgmesterens Afdeling",
           "user_key": "Borgmesterens Afdeling",
           "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "person": {
           "name": "J\u00f8rgen Siig J\u00f8rgensen",
           "uuid": "f1458657-2498-4c53-82e0-e3857f32875b"
         },
         "primary": null,
         "user_key": "f1458657-2498-4c53-82e0-e3857f32875b \
b6c11152-0645-4712-a207-ba2c53b391ab Tilknytning",
         "uuid": "ad366f7e-4294-4602-abd3-2bd6db20060e",
         "validity": {
           "from": "1996-04-21",
           "to": null
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
           "user_key": "Active Directory",
           "uuid": "ef1acc94-dc2f-49e3-aa03-73a02262393c",
           "validity": {
             "from": "1900-01-01",
             "to": null
           }
         },
         "org_unit": null,
         "person": {
           "name": "Bente Pedersen",
           "uuid": "c9eaffad-971e-4c0c-8516-44c5d29ca092"
         },
         "user_key": "BenteP",
         "uuid": "9045b3e3-5cb9-416d-9499-87c6648695d4",
         "validity": {
           "from": "1978-12-22",
           "to": null
         }
       }
     ]

    **Example address response**:

    .. sourcecode:: json

     [
       {
         "address_type": {
           "example": null,
           "name": "Email",
           "scope": "EMAIL",
           "user_key": "EmailUnit",
           "uuid": "f37f821e-2469-4fdd-bb7b-9e371df0a83b"
         },
         "href": "mailto:info@hjorring.dk",
         "name": "info@hjorring.dk",
         "org_unit": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "user_key": "info@hjorring.dk",
         "uuid": "3dce271e-ba61-4a32-ad3b-9ae9b504c1bb",
         "validity": {
           "from": "1960-01-01",
           "to": null
         },
         "value": "info@hjorring.dk"
       },
       {
         "address_type": {
           "example": null,
           "name": "Postadresse",
           "scope": "DAR",
           "user_key": "AddressMailUnit",
           "uuid": "ee9041d0-3a56-4935-82b3-71302e834cfe"
         },
         "href": "https://www.openstreetmap.org/\
?mlon=9.93195702&mlat=57.35598874&zoom=16",
         "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
         "org_unit": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
         "uuid": "5a21cf1a-aafb-40ad-b3ac-a563f7db4881",
         "validity": {
           "from": "1960-01-01",
           "to": null
         },
         "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
       },
       {
         "address_type": {
           "example": null,
           "name": "P-nummer",
           "scope": "PNUMBER",
           "user_key": "p-nummer",
           "uuid": "8d4d0452-7e53-47d8-86c4-64262e940076"
         },
         "href": null,
         "name": "1484518640",
         "org_unit": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "user_key": "1484518640",
         "uuid": "5bcc497b-22a5-4e51-bd57-63e71d3ce596",
         "validity": {
           "from": "1960-01-01",
           "to": null
         },
         "value": "1484518640"
       },
       {
         "address_type": {
           "example": null,
           "name": "Returadresse",
           "scope": "DAR",
           "user_key": "AdressePostRetur",
           "uuid": "3067bcd7-53d0-474d-a9ac-3d490c738d0a"
         },
         "href": "https://www.openstreetmap.org/\
?mlon=9.93195702&mlat=57.35598874&zoom=16",
         "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
         "org_unit": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
         "uuid": "a038d42a-0372-430d-bd78-f4cf65fcbc4e",
         "validity": {
           "from": "1960-01-01",
           "to": null
         },
         "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
       },
       {
         "address_type": {
           "example": null,
           "name": "Webadresse",
           "scope": "WWW",
           "user_key": "WebUnit",
           "uuid": "1ee7ee52-c597-44d7-a391-6efa7185f51c"
         },
         "href": null,
         "name": "www.hjorring.dk",
         "org_unit": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "user_key": "www.hjorring.dk",
         "uuid": "a18b7b18-7e7c-472d-a7f4-3f3e734b0cba",
         "validity": {
           "from": "1960-01-01",
           "to": null
         },
         "value": "www.hjorring.dk"
       },
       {
         "address_type": {
           "example": null,
           "name": "EAN-nummer",
           "scope": "EAN",
           "user_key": "EAN",
           "uuid": "e40662b4-4098-405d-909a-0a5b2ef11992"
         },
         "href": null,
         "name": "1557056556007",
         "org_unit": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "user_key": "1557056556007",
         "uuid": "bc529a74-0d42-42fa-a0a4-5091d4815331",
         "validity": {
           "from": "1960-01-01",
           "to": null
         },
         "value": "1557056556007"
       },
       {
         "address_type": {
           "example": null,
           "name": "Henvendelsessted",
           "scope": "DAR",
           "user_key": "AdresseHenvendelsessted",
           "uuid": "4525c0e0-0f55-4848-9222-b1b4543105a5"
         },
         "href": "https://www.openstreetmap.org/\
?mlon=9.93195702&mlat=57.35598874&zoom=16",
         "name": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
         "org_unit": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "user_key": "H\u00f8jskolebakken 2E, 1., 9760 Vr\u00e5",
         "uuid": "ec3b056c-9d58-4a95-b67a-ad5dc91ce695",
         "validity": {
           "from": "1960-01-01",
           "to": null
         },
         "value": "0a3f50c8-9f8f-32b8-e044-0003ba298018"
       }
     ]

    **Example org_unit response**:

    An array of objects as returned by :http:get:`/service/ou/(uuid:unitid)/`.

    .. sourcecode:: json

     [
       {
         "name": "Borgmesterens Afdeling",
         "org": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575"
         },
         "org_unit_type": {
           "example": null,
           "name": "Afdeling",
           "scope": "TEXT",
           "user_key": "Afdeling",
           "uuid": "c8002c56-8226-4a72-aefa-a01dcc839391"
         },
         "parent": {
           "name": "Hj\u00f8rring Kommune",
           "user_key": "Hj\u00f8rring Kommune",
           "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "time_planning": null,
         "user_key": "Borgmesterens Afdeling",
         "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
         "validity": {
           "from": "1960-01-01",
           "to": null
         }
       }
     ]

    **Example manager response**:

    .. sourcecode:: json

     [
       {
         "address": [],
         "manager_level": {
           "example": null,
           "name": "Niveau 4",
           "scope": "TEXT",
           "user_key": "Niveau 4",
           "uuid": "049fb201-fc32-40e3-80c7-4cd7cb89a9a3"
         },
         "manager_type": {
           "example": null,
           "name": "Direkt\u00f8r",
           "scope": "TEXT",
           "user_key": "Direkt\u00f8r",
           "uuid": "d4c5983b-c4cd-43f2-b18a-653387172b08"
         },
         "org_unit": {
           "name": "Borgmesterens Afdeling",
           "user_key": "Borgmesterens Afdeling",
           "uuid": "b6c11152-0645-4712-a207-ba2c53b391ab",
           "validity": {
             "from": "1960-01-01",
             "to": null
           }
         },
         "person": {
           "name": "Elisabeth B\u00f8gholm Meils\u00f8e",
           "uuid": "1cd7d465-e525-402f-b93e-e60a20a6e494"
         },
         "responsibility": [
           {
             "example": null,
             "name": "Personale: ans\u00e6ttelse/afskedigelse",
             "scope": "TEXT",
             "user_key": "Personale: ans\u00e6ttelse/afskedigelse",
             "uuid": "07b8b1f5-a441-46d4-b523-c2f44a6dd538"
           },
           {
             "example": null,
             "name": "Ansvar for bygninger og arealer",
             "scope": "TEXT",
             "user_key": "Ansvar for bygninger og arealer",
             "uuid": "76a2a5cc-3274-4110-993b-38110eaea182"
           },
           {
             "example": null,
             "name": "Beredskabsledelse",
             "scope": "TEXT",
             "user_key": "Beredskabsledelse",
             "uuid": "c2add5de-a3a7-41e8-88e9-a71f7b75dc60"
           }
         ],
         "user_key": "d1d2cc75-b86b-45a3-8110-ac7ccbd5993a",
         "uuid": "4a3074ec-bd64-4410-b9ac-08b1e48d6701",
         "validity": {
           "from": "2010-04-08",
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

    # ensure that we report an error correctly

    from ..handler import reading

    cls = reading.get_handler_for_type(function)
    return flask.jsonify(cls.get_from_type(c, type, id))
