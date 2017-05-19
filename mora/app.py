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
import requests

from . import lora
from . import util

basedir = os.path.dirname(__file__)
staticdir = os.path.join(basedir, 'static')

app = flask.Flask(__name__, static_url_path='')


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
    orgs = lora.organisation(uuid=lora.organisation(bvn='%'))

    def convert(org):
        reg = org['registreringer'][-1]
        attrs = reg['attributter']['organisationegenskaber'][0]
        return {
            'name': attrs['organisationsnavn'],
            'user-key': attrs['brugervendtnoegle'],
            'uuid': org['id'],
            'valid-from': attrs['virkning']['from'],
            'valid-to': attrs['virkning']['to'],
        }

    return flask.jsonify(list(map(convert, orgs)))


@app.route('/o/<uuid:orgid>/org-unit', methods=['POST'])
def create_organisation_unit(orgid):
    req = flask.request.get_json()

    virkning = {
        'from': util.reparsedate(req.get('valid-from'), '-infinity'),
        'to': util.reparsedate(req.get('valid-to'), 'infinity'),
    }

    nullrelation = [{
        'virkning': virkning,
    }]

    assert req['org'] == str(orgid)

    obj = {
        'attributter': {
            'organisationenhedegenskaber': [
                {
                    'enhedsnavn': req['name'],
                    'brugervendtnoegle': req['user-key'],
                    'virkning': virkning.copy(),
                },
            ],
        },
        'tilstande': {
            'organisationenhedgyldighed': [
                {
                    'gyldighed': 'Aktiv',
                    'virkning': virkning.copy(),
                },
            ],
        },
        'relationer': {
            'adresser': [
                {
                    'uuid': location['location']['UUID_EnhedsAdresse'],
                    'virkning': virkning.copy(),
                }
                for location in req.get('locations', [])
            ] + [
                {
                    'urn': 'urn:magenta.dk:telefon:{}'.format(
                        channel['contact-info'],
                    ),
                    'virkning': virkning.copy(),
                }
                for location in req.get('locations', [])
                for channel in location.get('contact-channels', [])
            ] or nullrelation,
            'tilhoerer': [
                {
                    'uuid': req['org'],
                    'virkning': virkning.copy(),
                }
            ],
            # 'tilknyttedeenheder': [
            #     {
            #         'urn': req['tilknyttedeenheder'],
            #         'virkning': virkning.copy(),
            #     }
            # ],
            'enhedstype': [
                {
                    'uuid': req['type']['uuid'],
                    'virkning': virkning.copy(),
                }
            ],
            'overordnet': [
                {
                    'uuid': req['parent'],
                    'virkning': virkning.copy(),
                }
            ],
        }
    }

    return lora.create('organisation/organisationenhed', obj), 201


# @app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['POST'])
# def update_organisation_unit(orgid, unitid):
#     req = flask.request.get_json()

#     import pprint
#     pprint.pprint(req)

#     return flask.jsonify(req), 500

