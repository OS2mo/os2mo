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
import itertools
import uuid

import flask
import werkzeug

from .. import util
from . import common

blueprint = flask.Blueprint('facet', __name__, static_url_path='',
                            url_prefix='/service')

FACETS = {
    'address': 'Adressetype',
    'job-title': 'Stillingsbetegnelse',
    'ou': 'Enhedstype',
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
          "desc": "List available address types.",
          "name": "address",
          "path": "/service/f/address/"
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
                                      facet=facetid),

            })

    return flask.jsonify(sorted(
        r,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f['name']),
    ))


def _convert_class(classid, clazz):
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
def get_classes(orgid: uuid.UUID, facet: uuid.UUID):
    '''List classes available in the given facet.

    .. :quickref: Facet; Get

    :param uuid orgid: Restrict search to this organisation.
    :param string facet: One of the facet names listed by
        :http:get:`/service/f/`

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
            _convert_class,
            c.klasse.get_all(facet=facetids, ansvarlig=str(orgid),
                             start=start, limit=limit),
        ),
        # use locale-aware sorting
        key=lambda c: locale.strxfrm(c['name']),
    ))


def get_class(uuid):
    c = common.get_connector()

    cls = c.klasse.get(uuid=uuid)

    return cls and _convert_class(uuid, cls)
