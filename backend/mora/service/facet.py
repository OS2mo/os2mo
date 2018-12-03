#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Facets
------

This sections describes how to interact with facets, i.e. the types of
objects.

    .. http:>jsonarr string name:: Human-readable name.

    .. http:>jsonarr string uuid:: Machine-friendly UUID.
    .. http:>jsonarr string user_key:: Short, unique key.
    .. http:>jsonarr string example:: An example value for the address field.
        A value of `<UUID>` means that this is a `DAR`_ address UUID.

'''

import locale
import uuid

import flask
import werkzeug

from .. import common
from .. import exceptions
from .. import mapping
from .. import settings
from .. import util

blueprint = flask.Blueprint('facet', __name__, static_url_path='',
                            url_prefix='/service')

# TODO: we should probably move this into the frontend - in
# actualilty, the translation services little purpose other than to
# make the application less flexible
FACETS = {
    mapping.ADDRESS_TYPE: 'Adressetype',
    mapping.ASSOCIATION_TYPE: 'Tilknytningstype',
    # mapping.AUTHORITY_TYPE: 'Myndighedstype',
    mapping.ENGAGEMENT_TYPE: 'Engagementstype',
    # mapping.FUNCTION_TYPE: 'Funktionstype',
    mapping.JOB_FUNCTION: 'Stillingsbetegnelse',
    mapping.MANAGER_TYPE: 'Ledertyper',
    mapping.ORG_UNIT_TYPE: 'Enhedstype',
    mapping.RESPONSIBILITY: 'Lederansvar',
    mapping.MANAGER_LEVEL: 'Lederniveau',
    mapping.ROLE_TYPE: 'Rolletype',
    # mapping.USER_TYPE: 'Brugertype',
    mapping.LEAVE_TYPE: 'Orlovstype',
    mapping.MANAGER_ADDRESS_TYPE: 'Lederadressetype',
}

FACET_NAMES = {
    v: k for k, v in FACETS.items()
}


@blueprint.route('/o/<uuid:orgid>/f/')
@util.restrictargs()
def list_facets(orgid):
    '''List the facet types available in a given organisation.

    :param uuid orgid: Restrict search to this organisation.

    .. :quickref: Facet; List types

    :>jsonarr string name: The facet name.
    :>jsonarr string path: The location on the web server.
    :>jsonarr string user_key: Short, unique key identifying the facet
    :>jsonarr string uuid: The UUID of the facet.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "address",
          "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address/",
          "user_key": "Adressetype",
          "uuid": "e337bab4-635f-49ce-aa31-b44047a43aa1"
        },
        {
          "name": "ou",
          "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/ou/",
          "user_key": "Enhedstype",
          "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280"
        }
      ]

    '''

    c = common.get_connector()

    r = []

    for facetid, facet in c.facet.get_all(ansvarlig=orgid,
                                          publiceret='Publiceret'):
        facet_name = FACET_NAMES.get(
            facet['attributter']['facetegenskaber'][0]['brugervendtnoegle'],
        )

        r.append(get_one_facet(c, facetid, facet_name, orgid, facet))

    return flask.jsonify(sorted(
        r,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f['name']) if f['name'] else '',
    ))


def get_one_facet(c, facetid, facet_name, orgid, facet=None, data=None):
    if not facet:
        facet = c.facet.get(facetid)

    r = {
        'uuid': facetid,
        'name': facet_name,
        'user_key':
            facet['attributter']
            ['facetegenskaber'][0]
            ['brugervendtnoegle'],
        'path': facet_name and flask.url_for('facet.get_classes', orgid=orgid,
                                             facet=facet_name),
    }

    if data:
        r['data'] = data

    return r


def get_one_class(c, classid, clazz=None):
    if not clazz:
        clazz = c.klasse.get(classid)

        if not clazz:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                'no such class {!r}'.format(classid),
            )

    attrs = clazz['attributter']['klasseegenskaber'][0]

    return {
        'uuid': classid,
        'name': attrs.get('titel'),
        'user_key': attrs.get('brugervendtnoegle'),
        'example': attrs.get('eksempel'),
        'scope': attrs.get('omfang'),
    }


@blueprint.route('/o/<uuid:orgid>/f/<facet>/')
@util.restrictargs('limit', 'start')
def get_classes(orgid: uuid.UUID, facet: str):
    '''List classes available in the given facet.

    .. :quickref: Facet; Get

    :param uuid orgid: Restrict search to this organisation.
    :param string facet: One of the facet names listed by
        :http:get:`/service/o/(uuid:orgid)/f/`

    :queryparam int start: Index of first item for paging.
    :queryparam int limit: Maximum items.

    :>jsonarr string name: Human-readable name.
    :>jsonarr string uuid: Machine-friendly UUID.
    :>jsonarr string user_key: Short, unique key.
    :>jsonarr string example: An example value. In most cases the
        value is meant to be presented to the user as an aid.
    :>jsonarr string scope: A representation of the type of value, see
        the table below for details.

    :status 200: On success.
    :status 404: Whenever the facet isn't found.

    **Example Response**:

    .. sourcecode:: json

      {
        "name": "address_type",
        "path":
          "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address_type/",
        "user_key": "Adressetype",
        "uuid": "e337bab4-635f-49ce-aa31-b44047a43aa1",
        "data": {
          "items": [
            {
              "example": "http://www.korsbaek.dk/",
              "name": "Hjemmeside",
              "scope": "WWW",
              "user_key": "URL",
              "uuid": "160ecaed-50b0-4800-bebc-0d0289a4f624"
            },
            {
              "example": "<UUID>",
              "name": "Lokation",
              "scope": "DAR",
              "user_key": "AdresseLokation",
              "uuid": "031f93c3-6bab-462e-a998-87cad6db3128"
            },
            {
              "example": "Mandag 10:00-12:00 Tirsdag 14:00-16:00",
              "name": "Åbningstid, telefon",
              "scope": "TEXT",
              "user_key": "Åbningstid Telefon",
              "uuid": "0836ffbf-3b3e-410f-8cbf-face7e6844ef"
            }
          ],
          "offset": 0,
          "total": 3
        }
      }

    '''

    try:
        facet_name = FACETS[facet]
    except KeyError:
        raise werkzeug.exceptions.NotFound(
            'No facet named {!r}! Possible values are: {}'.format(
                facet,
                ', '.join(sorted(FACETS)),
            ),
        )

    c = common.get_connector()

    start = int(flask.request.args.get('start') or 0)
    limit = int(flask.request.args.get('limit') or settings.DEFAULT_PAGE_SIZE)

    facetids = c.facet(
        bvn=facet_name, ansvarlig=orgid,
        publiceret='Publiceret',
    )

    assert len(facetids) <= 1, 'Facet is not unique'

    return flask.jsonify(
        facetids and get_one_facet(
            c,
            facetids[0],
            facet,
            orgid,
            data=c.klasse.paged_get(get_one_class,
                                    facet=facetids,
                                    ansvarlig=orgid,
                                    publiceret='Publiceret',
                                    start=start, limit=limit),
        ))
