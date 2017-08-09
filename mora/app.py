#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import traceback

import flask

from . import cli
from . import lora
from . import util
from .converters import addr
from .converters import reading
from .converters import writing

basedir = os.path.dirname(__file__)
staticdir = os.path.join(basedir, 'static')

app = flask.Flask(__name__, static_url_path='')

cli.load_cli(app)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    stack = traceback.format_exc()
    data = flask.request.get_json()

    if data:
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

    status_code = 400 if isinstance(error, ValueError) else 500

    return flask.jsonify({
        'status': status_code,
        'message': str(error),
        'context': stack,
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
    r = lora.login(user, flask.request.get_json()['password'])

    if r:
        return flask.jsonify(r)
    else:
        return '', 401


@app.route('/service/user/<user>/logout', methods=['POST'])
def logout(user):
    return flask.jsonify(
        lora.logout(user, flask.request.headers['X-AUTH-TOKEN'])
    )


@app.route('/acl/', methods=['POST', 'GET'])
def acl():
    return flask.jsonify([])


@app.route('/o/')
def list_organisations():
    return flask.jsonify(reading.list_organisations())


# --- Writing to LoRa --- #


@app.route('/o/<uuid:orgid>/org-unit', methods=['POST'])
def create_organisation_unit(orgid):
    req = flask.request.get_json()
    org_unit = writing.create_org_unit(req)
    uuid = lora.create('organisation/organisationenhed', org_unit)

    # If an end date is set for the org unit, inactivate it automatically
    # from this date
    if 'valid-to' in req:
        org_unit = writing.inactivate_org_unit(req['valid-from'],
                                               req['valid-to'])
        lora.update('organisation/organisationenhed/%s' % uuid, org_unit)

    return flask.jsonify({'uuid': uuid}), 201


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['DELETE'])
@util.restrictargs('endDate')
def inactivate_org_unit(orgid, unitid):
    update_url = 'organisation/organisationenhed/%s' % unitid

    # Keep the calls to LoRa in app.py (makes it easier to test writing.py)
    org_unit = lora.organisationenhed.get(uuid=unitid, virkningfra='-infinity',
                                          virkningtil='infinity')
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
    payload = writing.inactivate_org_unit(startdate,
                                          flask.request.args.get('endDate'))
    lora.update(update_url, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/actions/move',
           methods=['POST'])
@util.restrictargs()
def move_org_unit(orgid, unitid):
    # TODO: refactor common behavior from this route and the one below

    req = flask.request.get_json()
    payload = writing.move_org_unit(req)

    lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['POST'])
@util.restrictargs('rename')
def rename_or_retype_org_unit(orgid, unitid):
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
    # TODO: write test for this

    req = flask.request.get_json()

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
        flask.current_app.logger.error('sub-tree searching is unsupported!')
        return '', 400

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
            return flask.jsonify(reading.wrap_in_org(str(orgid), r[0]))
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
@util.restrictargs()
def get_orgunit_history(orgid, unitid):
    r = reading.unit_history(str(orgid), str(unitid))

    return flask.jsonify(list(r)) if r else ('', 404)


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/<role>/')
def get_role(orgid, unitid, role):
    # if role not in ['contact-channel', 'location']:
    #     return flask.jsonify([]), 400

    validity = flask.request.args.get('validity')

    getters = {
        'contact-channel': reading.get_contact_channels,
        'location': reading.get_locations,
    }

    if role not in getters:
        flask.current_app.logger.warn('unsupported role {!r}'.format(role))
        return flask.jsonify([]), 400

    r = getters[role](unitid, validity=validity)

    if r:
        return flask.jsonify(r)
    else:
        return '', 404


#
# Classification stuff - should be moved to own file
#

# This one is used when creating new "Enheder"
@app.route('/org-unit/type')
def list_classes():
    return flask.jsonify(reading.get_classes())


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
    # This yields three options in the original Mock test:
    # internal-only, external and unlisted. (In Danish: “Må vises
    # internt”, “Må vises eksternt” and “Hemmligt”.)
    return flask.jsonify(reading.get_contact_properties())


@util.restrictargs(required=['facetKey'])
@app.route('/role-types/contact/facets/type/classes/')
def get_contact_facet_types_classes():
    key = flask.request.args['facetKey']
    assert key == 'Contact_channel_location', 'unknown key: ' + key

    return flask.jsonify(reading.get_contact_types())
