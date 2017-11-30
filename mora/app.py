#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import os

import flask

from . import auth
from . import cli
from . import lora
from . import util
from . import validator
from .converters import addr
from .converters import reading
from .converters import writing

basedir = os.path.dirname(__file__)
staticdir = os.path.join(basedir, 'static')

app = flask.Flask(__name__, static_url_path='')

cli.load_cli(app)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    """
    Handles errors in case an exception is raised.

    :param error: The error raised.
    :return: JSON describing the problem and the apropriate status code.
    """
    data = flask.request.get_json()

    if data:
        if 'password' in data:
            data['password'] = 'X' * 8

        flask.current_app.logger.exception(
            'AN ERROR OCCURRED in %r:\n%s',
            flask.request.full_path,
            json.dumps(data, indent=2),
        )
    else:
        flask.current_app.logger.exception(
            'AN ERROR OCCURRED in %r',
            flask.request.full_path,
        )

    if isinstance(error, ValueError):
        status_code = 400
    elif isinstance(error, (KeyError, IndexError)):
        status_code = 404
    elif isinstance(error, PermissionError):
        status_code = 401
    else:
        status_code = 500

    return flask.jsonify({
        'status': status_code,
        'message': (
            error.args[0]
            if error.args and len(error.args) == 1
            else error.args
        )
    }), status_code


@app.route('/')
def root():
    return flask.send_from_directory(staticdir, 'index.html')


@app.route('/scripts/<path:path>')
def send_scripts(path):
    return flask.send_from_directory(staticdir, os.path.join('scripts', path))


@app.route('/styles/<path:path>')
def send_styles(path):
    return flask.send_from_directory(staticdir, os.path.join('styles', path))


@app.route('/service/user/<user>/login', methods=['POST'])
def login(user):
    return auth.login(user)


@app.route('/service/user/<user>/logout', methods=['POST'])
def logout(user):
    return auth.logout()


@app.route('/acl/', methods=['POST', 'GET'])
def acl():
    return flask.jsonify([])


@app.route('/o/')
def list_organisations():
    return flask.jsonify(reading.list_organisations())


#
# EMPLOYEES
#

@app.route('/e/')
@util.restrictargs('limit', 'query', 'start')
def list_employees():
    limit = int(flask.request.args.get('limit', 100))
    start = int(flask.request.args.get('start', 0))
    query = flask.request.args.get('query')

    ids = reading.list_employees(
        vilkaarligattr='%{}%'.format(query),
        limit=limit,
        start=start,
    )

    return flask.jsonify(
        reading.get_employees(
            ids,
        )
    )


@app.route('/e/<int:cpr_number>/')
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
        }), 404

    return flask.jsonify(reading.get_employees(ids)[0])


@app.route('/e/<uuid:id>/')
@util.restrictargs()
def get_employee(id):
    return flask.jsonify(reading.get_employees([id])[0])


# --- Writing to LoRa --- #


@app.route('/o/<uuid:orgid>/org-unit', methods=['POST'])
def create_organisation_unit(orgid):
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


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['DELETE'])
@util.restrictargs('endDate')
def inactivate_org_unit(orgid, unitid):
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


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/actions/move',
           methods=['POST'])
@util.restrictargs()
def move_org_unit(orgid, unitid):
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


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['POST'])
@util.restrictargs('rename')
def rename_or_retype_org_unit(orgid, unitid):
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


@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location',
    methods=['POST'],
)
@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location/<uuid:locid>',
    methods=['POST'],
)
def update_organisation_unit_location(orgid, unitid, locid=None):
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
        include_children=True,
    )

    if args.get('query'):
        # TODO: the query argument does sub-tree searching -- given
        # that LoRA has no notion of the organisation tree, we'd have
        # to emulate it
        raise ValueError('sub-tree searching is unsupported!')

    if args.get('treeType', None) == 'specific':
        r = reading.full_hierarchy(str(orgid), args['orgUnitId'], **params)

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
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/')
@util.restrictargs('query', 'validity', 'effective-date', 'limit', 'start',
                   't')
def get_orgunit(orgid, unitid=None):
    # TODO: we are not actually using the 't' parameter - we should
    # probably remove this from the frontend calls later on...

    query = flask.request.args.get('query')

    if bool(unitid) is bool(query) is True:
        raise ValueError('unitid and query cannot both be set!')

    unitids = reading.list_orgunits(
        unitid or query,
        tilhoerer=str(orgid),
        effective_date=flask.request.args.get('effective-date', None),
    )

    r = reading.get_orgunits(
        str(orgid), unitids,
        validity=flask.request.args.get('validity', None),
    )

    return flask.jsonify(r) if r else ('', 404)


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/history/')
@util.restrictargs('t')
def get_orgunit_history(orgid, unitid):
    # TODO: we are not actually using the 't' parameter - we should
    # probably remove this from the frontend calls later on...

    r = reading.unit_history(str(orgid), str(unitid))

    return flask.jsonify(list(r)) if r else ('', 404)


ROLE_TYPES = {
    'engagement': reading.get_engagements,
    'contact-channel': reading.get_contact_channels,
    'location': reading.get_locations,
}
ROLE_TYPE_SUFFIX = '<any({}):role>/'.format(','.join(map(repr, ROLE_TYPES)))


@app.route('/e/<uuid:userid>/role-types/' + ROLE_TYPE_SUFFIX)
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/' +
           ROLE_TYPE_SUFFIX)
@util.restrictargs('effective-date', 'validity', 't')
def get_role(role, **kwargs):
    validity = flask.request.args.get('validity')
    effective_date = flask.request.args.get('effective-date')

    r = ROLE_TYPES[role](validity=validity,
                         effective_date=effective_date,
                         **kwargs)

    if r:
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

    return flask.jsonify(reading.get_classes({
        "type": "Funktionstype",
        "job-title": "Stillingsbetegnelse",
    }[facet]))

    return flask.jsonify(reading.get_contact_types())


@app.route('/addressws/geographical-location')
@util.restrictargs('local', required=['vejnavn'])
def get_geographical_addresses():
    return flask.jsonify(
        addr.autocomplete_address(flask.request.args['vejnavn'],
                                  flask.request.args.get('local')),
    )


@util.restrictargs()
@app.route('/role-types/contact/facets/properties/classes/')
def get_contact_facet_properties_classes():
    return flask.jsonify(reading.get_contact_properties())


@util.restrictargs(required=['facetKey'])
@app.route('/role-types/contact/facets/type/classes/')
def get_contact_facet_types_classes():
    key = flask.request.args['facetKey']
    assert key == 'Contact_channel_location', 'unknown key: ' + key

    return flask.jsonify(reading.get_contact_types())
