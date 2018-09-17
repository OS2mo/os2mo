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

This section describes how to interact with organisations.

'''

import operator

import flask
import werkzeug

from .. import common
from .. import mapping
from .. import util

blueprint = flask.Blueprint('organisation', __name__, static_url_path='',
                            url_prefix='/service')


def get_one_organisation(c, orgid, org=None):
    if not org:
        org = c.organisation.get(orgid)

        if not org or not util.is_reg_valid(org):
            return None

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

    :queryparam date at: Show organisations at this point in time,
        in ISO-8601 format.

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

    :queryparam date at: Show the organisation at this point in time,
        in ISO-8601 format.

    :<json string name: Human-readable name of the organisation.
    :<json string user_key: Short, unique key identifying the unit.
    :<json string uuid: Machine-friendly UUID of the organisation.
    :<json int child_count: Number of org. units nested immediately beneath
                            the organisation.
    :<json int person_count: Amount of people belonging to this organisation.
    :<json int unit_count: Amount of units belonging to this organisation.
    :<json int employment_count: Amount of employments in this organisation.
    :<json int association_count: Amount of associations in this organisation.
    :<json int leave_count: Amount of leaves in this organisation.
    :<json int role_count: Amount of roles in this organisation.
    :<json int manager_count: Amount of managers in this organisation.

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
        "association_count": 1,
        "leave_count": 1,
        "role_count": 1,
        "manager_count": 1
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
                                         funktionsnavn=mapping.ENGAGEMENT_KEY)
    associations = c.organisationfunktion(
        tilknyttedeorganisationer=orgid,
        funktionsnavn=mapping.ASSOCIATION_KEY,
    )
    leaves = c.organisationfunktion(tilknyttedeorganisationer=orgid,
                                    funktionsnavn=mapping.LEAVE_KEY)
    roles = c.organisationfunktion(tilknyttedeorganisationer=orgid,
                                   funktionsnavn=mapping.ROLE_KEY)
    managers = c.organisationfunktion(tilknyttedeorganisationer=orgid,
                                      funktionsnavn=mapping.MANAGER_KEY)

    return flask.jsonify({
        'name': attrs['organisationsnavn'],
        'user_key': attrs['brugervendtnoegle'],
        'uuid': orgid,
        'child_count': len(children),
        'unit_count': len(units),
        'person_count': len(users),
        'engagement_count': len(engagements),
        'association_count': len(associations),
        'leave_count': len(leaves),
        'role_count': len(roles),
        'manager_count': len(managers),
    })
