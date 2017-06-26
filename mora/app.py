#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import operator
import os
import requests
import traceback
import uuid

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
        org_unit = writing.inactivate_org_unit(req['valid-to'])
        lora.update('organisation/organisationenhed/%s' % uuid, org_unit)

    return flask.jsonify({'uuid': uuid}), 201


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['DELETE'])
@util.restrictargs('endDate')
def inactivate_org_unit(orgid, unitid):
    payload = writing.inactivate_org_unit(flask.request.args.get('endDate'))
    lora.update('organisation/organisationenhed/%s' % unitid, payload)

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
def rename_org_unit(orgid, unitid):
    rename = flask.request.args.get('rename', None)

    # Make sure the rename param is present and set to true
    assert rename == 'true'

    req = flask.request.get_json()

    payload = writing.rename_org_unit(req)
    lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location',
    methods=['POST'],
)
@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location/<uuid:roleid>',
    methods=['POST'],
)
def update_organisation_unit_location(orgid, unitid, roleid=None):
    # TODO: write test for this

    req = flask.request.get_json()
    roletype = req.get('role-type')

    kwargs = writing.create_update_kwargs(roletype, req)
    payload = writing.update_org_unit_addresses(
        unitid, roletype, **kwargs)

    if payload['relationer']['adresser']:
        lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify(unitid), 200


@app.route('/o/<uuid:orgid>/full-hierarchy')
@util.restrictargs('treeType', 'orgUnitId', 'effective-date')
def full_hierarchy(orgid):

    # TODO: the 'effective-date' parameter is not used below, but it is
    # set by the frontend when moving an org unit - we could choose to
    # remove it from the frontend call

    args = flask.request.args

    treeType = args.get('treeType', None)

    if treeType == 'specific':
        return flask.jsonify(
            reading.full_hierarchy(str(orgid), args['orgUnitId'])['children'],
        )

    else:
        return flask.jsonify(reading.wrap_in_org(
            str(orgid),
            reading.full_hierarchies(str(orgid), str(orgid))[0],
        ))


@app.route('/o/<uuid:orgid>/org-unit/')
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/')
@util.restrictargs('query', 'validity', 'effective-date')
def get_orgunit(orgid, unitid=None):

    # TODO: the 'effective-date' parameter is not used below, but it is
    # set by the frontend when renaming an org unit - we could choose to
    # remove it from the frontend call

    query = flask.request.args.get('query', None)
    params = {
        'tilhoerer': str(orgid),
    }

    if query:
        assert unitid is None, 'unitid and query are both set!'

        try:
            params['uuid'] = str(uuid.UUID(query))
        except ValueError:
            # If the query is not an UUID, search for an org unit name instead
            params['enhedsnavn'] = query
    else:
        params['uuid'] = unitid

    validity = flask.request.args.get('validity', 'present')

    return flask.jsonify([
        reading.full_hierarchy(
            str(orgid), orgunitid,
            include_children=False, include_parents=True,
            include_activename=True,
        )
        for orgunitid in lora.organisationenhed(**params)
    ])


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/<role>/')
def get_role(orgid, unitid, role):
    if role not in ['contact-channel', 'location']:
        return flask.jsonify([]), 400

    validity = flask.request.args.get('validity')

    try:
        orgunit = lora.organisationenhed.get(unitid, validity)
    except ValueError:
        traceback.print_exc()
        return '', 404

    if role == 'contact-channel':
        PHONE_PREFIX = 'urn:magenta.dk:telefon:'
        return flask.jsonify([
            {
                "contact-info": addr['urn'][len(PHONE_PREFIX):],
                # "name": "telefon 12345678",
                'location': {
                    'uuid': '00000000-0000-0000-0000-000000000000',
                },
                "type": {
                    "name": "Telefonnummer",
                    "user-key": "Telephone_number",
                    "prefix": "urn:magenta.dk:telefon:",
                },
                "valid-from": addr['virkning']['from'],
                "valid-to": addr['virkning']['to'],
            }
            for addr in orgunit['relationer']['adresser']
            if addr.get('urn', '').startswith(PHONE_PREFIX)
        ])
    elif role == 'location':
        def convert_addr(addrobj):
            # TODO: can we live with struktur=mini?
            addrinfo = addr.get_address(addrobj['uuid'])

            return {
                "location": {
                    "name": addrinfo['adressebetegnelse'],
                    "user-key": addrinfo['kvhx'],
                    "uuid": addrinfo['id'],
                    "valid-from": addrinfo['historik']['oprettet'],
                    "valid-to": "infinity"
                },
                "name": addrinfo['adressebetegnelse'],
                "org-unit": unitid,
                "primaer": True,  # TODO: really?
                "role-type": "location",
                "uuid": addrinfo['id'],
                "valid-from": addrobj['virkning']['from'],
                "valid-to": addrobj['virkning']['to'],
            }

        return flask.jsonify([
            convert_addr(addr)
            for addr in orgunit['relationer']['adresser']
            if addr.get('uuid', '')
        ])


#
# Classification stuff - should be moved to own file
#

# This one is used when creating new "Enheder"
@app.route('/org-unit/type')
def list_classes():
    # TODO: we need to somehow restrict the available classes to
    # sensible options; a classification hierarchy, perhaps, or only
    # those related to or listed in our organisation?
    clazzes = lora.klasse(uuid=lora.klasse(bvn='%'))

    # TODO: Refactor this convert function into a module and make it
    # generic
    def convert(clazz):
        reg = clazz['registreringer'][-1]
        attrs = reg['attributter']['klasseegenskaber'][0]
        return {
            'uuid': clazz['id'],
            'name': attrs['titel'],
            'userKey': attrs['brugervendtnoegle']
        }

    return flask.jsonify(sorted(map(convert, clazzes),
                                key=operator.itemgetter('name')))


@app.route('/addressws/geographical-location')
@util.restrictargs('local', required=['vejnavn'])
def get_geographical_addresses():
    return flask.jsonify(
        addr.autocomplete_address(flask.request.args['vejnavn'],
                                  flask.request.args.get('local')),
    )


@app.route('/role-types/contact/facets/properties/classes/')
def get_contact_facet_properties_classes():
    # This yields three options in the original Mock test:
    # internal-only, external and unlisted. (In Danish: “Må vises
    # internt”, “Må vises eksternt” and “Hemmligt”.)
    return flask.jsonify([
        {
            "name": "N/A",
            "user-key": "N/A",
            "uuid": "00000000-0000-0000-0000-000000000000"
        },
    ])


@app.route('/role-types/contact/facets/type/classes/')
def get_contact_facet_types_classes():
    key = flask.request.args.get('facetKey')
    assert key == 'Contact_channel_location', 'unknown key: ' + key

    return flask.jsonify([
        {
            "name": "Phone Number",
            "prefix": "urn:magenta.dk:telefon:",
            "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
        },
    ])
