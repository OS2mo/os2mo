# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import collections
import itertools
import os

import flask

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


@app.route('/service/user/<user>/login', methods=['POST', 'GET'])
def login(user):
    return flask.jsonify({
        "user": user,
        "token": "kaflaflibob",
        "role": [
            "o-admin"
        ]
    })


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
    print(flask.request.args)
    # if not flask.request.args.get('treeType', False):
    #     return flask.jsonify([])
    # if not flask.request.args.get('orgUnitId', False):
    #     return flask.jsonify([])

    org = lora.organisation(uuid=orgid)[0]

    orgunitids = lora.organisationenhed(tilhoerer=orgid)
    orgunits = {
        orgunit['id']: orgunit['registreringer']
        for orgunit in itertools.chain.from_iterable(
                lora.organisationenhed(uuid=orgunitids[i:i+100])
                for i in range(0, len(orgunitids), 100)
        )
    }

    children = collections.defaultdict(set)

    for orgunitid, orgunit in orgunits.items():
        assert orgunit[-1]['relationer'].get('overordnet', []), orgunitid
        for parent in orgunit[-1]['relationer']['overordnet']:
            if 'uuid' in parent:
                children[parent['uuid']].add(orgunitid)
            elif 'urn' in parent:
                continue
            else:
                # empty, so root unit
                children[str(orgid)].add(orgunitid)

    def convert(unitid):
        reg = orgunits[unitid][-1]
        attrs = reg['attributter']['organisationenhedegenskaber'][0]
        rels = reg['relationer']

        return {
            'name': attrs['enhedsnavn'],
            'user-key': attrs['brugervendtnoegle'],
            'uuid': unitid,
            'valid-from': attrs['virkning']['from'],
            'valid-to': attrs['virkning']['to'],
            'hasChildren': bool(children[unitid]),
            'children': [
                convert(childid) for childid in children[unitid]
            ],
            'org': str(orgid),
            'parent': rels['overordnet']
        }

    assert children[str(orgid)] and len(children[str(orgid)]) == 1, \
        'too many roots!'

    rootid = children[str(orgid)].pop()

    orgattrs = \
        org['registreringer'][-1]['attributter']['organisationegenskaber'][0]

    return flask.jsonify({
        'hierarchy': convert(rootid),
        'name': orgattrs['organisationsnavn'],
        'user-key': orgattrs['brugervendtnoegle'],
        'uuid': org['id'],
        'valid-from': orgattrs['virkning']['from'],
        'valid-to': orgattrs['virkning']['to'],
    })

    # treeType=specific
    return flask.jsonify({
        "hierarchy": {
            "children": [],
            "hasChildren": True,
            "name": "Borgmesterforvaltningen",
            "org": "1001",
            "parent": "",
            "user-key": "ean12345",
            "uuid": "1101",
            "valid-from": "-infinity",
            "valid-to": "infinity"
        },
        "name": "Administrativ Organisation",
        "user-key": "auth",
        "uuid": "1001"
    })

    # no treetype
    return flask.jsonify({
        "hierarchy": {
            "children": [
                {
                    "hasChildren": False,
                    "name": "Digitaliseringskontoret",
                    "org": "1001",
                    "parent": "1101",
                    "user-key": "ean123456",
                    "uuid": "1102",
                    "valid-from": "-infinity",
                    "valid-to": "infinity"
                },
                {
                    "children": [
                        {
                            "hasChildren": False,
                            "name": "Vicev\u00e6rtkontoret",
                            "org": "1001",
                            "parent": "1105",
                            "user-key": "ean12345678",
                            "uuid": "1106",
                            "valid-from": "-infinity",
                            "valid-to": "infinity"
                        }
                    ],
                    "hasChildren": False,
                    "name": "Ejendomsservice",
                    "org": "1001",
                    "parent": "1101",
                    "user-key": "ean1234567",
                    "uuid": "1105",
                    "valid-from": "-infinity",
                    "valid-to": "infinity"
                }
            ],
            "hasChildren": False,
            "name": "Borgmesterforvaltningen",
            "org": "1001",
            "parent": "",
            "user-key": "ean12345",
            "uuid": "1101",
            "valid-from": "-infinity",
            "valid-to": "infinity"
        },
        "name": "Administrativ Organisation",
        "user-key": "auth",
        "uuid": "1001"
    })
