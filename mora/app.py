#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import datetime
import itertools
import os
import traceback

import flask
import requests

from . import lora

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


@app.route('/o/<uuid:orgid>/full-hierarchy')
def full_hierarchy(orgid):
    args = flask.request.args
    treeType = args.get('treeType', None)

    org = lora.organisation(uuid=orgid)[0]

    if treeType == 'specific':
        orgunitids = lora.organisationenhed(tilhoerer=orgid,
                                            overordnet=args['orgUnitId'])
    else:
        orgunitids = lora.organisationenhed(tilhoerer=orgid)

    orgunits = {
        orgunit['id']: orgunit['registreringer']
        for orgunit in itertools.chain.from_iterable(
                lora.organisationenhed(uuid=orgunitids[i:i+100])
                for i in range(0, len(orgunitids), 100)
        )
    }

    children = collections.defaultdict(set)
    roots = set()

    for orgunitid, orgunit in orgunits.items():
        assert orgunit[-1]['relationer'].get('overordnet', []), \
            'missing superior unit for ' + orgunitid
        assert len(orgunit[-1]['relationer']['overordnet']) == 1, \
            'too many superior units for ' + orgunitid

        for parent in orgunit[-1]['relationer']['overordnet']:
            if 'uuid' in parent:
                children[parent['uuid']].add(orgunitid)
            elif 'urn' in parent:
                continue
            else:
                # empty, so root unit
                roots.add(orgunitid)

    def convert(unitid):
        try:
            reg = orgunits[unitid][-1]
        except:
            print(unitid, orgunits.keys())
            raise
        attrs = reg['attributter']['organisationenhedegenskaber'][0]
        rels = reg['relationer']

        has_children = bool(
            children[unitid] or
            lora.organisationenhed(tilhoerer=orgid, overordnet=unitid)
        )

        return {
            'name': attrs['enhedsnavn'],
            'user-key': attrs['brugervendtnoegle'],
            'uuid': unitid,
            'valid-from': attrs['virkning']['from'],
            'valid-to': attrs['virkning']['to'],
            'hasChildren': has_children,
            'children': [
                convert(childid) for childid in sorted(children[unitid])
            ] if has_children and not treeType else [],
            'org': str(orgid),
            'parent': rels['overordnet'][0].get('uuid', ''),
        }

    if treeType == 'specific':
        return flask.jsonify(list(map(convert, orgunitids)))
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
        return flask.jsonify(list(map(convert, roots)))


@app.route('/o/<uuid:orgid>/org-unit/')
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/')
def get_orgunit(orgid, unitid=None):
    params = {
        'tilhoerer': orgid,
        'uuid': unitid or flask.request.args.get('query', []),
    }

    validity = flask.request.args.get('validity', 'current')
    if validity == 'current':
        params['virkningfra'] = str(datetime.date.today())
        params['virkningtil'] = str(datetime.date.today() +
                                    datetime.timedelta(days=1))
    elif validity == 'past':
        # FIXME: this includes 'current' unless created today
        params['virkningfra'] = '-infinity'
        params['virkningtil'] = str(datetime.datetime.now())
    elif validity == 'future':
        # FIXME: this includes 'current' unless it expires today
        params['virkningfra'] = str(datetime.date.today() +
                                    datetime.timedelta(days=1))
        params['virkningtil'] = 'infinity'

    orgunitids = set(lora.organisationenhed(**params))

    def convert(unitid):
        orgunit = lora.organisationenhed(uuid=unitid)[0]
        reg = orgunit['registreringer'][-1]
        attrs = reg['attributter']['organisationenhedegenskaber'][0]
        rels = reg['relationer']

        childids = lora.organisationenhed(tilhoerer=orgid, overordnet=unitid)

        parentid = rels['overordnet'][0].get('uuid', None)

        return {
            "activeName": attrs['enhedsnavn'],
            "hasChildren": bool(childids),
            "name": attrs['enhedsnavn'],
            "org": str(orgid),
            "parent": rels['overordnet'][0].get('uuid', ''),
            "parent-object": convert(parentid) if parentid else None,
            "user-key": attrs['brugervendtnoegle'],
            "uuid": unitid,
            'valid-from': attrs['virkning']['from'],
            'valid-to': attrs['virkning']['to'],
        }

    return flask.jsonify([
        convert(orgunitid) for orgunitid in orgunitids
    ])


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/<role>/')
def get_role(orgid, unitid, role):
    try:
        orgunit = lora.organisationenhed(uuid=unitid)[0]['registreringer'][0]
    except KeyError:
        traceback.print_exc()
        return '', 404

    # TODO: past & future...
    if flask.request.args.get('validity', 'present') != 'present':
        return flask.jsonify([]), 404

    elif role == 'contact-channel':
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
            addrinfo = requests.get(
                'http://dawa.aws.dk/adresser/' + addr['uuid']
            ).json()

            return {
                "location": {
                    "name": addrinfo['adressebetegnelse'],
                    "user-key": addrinfo['kvhx'],
                    "uuid": addrinfo['id'],
                    "valid-from": "-infinity",
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
    elif role == 'association':
        return flask.jsonify([]), 404
    elif role == 'leader':
        return flask.jsonify([]), 404
    elif role == 'engagement':
        return flask.jsonify([]), 404
    elif role == 'job-function':
        return flask.jsonify([]), 404
    else:
        print(role, flask.request.args)
        return flask.jsonify([]), 400


### Classification stuff - should be moved to own file ###

# This one is used when creating new "Enheder"
@app.route('/org-unit/type')
def list_classes():
    clazzes = lora.klasse(uuid=lora.klasse(bvn='%'))

    # TODO: Refactor this convert function (and the one used for orgs) into a module and make it generic
    def convert(clazz):
        reg = clazz['registreringer'][-1]
        attrs = reg['attributter']['klasseegenskaber'][0]
        return {
            'uuid': clazz['id'],
            'name': attrs['titel'],
            'userKey': attrs['brugervendtnoegle']
        }

    return flask.jsonify(list(map(convert, clazzes)))