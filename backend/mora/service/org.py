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
from .. import exceptions

blueprint = flask.Blueprint('organisation', __name__, static_url_path='',
                            url_prefix='/service')


class ConfiguredOrganisation:
    """ OS2mo organisation has been moved into configuration values
    this class validates the configured values before returning the
    configured values. Upon successful validation this is remembered
    until restart of the application. The rules are:
    - there can be at most 1 organisation in lora database
    - if the organisation values are configured they must be the same
      as the organisation in lora, if any
    - for production environment the organisation must be configured
    """
    valid = False

    @classmethod
    def validate(cls, app):
        orglist = get_valid_organisations()

        # if running production or no organisation in lora
        # organisation must be configured
        if (app.env == 'production' or len(orglist) == 0) and not (
            app.config.get("ORGANISATION_NAME") and
            app.config.get("ORGANISATION_USER_KEY") and
            app.config.get("ORGANISATION_UUID")
        ):
            exceptions.ErrorCodes.E_ORG_UNCONFIGURED()

        if len(orglist) > 1:
            exceptions.ErrorCodes.E_ORG_TOO_MANY(count=len(orglist))

        elif len(orglist) == 0:
            cls.valid = True
            return

        elif len(orglist) == 1:
            # check configuration values - dev/test may be blank
            # production is sure to be configured (see above)
            expected = orglist[0]
            actual = {
                'name': app.config.get("ORGANISATION_NAME", ""),
                'user_key': app.config.get("ORGANISATION_USER_KEY", ""),
                'uuid': app.config.get("ORGANISATION_UUID", ""),
            }
            bad_values = {
                "ORGANISATION_" + k.upper(): v
                for k, v in actual.items()
                if v and v != expected[k]
            }

            if bad_values:
                exceptions.ErrorCodes.E_ORG_CONFIG_BAD(**bad_values)

            # for blank test/dev values use org present in os2mo
            if app.env != 'production':
                app.config["ORGANISATION_UUID"] = orglist[0]["uuid"]
                app.config["ORGANISATION_NAME"] = orglist[0]["name"]
                app.config["ORGANISATION_USER_KEY"] = orglist[0]["user_key"]
            cls.valid = True
            return


def organisation():
    app = flask.current_app
    if not ConfiguredOrganisation.valid:
        ConfiguredOrganisation.validate(app)
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

    # in prod, all values must be defined

    if app.env == 'production' and not (
        app.config.get("ORGANISATION_NAME") and
        app.config.get("ORGANISATION_USER_KEY") and
        app.config.get("ORGANISATION_UUID")
    ):
        raise KeyError("Organisation not configured")


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
