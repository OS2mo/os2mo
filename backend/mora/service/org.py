#
# Copyright (c) Magenta ApS
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

import flask
import werkzeug

from .. import common
from .. import mapping
from .. import util

blueprint = flask.Blueprint('organisation', __name__, static_url_path='',
                            url_prefix='/service')

# The one and only os2mo/lora organisation


def organisation():
    app = flask.current_app
    return {
        'name': app.config["ORGANISATION_NAME"],
        'user_key': app.config["ORGANISATION_USER_KEY"],
        'uuid': app.config["ORGANISATION_UUID"],
    }


def check_config(app):
    """ put mora default organization into configuration before doing any work
        we mean to always set the organisation from the database, and it is
        safe to do as long as we have only one organization in lora database
        which satisfies the demands in 'list_organisations'
    """
    orglist = get_valid_organisations()

    if not len(orglist) < 2:
        raise IndexError("at most one organisation allowed in backend")

    # in prod, all values must be defined

    if app.env == 'production' and not (
        app.config.get("ORGANISATION_NAME") and
        app.config.get("ORGANISATION_USER_KEY") and
        app.config.get("ORGANISATION_UUID")
    ):
        raise KeyError(
            "ORGANISATION_NAME, ORGANISATION_USER_KEY, "
            "and ORGANISATION_UUID must be configured"
        )

    # if values are defined they must match org in lora

    if len(orglist) == 1:
        expected = orglist[0]
        actual = {
            'name': app.config.get("ORGANISATION_NAME", ""),
            'user_key': app.config.get("ORGANISATION_USER_KEY", ""),
            'uuid': app.config.get("ORGANISATION_UUID", ""),
        }

        bad_values = [
            ("ORGANISATION_" + k.upper(), v)
            for k, v in actual.items()
            if v and v != expected[k]
        ]
        if len(bad_values):
            raise ValueError(
                "The following configuration values "
                "do not match database: %r" % bad_values
            )

    # for test/dev we will pick the organisation already present in os2mo

    if app.env != 'production':
        app.config["ORGANISATION_UUID"] = orglist[0]["uuid"]
        app.config["ORGANISATION_NAME"] = orglist[0]["name"]
        app.config["ORGANISATION_USER_KEY"] = orglist[0]["user_key"]


def get_lora_organisation(c, orgid, org=None):
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


def get_valid_organisations():
    """ return all valid organisations, being the ones
        who have at least one top organisational unit
    """
    c = common.lora.Connector()
    orglist = [
        get_lora_organisation(c, orgid, org)
        for orgid, org in c.organisation.get_all(bvn='%')
        if c.organisationenhed(overordnet=orgid, gyldighed='Aktiv')
    ]
    return orglist


@blueprint.route('/o/')
@util.restrictargs('at')
def list_organisations():
    '''List displayable organisations. This endpoint is retained for
    backwards compatibility. It will always return a list of only one
    organisation - namely the one that is defined in the configuration
    values ORGANISATION_NAME, ORGANISATION_UUID, and ORGANISATION_UUID.

    .. :quickref: Organisation; List

    :queryparam date at: Show organisations at this point in time,
        in ISO-8601 format. This parameter is retained for backwards
        compatibility. There can be only one organisation defined
        at any point in time

    :<jsonarr string name: Human-readable name of the organisation.
    :<jsonarr string user_key: Short, unique key identifying the unit.
    :<jsonarr string uuid: Machine-friendly UUID of the organisation.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

     [
       {
         "name": "Hj\u00f8rring Kommune",
         "user_key": "Hj\u00f8rring Kommune",
         "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575"
       }
     ]

    '''
    return flask.jsonify([organisation()])


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
       "association_count": 24,
       "child_count": 2,
       "engagement_count": 111,
       "leave_count": 0,
       "manager_count": 41,
       "name": "Hj\u00f8rring Kommune",
       "person_count": 132,
       "role_count": 22,
       "unit_count": 67,
       "user_key": "Hj\u00f8rring Kommune",
       "uuid": "8d79e880-02cf-46ed-bc13-b5f73e478575"
     }

    '''

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
