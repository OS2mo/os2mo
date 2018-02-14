#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Organisation
------------

This section describes how to interact with organisations and
organisational units.

'''

import enum
import operator

import flask
import werkzeug

from .. import util
from . import common
from . import keys

blueprint = flask.Blueprint('organisation', __name__, static_url_path='',
                            url_prefix='/service')


def get_one_organisation(c, orgid, org=None):
    if not org:
        org = c.organisation.get(orgid)

    attrs = org['attributter']['organisationegenskaber'][0]

    return {
        'name': attrs['organisationsnavn'],
        'user_key': attrs['brugervendtnoegle'],
        'uuid': orgid,
    }


@blueprint.route('/o/')
@util.restrictargs('at')
def list_organisations():
    '''List displayable organisations. We consider anything that has *at
    least one* root unit 'displayable'.

    .. :quickref: Organisation; List

    :queryparam date at: Current time in ISO-8601 format.

    :<jsonarr string name: Human-readable name of the organisation.
    :<jsonarr string user_key: Short, unique key identifying the unit.
    :<jsonarr string uuid: Machine-friendly UUID of the organisation.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Aarhus Kommune",
          "user_key": "AARHUS",
          "uuid": "59141156-ed0b-457c-9535-884447c5220b"
        },
        {
          "name": "Ballerup Kommune",
          "user_key": "BALLERUP",
          "uuid": "3a87187c-f25a-40a1-8d42-312b2e2b43bd"
        }
      ]

    '''
    c = common.get_connector()

    return flask.jsonify(sorted(
        (
            get_one_organisation(c, orgid, org)
            for orgid, org in c.organisation.get_all(bvn='%')
            if c.organisationenhed(overordnet=orgid, gyldighed='Aktiv')
        ),
        key=operator.itemgetter('name'),
    ))


@blueprint.route('/o/<uuid:orgid>/')
@util.restrictargs('at')
def get_organisation(orgid):
    '''Obtain the initial level of an organisation.

    .. :quickref: Organisation; Getter

    :queryparam date at: Current time in ISO-8601 format.

    :<json string name: Human-readable name of the organisation.
    :<json string user_key: Short, unique key identifying the unit.
    :<json string uuid: Machine-friendly UUID of the organisation.
    :<json int child_count: Number of org. units nested immediately beneath
                            the organisation.
    :<json int person_count: Amount of people belonging to this organisation.
    :<json int unit_count: Amount of units belonging to this organisation.
    :<json int employment_count: Amount of employments in this organisation?

    :status 200: Whenever the organisation exists and is readable.
    :status 404: When no such organisation exists.

    **Example Response**:

    .. sourcecode:: json

      {
        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
        "name": "Aarhus Universitet",
        "user_key": "AU",
        "person_count": 2,
        "child_count": 1,
        "unit_count": 6,
        "employment_count": 1,
        'association_count': 1,
        'leave_count': 1,
        'role_count': 1,
        'manager_count': 1
      }

    '''

    orgid = str(orgid)
    c = common.get_connector()

    org = c.organisation.get(orgid)

    try:
        attrs = org['attributter']['organisationegenskaber'][0]
    except (KeyError, TypeError):
        raise werkzeug.exceptions.NotFound

    units = c.organisationenhed(tilhoerer=orgid, gyldighed='Aktiv')
    children = c.organisationenhed(overordnet=orgid, gyldighed='Aktiv')

    # FIXME: we should filter for activity, but that's extremely slow
    # 0.8s -> 12.3s for 28k users and 33k functions
    # https://redmine.magenta-aps.dk/issues/21273
    users = c.bruger(tilhoerer=orgid)
    engagements = c.organisationfunktion(tilknyttedeorganisationer=orgid,
                                         funktionsnavn=keys.ENGAGEMENT_KEY)
    associations = c.organisationfunktion(tilknyttedeorganisationer=orgid,
                                          funktionsnavn=keys.ASSOCIATION_KEY)
    leaves = c.organisationfunktion(tilknyttedeorganisationer=orgid,
                                    funktionsnavn=keys.LEAVE_KEY)
    roles = c.organisationfunktion(tilknyttedeorganisationer=orgid,
                                   funktionsnavn=keys.ROLE_KEY)
    managers = c.organisationfunktion(tilknyttedeorganisationer=orgid,
                                      funktionsnavn=keys.MANAGER_KEY)

    return flask.jsonify({
        'name': attrs['organisationsnavn'],
        'user_key': attrs['brugervendtnoegle'],
        'uuid': orgid,
        'child_count': len(children),
        'unit_count': len(units),
        'person_count': len(users),
        'employment_count': len(engagements),
        'association_count': len(associations),
        'leave_count': len(leaves),
        'role_count': len(roles),
        'manager_count': len(managers),
    })


@enum.unique
class UnitDetails(enum.Enum):
    # name & userkey only
    MINIMAL = 0

    # with organisation
    ORG = 1

    # with child count
    NCHILDREN = 2

    # with children and parent
    FULL = 3


def get_one_orgunit(c, unitid, unit=None,
                    details=UnitDetails.NCHILDREN) -> dict:
    '''Internal API for returning one organisation unit.

    '''

    if not unit:
        unit = c.organisationenhed.get(unitid)

        if not unit:
            return None

    attrs = unit['attributter']['organisationenhedegenskaber'][0]
    rels = unit['relationer']

    r = {
        'name': attrs['enhedsnavn'],
        'user_key': attrs['brugervendtnoegle'],
        'uuid': unitid,
    }

    if details is UnitDetails.ORG:
        r[keys.ORG] = get_one_organisation(c, rels['tilhoerer'][0]['uuid'])

    elif details is UnitDetails.NCHILDREN:
        children = c.organisationenhed(overordnet=unitid, gyldighed='Aktiv')

        r['child_count'] = len(children)

    elif details is UnitDetails.FULL:
        r['parent'] = get_one_orgunit(c, rels['overordnet'][0]['uuid'],
                                      details=UnitDetails.MINIMAL)

        r['children'] = [
            get_one_orgunit(c, childid, child)
            for childid, child in
            c.organisationenhed.get_all(overordnet=unitid, gyldighed='Aktiv')
        ]
        r['children'].sort(key=operator.itemgetter('name'))

    return r


@blueprint.route('/<any(o,ou):type>/<uuid:parentid>/children')
@util.restrictargs('at')
def get_children(type, parentid):
    '''Obtain the list of nested units within an organisation or an
    organisational unit.

    .. :quickref: Unit; Children

    :param type: 'o' if the parent is an organistion, and 'ou' if it's a unit.
    :param uuid parentid: The UUID of the parent.

    :queryparam date at: Current time in ISO-8601 format.

    :<jsonarr string name: Human-readable name of the unit.
    :<jsonarr string user_key: Short, unique key identifying the unit.
    :<jsonarr uuid uuid: Machine-friendly UUID of the unit.
    :<jsonarr int child_count: Number of org. units nested immediately beneath
                               the organisation.

    :status 200: Whenever the organisation or unit exists and is readable.
    :status 404: When no such organisation or unit exists, or the
                 parent was of the wrong type.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Humanistisk fakultet",
          "user_key": "hum",
          "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
          "child_count": 2
        },
        {
          "name": "Samfundsvidenskabelige fakultet",
          "user_key": "samf",
          "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
          "child_count": 0
        }
      ]

    '''
    c = common.get_connector()

    if type == 'o':
        scope = c.organisation
    else:
        assert type == 'ou'
        scope = c.organisationenhed

    obj = scope.get(parentid)

    if not obj or not obj.get('attributter'):
        raise werkzeug.exceptions.NotFound

    children = [
        get_one_orgunit(c, childid, child)
        for childid, child in
        c.organisationenhed.get_all(overordnet=parentid,
                                    gyldighed='Aktiv')
    ]

    children.sort(key=operator.itemgetter('name'))

    return flask.jsonify(children)


@blueprint.route('/ou/<uuid:unitid>/')
@util.restrictargs('at', 'validity')
def get_orgunit(unitid):
    '''Retrieve an organisational unit.

    .. :quickref: Unit; Get

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam string validity: Only show *past*, *present* or
        *future* values -- which the default being to show *present*
        values.

    :<json string name: Human-readable name.
    :<json string uuid: Machine-friendly UUID.
    :<json string user_key: Short, unique key identifying the unit.
    :<json object org: The organisation that this unit belongs to, as
        yielded by :http:get:`/service/o/`.

    :status 404: If the organisational unit isn't found.
    :status 200: Otherwise.

    **Example Response**:

    .. sourcecode:: json

      {
        "name": "Ballerup Kommune",
        "org": {
          "name": "Ballerup Kommune",
          "user_key": "Ballerup Kommune",
          "uuid": "3a87187c-f25a-40a1-8d42-312b2e2b43bd"
        },
        "user_key": "BALLERUP",
        "uuid": "9f42976b-93be-4e0b-9a25-0dcb8af2f6b4"
      }

    '''
    c = common.get_connector()

    r = get_one_orgunit(c, unitid, details=UnitDetails.ORG)

    if r:
        return flask.jsonify(r)
    else:
        raise werkzeug.exceptions.NotFound('no such unit')


@blueprint.route('/ou/<uuid:unitid>/tree')
@util.restrictargs('at')
def get_orgunit_tree(unitid):
    '''Retrieve information about an organisational unit, including parent
    and children.

    .. :quickref: Unit; Tree

    :queryparam date at: Current time in ISO-8601 format.

    :<json string name: Human-readable name.
    :<json string uuid: Machine-friendly UUID.
    :<json string user_key: Short, unique key identifying the unit.
    :<json array children: Array of child units, as output by
        :http:get:`/service/ou/(uuid:unitid)/`.
    :<json object parent: Parent unit, as output by
        :http:get:`/service/ou/(uuid:unitid)/` or ``null`` if this the
        top-most unit.

    :status 404: If the organisational unit isn't found.
    :status 200: Otherwise.

    **Example Response**:

    .. sourcecode:: json

      {
        "children": [
          {
            "child_count": 0,
            "name": "Filosofisk Institut",
            "user_key": "fil",
            "uuid": "85715fc7-925d-401b-822d-467eb4b163b6"
          },
          {
            "child_count": 1,
            "name": "Historisk Institut",
            "user_key": "hist",
            "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa"
          }
        ],
        "name": "Humanistisk fakultet",
        "parent": {
          "name": "Overordnet Enhed",
          "user_key": "root",
          "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"
        },
        "user_key": "hum",
        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
      }

    '''
    c = common.get_connector()

    return flask.jsonify(get_one_orgunit(c, unitid, details=UnitDetails.FULL))


@blueprint.route('/o/<uuid:orgid>/ou/')
@util.restrictargs('at', 'start', 'limit', 'query')
def list_orgunits(orgid):
    '''Query organisational units in an organisation.

    .. :quickref: Unit; List & search

    :param uuid orgid: UUID of the organisation to search.

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by units matching this string.

    :<jsonarr string name: Human-readable name.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string user_key: Short, unique key identifying the unit.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Samfundsvidenskabelige fakultet",
          "user_key": "samf",
          "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0"
        }
      ]

    '''
    c = common.get_connector()

    args = flask.request.args

    kwargs = dict(
        limit=int(args.get('limit', 0)) or 20,
        start=int(args.get('start', 0)) or 0,
    )

    if 'query' in args:
        kwargs.update(vilkaarligattr='%{}%'.format(args['query']))

    return flask.jsonify([
        get_one_orgunit(c, unitid, unit, details=UnitDetails.MINIMAL)
        for unitid, unit in c.organisationenhed.get_all(
            tilhoerer=str(orgid),
            gyldighed='Aktiv',
            **kwargs,
        )
    ])
