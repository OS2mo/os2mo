#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Legacy service layer
--------------------

This is the legacy service API retained for compatibility with the
original UI.

'''


import os

import flask

from . import lora, util, validator
from .converters import addr, reading, writing

basedir = os.path.dirname(__file__)
staticdir = os.path.join(basedir, 'static')

blueprint = app = flask.Blueprint('api', __name__, static_url_path='',
                                  url_prefix='/mo')

ROLE_TYPES = {
    'engagement': reading.get_engagements,
    'contact-channel': reading.get_contact_channels,
    # XXX: Hack to handle inconsistencies in API
    'contact': reading.get_contact_channels,
    'it': reading.get_it_systems,
    'location': reading.get_locations,
}
ROLE_TYPE_SUFFIX = '<any({}):role>/'.format(','.join(map(repr, ROLE_TYPES)))


@app.route('/o/')
def list_organisations():
    return flask.jsonify(reading.get_organisations())


@app.route('/o/<uuid:id>/')
@util.restrictargs()
def get_organisation(id):
    return flask.jsonify(reading.get_organisations(str(id))[0])


#
# EMPLOYEES
#

@app.route('/e/')
@util.restrictargs('limit', 'query', 'start')
def list_employees():
    limit = int(flask.request.args.get('limit', 100))
    start = int(flask.request.args.get('start', 0))
    query = flask.request.args.get('query')

    if util.is_cpr_number(query):
        search = {
            'tilknyttedepersoner': 'urn:dk:cpr:person:' + query,
        }

    elif query:
        search = {
            'vilkaarligattr': '%{}%'.format(query),
        }

    else:
        search = {
            'bvn': '%',
        }

    ids = reading.list_employees(
        limit=limit,
        start=start,
        **search,
    )

    r = reading.get_employees(ids[-limit:])

    return flask.jsonify(r) if r else ('', 404)


@app.route('/e/<int(fixed_digits=10):cpr_number>/')
@util.restrictargs()
def get_employee_by_cpr(cpr_number):
    ids = reading.list_employees(
        tilknyttedepersoner='urn:dk:cpr:person:{:010d}'.format(cpr_number),
    )

    if not ids:
        return flask.jsonify({
            'message': 'no such user',
        }), 404
    elif len(ids) > 1:
        return flask.jsonify({
            'message': 'multiple users found',
        }), 409

    return flask.jsonify(reading.get_employees(ids)[0])


@app.route('/e/<uuid:id>/')
@util.restrictargs()
def get_employee(id):
    return flask.jsonify(reading.get_employees([id])[0])


# --- Writing to LoRa --- #
@app.route('/e/<uuid:employeeid>/actions/role', methods=['POST'])
# XXX: Hack to handle inconsistencies in API
@app.route('/mo/e/<uuid:employeeid>/actions/role', methods=['POST'])
@app.route('/e/<uuid:employeeid>/role-types/' +
           ROLE_TYPE_SUFFIX.rstrip('/'), methods=['POST'])
def create_employee_role(employeeid, role=None):
    """
    Catch-all function for creating Employees roles

    :param employeeid:  Employee ID from MO. Not used.
    :return: The uuid of the employee and a HTTP status code.
    """

    def handle_request(role_type, req):
        handlers = {
            # 'association': create_association,
            # 'it': create_it,
            'contact': writing.create_contact,
            # 'leader': create_leader,
        }

        handler = handlers.get(role_type)

        if not handler:
            raise ValueError('unsupported role type {}'.format(role_type))

        handler(req)

    if role:
        req = flask.request.get_json()

        # set variables for consistency
        req.setdefault('role-type', role)
        req.setdefault('person', str(employeeid))

        handle_request(role, flask.request.get_json())

    else:
        for req in flask.request.get_json():
            handle_request(req.get('role-type'), req)

    return flask.jsonify(employeeid), 200


@app.route('/org-unit', methods=['POST'])
@app.route('/o/<uuid:orgid>/org-unit', methods=['POST'])
def create_organisation_unit(orgid=None):
    """
    Create a new org unit.

    :param orgid: The UUID of the organisation (not used, but given by the
        frontend).
    :return: JSON containing the new org unit UUID and the response status
        code.
    """

    req = flask.request.get_json()
    if not validator.is_create_org_unit_request_valid(req):
        return flask.jsonify(validator.ERRORS['create_org_unit']), 400

    org_unit = writing.create_org_unit(req)
    uuid = lora.create('organisation/organisationenhed', org_unit)

    return flask.jsonify({'uuid': uuid}), 201


@app.route('/org-unit/<uuid:unitid>', methods=['DELETE'])
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['DELETE'])
@util.restrictargs('endDate')
def inactivate_org_unit(unitid, orgid=None):
    """
    Inactivate an org unit.

    :param orgid: The UUID of the organisation (not used, but given by the
        frontend).
    :param unitid: The UUID of the org unit.
    :return: JSON containing the org unit UUID and the response status code.
    """

    enddate = flask.request.args.get('endDate')
    if not validator.is_inactivation_date_valid(str(unitid), enddate):
        return flask.jsonify(validator.ERRORS['inactivate_org_unit']), 400

    update_url = 'organisation/organisationenhed/%s' % unitid

    # Keep the calls to LoRa in app.py (makes it easier to test writing.py)
    org_unit = lora.get_org_unit(unitid)
    startdate = [
        g['virkning']['from'] for g in
        org_unit['tilstande']['organisationenhedgyldighed']
        if g['gyldighed'] == 'Aktiv'
    ]
    assert len(startdate) == 1  # We only support one active period for now
    startdate = startdate[0]

    # Delete org data for validity first - only way to do it in LoRa
    lora.update(update_url, {'tilstande': {'organisationenhedgyldighed': []}})

    # Then upload payload with actual virkninger
    payload = writing.inactivate_org_unit(startdate, enddate)
    lora.update(update_url, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/org-unit/<uuid:unitid>/actions/move', methods=['POST'])
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/actions/move',
           methods=['POST'])
@util.restrictargs()
def move_org_unit(unitid, orgid=None):
    """
    Move an org unit.

    :param orgid: The UUID of the organisation (not used, but given by the
        frontend).
    :param unitid: The UUID of the org unit.
    :return: JSON containing the org unit UUID and the response status code.
    """

    # TODO: refactor common behavior from this route and the one below

    req = flask.request.get_json()
    if not validator.is_candidate_parent_valid(str(unitid), req):
        return flask.jsonify(validator.ERRORS['rename_org_unit']), 400

    payload = writing.move_org_unit(req)
    lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/org-unit/<uuid:unitid>', methods=['POST'])
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['POST'])
@util.restrictargs('rename')
def rename_or_retype_org_unit(unitid, orgid=None):
    """
    Change the name or the type of an org unit.

    :param orgid: The UUID of the organisation.
    :param unitid: The UUID of the org unit.
    :return: JSON containing the org unit UUID and the response status code.
    """

    rename = flask.request.args.get('rename', None)

    req = flask.request.get_json()

    if rename:
        # Renaming an org unit
        payload = writing.rename_org_unit(req)
    else:
        # Changing the org units enhedstype
        assert req['type']
        payload = writing.retype_org_unit(req)

    lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/org-unit/<uuid:unitid>/role-types/location', methods=['POST'])
@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location',
    methods=['POST'],
)
@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location/<uuid:locid>',
    methods=['POST'],
)
def update_organisation_unit_location(orgid=None, unitid=None, locid=None):
    """
    Add a location or contact channel or update existing ones.

    :param orgid: The UUID of the organisation.
    :param unitid: The UUID of the org unit.
    :param locid: The UUID of the location (i.e. the address UUID).
    :return: JSON containing the org unit UUID and the response status code.
    """

    req = flask.request.get_json()
    if not validator.is_location_update_valid(req):
        return flask.jsonify(validator.ERRORS['update_existing_location']), 400

    kwargs = writing.create_update_kwargs(req)
    payload = writing.update_org_unit_addresses(
        unitid, **kwargs)

    if payload['relationer']['adresser']:
        lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/o/<uuid:orgid>/full-hierarchy')
@util.restrictargs('treeType', 'orgUnitId', 'query',
                   'effective-date', 't')
def full_hierarchy(orgid):
    args = flask.request.args

    params = dict(
        effective_date=args.get('effective-date', None),
    )

    if args.get('query'):
        # TODO: the query argument does sub-tree searching -- given
        # that LoRA has no notion of the organisation tree, we'd have
        # to emulate it
        raise ValueError('sub-tree searching is unsupported!')

    if args.get('treeType', None) == 'specific':
        r = reading.full_hierarchy(args['orgUnitId'], **params)

        if r:
            return flask.jsonify(
                r['children'],
            )
        else:
            return '', 404

    else:
        r = reading.full_hierarchies(str(orgid), str(orgid), **params)

        if r:
            c = lora.Connector(effective_date=args.get('effective-date', None))

            return flask.jsonify(reading.wrap_in_org(c, str(orgid), r[0]))
        else:
            return '', 404


@app.route('/o/<uuid:orgid>/org-unit/')
@util.restrictargs('query', 'validity', 'effective-date', 'limit', 'start',
                   't')
def list_orgunits(orgid):
    # TODO: we are not actually using the 't' parameter - we should
    # probably remove this from the frontend calls later on...

    limit = int(flask.request.args.get('limit', 100))
    start = int(flask.request.args.get('start', 0))
    query = flask.request.args.get('query')

    if util.is_uuid(query):
        search = {
            'uuid': query,
            # 'tilhoerer': orgid,
        }
    elif query:
        search = {
            'vilkaarligattr': '%{}%'.format(query),
            'tilhoerer': orgid,
        }
    else:
        search = {
            'tilhoerer': orgid,
        }

    unitids = reading.list_orgunits(
        limit=limit,
        start=start,
        **search,
        effective_date=flask.request.args.get('effective-date', None),
    )

    r = reading.get_orgunits(
        unitids,
        validity=flask.request.args.get('validity', None),
        include_parents=False,
    )

    return flask.jsonify(r) if r else ('', 404)


@app.route('/org-unit/<uuid:unitid>/')
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/')
@util.restrictargs('query', 'validity', 'effective-date', 'limit', 'start',
                   't')
def get_orgunit(unitid, orgid=None):
    # TODO: we are not actually using the 't' parameter - we should
    # probably remove this from the frontend calls later on...

    query = flask.request.args.get('query')

    if query:
        raise ValueError('sub-tree searching not supported!')

    r = reading.get_orgunits(
        [str(unitid)],
        validity=flask.request.args.get('validity', None),
    )

    return flask.jsonify(r) if r else ('', 404)


@app.route('/org-unit/<uuid:unitid>/history/')
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/history/')
@util.restrictargs('t')
def get_orgunit_history(unitid, orgid=None):
    # TODO: we are not actually using the 't' parameter - we should
    # probably remove this from the frontend calls later on...

    r = reading.unit_history(str(unitid))

    return flask.jsonify(list(r)) if r else ('', 404)


@app.route('/role-types/')
@util.restrictargs()
def list_roles():
    '''List the supported role types.

    .. :quickref: Roles; Available roles
    '''
    return flask.jsonify(sorted(ROLE_TYPES))


@app.route('/e/<uuid:userid>/role-types/' + ROLE_TYPE_SUFFIX)
@app.route('/org-unit/<uuid:unitid>/role-types/' + ROLE_TYPE_SUFFIX)
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/' +
           ROLE_TYPE_SUFFIX)
@util.restrictargs('effective-date', 'validity', 'unique', 't')
def get_role(role, **kwargs):
    '''Get the roles of an employee or organisational unit.

    :queryparam string validity: Only yield entries relevant to the
                                 past, present or future.
    :queryparam date effective-date: Set the "current" date for the
                                     time machine.
    :queryparam boolean unique: Retained for compatibility with original UI.
    :queryparam int t: Retained for compatibility with original UI.

    :param string role: The relevant role type, see :http:get:`/mo/role-types/`
    :param uuid userid: Optional employee UUID.
    :param uuid unitid: Optional unit UUID.
    :param uuid orgid: Optional organisation UUID, retained for compatibility
                       with original UI.

    .. :quickref: Roles; Get

    '''

    validity = flask.request.args.get('validity')
    effective_date = flask.request.args.get('effective-date')

    r = ROLE_TYPES[role](validity=validity,
                         effective_date=effective_date,
                         **kwargs)

    # XXX: Hack to handle inconsistencies in API
    if 'userid' in kwargs or r:
        return flask.jsonify(r)
    else:
        return '', 404


#
# Classification stuff - should be moved to own file
#

# This one is used when creating new "Enheder"
@app.route('/org-unit/type')
@util.restrictargs()
def list_classes():
    # TODO: require an organisation parameter

    return flask.jsonify(reading.get_classes("Enhedstype"))


@app.route(
    '/role-types/engagement/facets/<any("type", "job-title"):facet>/classes/',
)
@util.restrictargs()
def get_engagement_classes(facet):
    # TODO: require a unit or organisation parameter?

    facet_name = {
        "type": "Funktionstype",
        "job-title": "Stillingsbetegnelse",
    }[facet]

    return flask.jsonify(reading.get_classes(facet_name))


@app.route('/addressws/geographical-location')
@util.restrictargs('local', required=['vejnavn'])
def get_geographical_addresses():
    return flask.jsonify(
        addr.autocomplete_address(flask.request.args['vejnavn'],
                                  flask.request.args.get('local')),
    )


@app.route('/role-types/contact/facets/properties/classes/')
@util.restrictargs()
def get_contact_facet_properties_classes():
    return flask.jsonify(reading.get_contact_properties())


@app.route('/role-types/contact/facets/type/classes/')
@util.restrictargs('facetKey')
def get_contact_facet_types_classes():
    key = flask.request.args.get('facetKey')
    assert not key or key == 'Contact_channel_location', \
        'unknown key: ' + repr(key)

    return flask.jsonify(reading.get_contact_types())


@app.route('/o/<uuid:orgid>/it/')
# used when creating new "IT Systems"
@app.route('/it-system/')
# used when editing existing entries...
@app.route('/it/')
@util.restrictargs()
def list_itsystems(orgid=None):
    '''List the available IT systems.

    .. :quickref: IT systems; List

    :param string orgid: optional organisation UUID restricting the
                         search

    :>jsonarr string name: user-friendly name
    :>jsonarr string userKey: unique, human-readable identifyer
    :>jsonarr string uuid: unique, machine-friendly identifyer

    :status 200: Always, even if nothing found.
    :status 404: Not used.

    '''

    return flask.jsonify(reading.list_it_systems(orgid))