@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location',
    methods=['POST'],
)
@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location/<uuid:roleid>',
    methods=['POST'],
)
def update_organisation_unit_location(orgid, unitid, roleid=None):
    req = flask.request.get_json()
    roletype = req.get('role-type')

    unitobj = lora.organisationenhed(uuid=unitid)[0]['registreringer'][-1]

    import json
    print(json.dumps(req, indent=2))
    print(json.dumps(unitobj, indent=2))

    if roletype == 'contact-channel':
        # TODO: the UI assigns the objects to a location, but since we map
        # locations to address UUIDs, we cannot do that; instead, we just
        # stash everything on the unit
        addresses = unitobj['relationer']['adresser']

        # TODO: handle empty relation
        addresses.extend([
            {
                'urn': info['type']['prefix'] + info['contact-info'],
                'virkning': {
                    'from': info['valid-from'],
                    'to': info['valid-to'],
                }
            }
            for info in req['contact-channels']
        ])

        lora.update('organisation/organisationenhed/{}'.format(unitid), {
            'relationer': {
                'adresser': addresses
            }
        })
    elif roletype == 'location':
        assert req['changed'], 'not changed?'

        lora.update('organisation/organisationenhed/{}'.format(unitid), {
            'relationer': {
                'adresser': [
                    addr if addr.get('uuid') != req['uuid'] else {
                        'uuid': (req['location'].get('UUID_EnhedsAdresse') or
                                 req['location']['uuid']),
                        'virkning': {
                            'from': util.reparsedate(req['valid-from']),
                            'to': util.reparsedate(req['valid-to']),
                        },
                    }
                    for addr in unitobj['relationer']['adresser']
                ]
            }
        })

    elif roletype:
        raise NotImplementedError(roletype)
    else:
        # direct creation of a location

        addresses = unitobj['relationer']['adresser']

        # TODO: handle empty relation
        addresses.append({
            'uuid': req['location']['UUID_EnhedsAdresse'],
            'virkning': {
                'from': util.reparsedate(
                    req['location'].get('valid-from') or req['valid-from']
                ),
                'to': util.reparsedate(
                    req['location'].get('valid-to') or req['valid-to']
                ),
            },
        })

        lora.update('organisation/organisationenhed/{}'.format(unitid), {
            'relationer': {
                'adresser': addresses
            }
        })

    return flask.jsonify(unitid), 201


@app.route('/o/<uuid:orgid>/full-hierarchy')
def full_hierarchy(orgid):
    args = flask.request.args
    treeType = args.get('treeType', None)

    org = lora.organisation(uuid=orgid)[0]

    if treeType == 'specific':
        overordnet = args['orgUnitId']
    elif not treeType:
        return flask.jsonify([]), 400
    else:
        overordnet = str(orgid)

    roots = lora.organisationenhed(tilhoerer=orgid, overordnet=overordnet)

    def convert_list(unitids):
        return sorted(map(convert, unitids), key=lambda r: r['name'].lower())

    def convert(unitid):
        orgunit = lora.organisationenhed(uuid=unitid)[0]
        reg = orgunit['registreringer'][-1]
        attrs = reg['attributter']['organisationenhedegenskaber'][0]
        rels = reg['relationer']

        children = lora.organisationenhed(tilhoerer=orgid, overordnet=unitid)
        is_root = rels['overordnet'][0]['uuid'] == str(orgid)

        return {
            'name': attrs['enhedsnavn'],
            'user-key': attrs['brugervendtnoegle'],
            'uuid': unitid,
            'valid-from': attrs['virkning']['from'],
            'valid-to': attrs['virkning']['to'],
            'hasChildren': bool(children),
            'children': (
                convert_list(children)
                if children and not treeType
                else []
            ),
            'org': str(orgid),
            'parent': rels['overordnet'][0]['uuid'] if not is_root else None,
        }

    if treeType == 'specific':
        return flask.jsonify(convert_list(roots))

    elif len(roots) == 1:
        root = convert(roots.pop())

        if root['parent']:
            return flask.jsonify(root)
        else:
            orgreg = org['registreringer'][-1]
            orgattrs = orgreg['attributter']['organisationegenskaber'][0]
            return flask.jsonify({
                'hierarchy': root,
                'name': orgattrs['organisationsnavn'],
                'user-key': orgattrs['brugervendtnoegle'],
                'uuid': org['id'],
                'valid-from': orgattrs['virkning']['from'],
                'valid-to': orgattrs['virkning']['to'],
            })

    else:
        return flask.jsonify(convert_list(roots))


