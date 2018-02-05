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

import functools
import itertools
import locale
import uuid

import flask
import werkzeug

from . import common
from .keys import ADDRESS_TYPE, JOB_FUNCTION, ORG_UNIT_TYPE, ASSOCIATION_TYPE
from .. import util

blueprint = flask.Blueprint('facet', __name__, static_url_path='',
                            url_prefix='/service')

FACETS = {
    ADDRESS_TYPE: 'Adressetype',
    JOB_FUNCTION: 'Stillingsbetegnelse',
    ASSOCIATION_TYPE: 'Tilknytningstype',
    ORG_UNIT_TYPE: 'Enhedstype',
}


@blueprint.route('/o/<uuid:orgid>/f/')
@util.restrictargs()
def list_facets(orgid):
    '''List the facet types available in a given organisation.

    :param uuid orgid: Restrict search to this organisation.

    .. :quickref: Facet; List types

    :>jsonarr string name: The facet name.
    :>jsonarr string path: The location on the web server.
    :>jsonarr string desc: Human readable description.

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

    for facet_name, facet_key in FACETS.items():
        for facetid, facet in c.facet.get_all(bvn=facet_key,
                                              ansvarlig=str(orgid)):
            r.append({
                'uuid': facetid,

                'name': facet_name,

                'user_key':
                facet['attributter']
                ['facetegenskaber'][0]
                ['brugervendtnoegle'],

                'path': flask.url_for('facet.get_classes', orgid=orgid,
                                      facet=facet_name),

            })

    return flask.jsonify(sorted(
        r,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f['name']),
    ))


def get_one_class(c, classid, clazz=None):
    if not clazz:
        clazz = c.klasse.get(classid)

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

    **Scopes**:

    .. list-table::
      :header-rows: 1

      * - Key
        - Description
      * - ``"DAR"``
        - UUID of a `DAR address`_, as found through the API. Please
          note that this requires performing separate calls to convert
          this value to and from human-readable strings.
      * - ``"EMAIL"``
        - An email address, as specified by :rfc:`5322#section-3.4`.
      * - ``"INTEGER"``
        - A integral number.
      * - ``"PHONE"``
        - A phone number.
      * - ``"TEXT"``
        - Arbitrary text.
      * - ``"WWW"``
        - An HTTP or HTTPS URL, as specified by :rfc:`1738`.

    .. _DAR address: http://dawa.aws.dk/dok/api/adresse


    **Example Response**:

    .. sourcecode:: json

      [
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
      ]

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
    limit = int(flask.request.args.get('limit') or 1000)

    facetids = c.facet(bvn=facet_name, ansvarlig=str(orgid))

    return flask.jsonify(facetids and sorted(
        itertools.starmap(
            functools.partial(get_one_class, c),
            c.klasse.get_all(facet=facetids, ansvarlig=str(orgid),
                             start=start, limit=limit),
        ),
        # use locale-aware sorting
        key=lambda c: locale.strxfrm(c['name']),
    ))