@app.route('/o/<uuid:orgid>/org-unit/')
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/')
def get_orgunit(orgid, unitid=None):
    params = {
        'tilhoerer': orgid,
        'uuid': unitid or flask.request.args.get('query', []),
    }

    validity = flask.request.args.get('validity', 'present')

    orgunitids = set(lora.organisationenhed(**params))

    def convert(unitid):
        orgunit = lora.organisationenhed.get(unitid, validity)
        try:
            attrs = orgunit['attributter']['organisationenhedegenskaber'][0]
        except IndexError:
            return None

        rels = orgunit['relationer']

        childids = lora.organisationenhed(tilhoerer=orgid, overordnet=unitid)

        parentid = rels['overordnet'][0]['uuid']

        if parentid == str(orgid):
            parentid = None

        return {
            "activeName": attrs['enhedsnavn'],
            "hasChildren": bool(childids),
            "name": attrs['enhedsnavn'],
            "org": str(orgid),
            "parent": parentid,
            "parent-object": parentid and convert(parentid),
            "user-key": attrs['brugervendtnoegle'],
            "uuid": unitid,
            'valid-from': attrs['virkning']['from'],
            'valid-to': attrs['virkning']['to'],
        }

    return flask.jsonify(
        # for validity, filter out empty entries
        list(filter(None, [
            convert(orgunitid) for orgunitid in orgunitids
        ]))
    )


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
                "type": {
                    "name": "Telefonnummer",
                    "user-key": "Telephone_number",
                },
                "valid-from": addr['virkning']['from'],
                "valid-to": addr['virkning']['to'],
            }
            for addr in orgunit['relationer']['adresser']
            if addr.get('urn', '').startswith(PHONE_PREFIX)
        ])
    elif role == 'location':
        def convert_addr(addr):
            # TODO: can we live with struktur=mini?
            addrinfo = requests.get(
                'http://dawa.aws.dk/adresser/' + addr['uuid'],
                params={
                    'noformat': '1',
                },
            ).json()

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
                "valid-from": addr['virkning']['from'],
                "valid-to": addr['virkning']['to'],
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
    clazzes = lora.klasse(uuid=lora.klasse(bvn='%'))

    # TODO: Refactor this convert function (and the one used for orgs)
    # into a module and make it generic
    def convert(clazz):
        reg = clazz['registreringer'][-1]
        attrs = reg['attributter']['klasseegenskaber'][0]
        return {
            'uuid': clazz['id'],
            'name': attrs['titel'],
            'userKey': attrs['brugervendtnoegle']
        }

    return flask.jsonify(list(map(convert, clazzes)))


@app.route('/addressws/geographical-location')
@app.route('/addressws/geographical-location/<uuid:orgid>')
def get_geographical_addresses(orgid=None):
    # example output from runWithMocks:
    # [{
    #     "UUID_AdgangsAdresse": "0A3F507B-67A6-32B8-E044-0003BA298018",
    #     "UUID_EnhedsAdresse": "0A3F50A2-FA9D-32B8-E044-0003BA298018",
    #     "kommunenavn": "Ballerup",
    #     "kommunenr": "151",
    #     "koorNord": "6180286.02",
    #     "koorOest": "710570.98",
    #     "latitude": "55.7223788579",
    #     "longitude": "12.3529929726",
    #     "postdistrikt": "Ballerup",
    #     "postnr": "2750",
    #     "valid-from": "05-02-2000",
    #     "valid-to": "31-12-9999",
    #     "vejnavn": "Flakhaven 4"
    # }]

    query = flask.request.args.get('vejnavn')
    local = flask.request.args.get('local')

    if local:
        org = lora.organisation.get(local)
        codeprefix = 'urn:dk:kommune:'
        for myndighed in org['relationer']['myndighed']:
            if myndighed.get('urn', '').startswith(codeprefix):
                code = int(myndighed['urn'][len(codeprefix):])
                break
        else:
            return 'No local municipality found!', 400
    else:
        code = None

    if not query:
        return flask.jsonify([{
            'message': 'missing "vejnavn" parameter',
        }]), 400

    return flask.jsonify([
        {
            "UUID_EnhedsAdresse": addrinfo['adresse']['id'],
            "postdistrikt": addrinfo['adresse']['postnrnavn'],
            "postnr": addrinfo['adresse']['postnr'],
            "vejnavn": addrinfo['tekst'],
        }
        for addrinfo in requests.get(
                'http://dawa.aws.dk/adresser/autocomplete',
                params={
                    'noformat': '1',
                    'kommunekode': code,
                    'q': query,
                },
        ).json()
    ])


@app.route('/role-types/contact/facets/properties/classes/')
def get_contact_facet_properties_classes():
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
