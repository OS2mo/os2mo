#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools
import json
import os

import click
from requests import Session
from sqlalchemy import union_all

from . import spreadsheets
from .ballerup import dawa
from .ballerup import db
from ..service import common

session = Session()

LORA_URL = os.environ.get('LORA_URL', "http://mox.lxc:8080")
MO_URL = os.environ.get('MO_URL', "http://localhost:5000/service")

ORG_UUID = os.environ.get('ORG_UUID', "3a87187c-f25a-40a1-8d42-312b2e2b43bd")

CSV_PATH = os.environ.get('CSV_PATH',
                          'mora/importing/ballerup/data/BALLERUP.csv')


@functools.lru_cache(1024)
def get_class(typename, **kwargs):
    r = session.get(
        '{}/o/{}/f/{}'.format(
            MO_URL, ORG_UUID, typename),
    )

    assert r.ok

    for addrtype in r.json()['data']['items']:
        if all(addrtype[k] == v for k, v in kwargs.items()):
            return addrtype


@functools.lru_cache(1024)
def get_facet(typename, **kwargs):
    r = session.get(
        '{}/o/{}/f/{}'.format(
            MO_URL, ORG_UUID, typename),
    )
    assert r.ok
    return r.json()['uuid']


@functools.lru_cache(1024)
def lookup_addr_object(addr):
    addr_uuid = dawa.lookup(
        vejnavn=addr.vejnavn,
        husnummer=addr.husnummer,
        bynavn=addr.bynavn,
        postnummer=addr.postnummer
    )
    if not addr_uuid:
        fail(addr.uuid, addr.vejnavn, addr.husnummer, addr.postnummer, addr.bynavn)
    return addr_uuid


def log(msg, error=False):
    click.echo(msg, err=error)


def fail(*args):
    i = map(str, args)
    arg_string = ", ".join(i)
    log(arg_string, True)


def insert(path, payload, *args, method="POST"):
    r = session.request(
        method,
        path,
        json=payload
    )
    if not r:
        try:
            fail(json.dumps(r.json(), indent=2),
                 json.dumps(payload, indent=2), *args)
        except json.JSONDecodeError:
            fail(r, json.dumps(payload, indent=2), *args)
    else:
        return r.json()


def address_payload(value, address_type):
    payload = {
        "address_type": address_type,
        "type": "address",
        "validity": {
            "from": "2010-01-01T00:00:00+00:00",
            "to": None
        }
    }
    if address_type['scope'] == 'DAR':
        payload['uuid'] = value
    else:
        payload['value'] = value

    return payload


def create_klasse(bvn, titel, beskrivelse, ansvarlig, facet):
    virkning = {
        "from": "2010-01-01 00:00:00+01:00",
        "to": "infinity"
    }

    klasse = {
        "attributter": {
            "klasseegenskaber": [
                {
                    "brugervendtnoegle": bvn,
                    "titel": titel,
                    "beskrivelse": beskrivelse,
                    "virkning": virkning
                }
            ]
        },
        "tilstande": {
            "klassepubliceret": [
                {
                    "publiceret": "Publiceret",
                    "virkning": virkning
                }
            ]
        },
        "relationer": {
            "ansvarlig": [
                {
                    "objekttype": "organisation",
                    "uuid": ansvarlig,
                    "virkning": virkning
                }
            ],
            "facet": [
                {
                    "objekttype": "facet",
                    "uuid": facet,
                    "virkning": virkning
                }
            ]
        },
        "note": "Indlæst af Magenta"
    }

    return klasse


def stillingsbetegnelser():
    log('Importerer stillingsbetegnelser')

    # Get job titles by finding all rows referred to by engagements
    jobtitles = db.session.query(
        db.Jobtitles
    ).join(
        db.Engagement, db.Jobtitles.uuid == db.Engagement.stillingUuid
    ).distinct().all()

    with click.progressbar(
        jobtitles
    ) as bar:
        for row in bar:
            k = create_klasse(
                row.brugervendtnoegle,
                row.title,
                str(row.objektid),
                ORG_UUID,
                get_facet('job_function')
            )
            insert(
                "{}/klassifikation/klasse/{}".format(LORA_URL, row.uuid),
                k,
                row,
                method="PUT"
            )


def lederansvar():
    log('Importerer lederansvar')

    # Get responsibility by finding all rows referred to by function tasks
    responsibilities = db.session.query(
        db.Jobtitles
    ).join(
        db.Functiontasks, db.Jobtitles.uuid == db.Functiontasks.taskUuid
    ).distinct().all()

    with click.progressbar(
        responsibilities
    ) as bar:
        for row in bar:
            k = create_klasse(
                row.uuid,
                row.title,
                str(row.objektid),
                ORG_UUID,
                get_facet('responsibility')
            )
            insert(
                "{}/klassifikation/klasse".format(LORA_URL),
                k,
                row,
                method="POST"
            )


def ledertyper():
    log('Importerer ledertyper')

    # Get manager types by finding all distinct names in Functions
    manager_types = db.session.query(
        db.Functions.name
    ).distinct().all()

    with click.progressbar(
        manager_types
    ) as bar:
        for row in bar:
            k = create_klasse(
                row.name.lower(),
                row.name,
                row.name,
                ORG_UUID,
                get_facet('manager_type')
            )
            a = insert(
                "{}/klassifikation/klasse".format(LORA_URL),
                k,
                row,
                method="POST"
            )


def enhed():
    """
    Due to the parent/child structure found in org units we are forced
    to analyze and insert the tree in the correct order
    """
    log('Importerer organisationsenheder')

    # objektid to uuid
    org_unit_map = {0: ORG_UUID}
    # parent objektid to row
    structure = {}

    def org_unit_payload(row, addrs):
        uuid, unittype, objectid, overordnet, navn, bvn = row

        valid_from = "2010-01-01"

        org_unit_type = get_class("org_unit_type", user_key='unknown')[
            'uuid']

        return {
            "name": navn,
            "parent": {
                "uuid": org_unit_map[overordnet]
            },
            "org_unit_type": {
                "uuid": org_unit_type
            },
            "user_key": bvn,
            "validity": {
                "from": valid_from,
                "to": None,
            },
            "addresses": addrs,
            "uuid": uuid,
        }

    def child_unit(addr_type, addr_uuids, u):
        addresses = [address_payload(a, addr_type) for a in addr_uuids]
        payload = org_unit_payload(
            u,
            addresses
        )
        return payload

    def root_unit(addr_type, addr_uuids, u):
        addresses = [{
            "uuid": a,
            "objekttype": addr_type['uuid']
        } for a in addr_uuids]
        payload = common.create_organisationsenhed_payload(
            u.navn,
            "2010-01-01",
            "infinity",
            'root',
            ORG_UUID,
            get_class("org_unit_type", user_key='unknown')['uuid'],
            ORG_UUID,
            addresses,
        )
        return payload

    # Build structure
    for row in db.session.query(db.t_unit):
        org_unit_map[row.objectid] = row.uuid
        entry = structure.setdefault(row.overordnetid, [])
        entry.append(row)

    def traverse_units(parent_id, bar):
        units = structure.get(parent_id, [])
        for u in units:

            # Lookup the enhed address
            addrs = db.session.query(
                db.GetGeographicDetails).filter(
                db.Unit.uuid == u.uuid,
                db.Unit.uuid == db.Locations.unitUuid,
                db.Locations.GeographicUuid == db.GetGeographicDetails.uuid
            ).all()
            addr_type = get_class('address_type', user_key='AdressePost')
            addr_uuids = [lookup_addr_object(geo) for geo in addrs]
            addr_uuids = [uuid for uuid in addr_uuids if uuid]

            # Special handling of root enhed
            if u.type == "root":
                path = "{}/organisation/organisationenhed/{}".format(
                    LORA_URL, u.uuid)
                payload = root_unit(addr_type, addr_uuids, u)
                insert(path, payload, u, method="PUT")
            # Normal units
            else:
                path = "{}/ou/create".format(MO_URL)
                payload = child_unit(addr_type, addr_uuids, u)
                insert(path, payload, u)
            bar.update(1)
            traverse_units(u.objectid, bar)

    with click.progressbar(length=len(org_unit_map) - 1) as bar:
        # 0 is the root enhed
        traverse_units(0, bar)


def bruger():
    log('Importerer brugere')

    def bruger_payload(row):
        return {
            'uuid': row.uuid,
            'cpr_no': row.personNumber,
            'name': row.addresseringsnavn,
            'org': {
                'uuid': ORG_UUID
            }
        }

    engagement = db.session.query(
        db.Engagement.personUuid).subquery()
    attachedpersons = db.session.query(
        db.Attachedpersons.personUuid).subquery()
    functionpersons = db.session.query(
        db.Functionpersons.personUuid).subquery()

    persons = db.session.query(db.Person).filter(
        db.Person.uuid.in_(engagement.select()) |
        db.Person.uuid.in_(attachedpersons.select()) |
        db.Person.uuid.in_(functionpersons.select())
    ).all()
    with click.progressbar(
        persons,
    ) as bar:
        for row in bar:
            payload = bruger_payload(row)
            insert('{}/e/create'.format(MO_URL), payload)


def engagement():
    log('Importerer engagementer')

    def engagement_payload(unit_id, job_function, engagement_type,
                           engagement_uuid, bvn):
        payload = [{
            "type": "engagement",
            "org_unit": {
                "uuid": unit_id
            },
            "job_function": {
                "uuid": job_function
            },
            "engagement_type": {
                "uuid": engagement_type
            },
            "validity": {
                "from": "2010-01-01T00:00:00+00:00",
                "to": None
            },
            "user_key": bvn
        }]

        return payload

    engagements = db.session.query(db.Engagement).filter(
        db.Engagement.personUuid.isnot(None),
        db.Engagement.personUuid != "",
        db.Engagement.personUuid != " "
    ).all()
    with click.progressbar(
        engagements,
    ) as bar:
        for engagement in bar:
            bruger_uuid = engagement.personUuid

            stilling_uuid = engagement.stillingUuid
            if not stilling_uuid:
                stilling_uuid = get_class('job_function', user_key='unknown')[
                    'uuid']

            e = engagement_payload(
                engagement.unitUuid,
                stilling_uuid,
                get_class('engagement_type', user_key='Ansat')['uuid'],
                engagement.uuid,
                engagement.userKey,
            )
            insert("{}/e/{}/create".format(MO_URL, bruger_uuid), e)

            addrs = db.session.query(db.ContactChannel).filter(
                db.ContactChannel.ownerUuid == engagement.uuid,
                db.ContactChannel.value != ' ').all()

            addr_payload = [
                address_payload(
                    addr.value,
                    get_class('address_type', user_key=addr.typeUuid)
                )
                for addr in addrs
            ]
            path = "{}/e/{}/create".format(MO_URL, engagement.personUuid)
            insert(path, addr_payload)


def tilknytning():
    log('Importerer tilknytninger')

    attachedpersons = db.session.query(db.t_attachedpersons).all()

    def tilknytning_payload(unit_id):
        payload = [{
            "org_unit": {
                "uuid": unit_id
            },
            "job_function": get_class('job_function', user_key='unknown'),
            "association_type": get_class('association_type',
                                          user_key='Tilknyttet'),
            "validity": {
                "from": "2010-01-01T00:00:00+00:00",
                "to": None
            },
            "type": "association"
        }]

        return payload

    with click.progressbar(
        attachedpersons
    ) as bar:
        for row in bar:
            a = tilknytning_payload(row.unitUuid)
            insert("{}/e/{}/create".format(MO_URL, row.personUuid), payload=a)


def leder():
    log("Importerer ledere")

    def leder_payload(unit, task, name):
        payload = [{
            "type": "manager",
            "org_unit": {
                "uuid": unit,
            },
            "manager_type": {
                "uuid": get_class("manager_type", user_key=name.lower())[
                    'uuid']
            },
            "responsibility": {
                "uuid": get_class("responsibility", user_key=task)['uuid']
            },
            "manager_level": {
                "uuid": get_class("manager_level", user_key="unknown")['uuid']
            },
            "validity": {
                "from": "2010-01-01T00:00:00+00:00",
                "to": None
            }
        }]

        return payload

    ledere = db.session.query(
        db.Functionpersons.personUuid, db.Functionunits.unitUuid,
        db.Functiontasks.taskUuid, db.Functions.name
    ).join(
        db.Functions,
        db.Functions.functionUuid == db.Functionpersons.functionUuid
    ).join(
        db.Functionunits,
        db.Functionunits.functionUuid == db.Functions.functionUuid
    ).join(
        db.Functiontasks,
        db.Functiontasks.functionUuid == db.Functionunits.functionUuid
    ).all()

    with click.progressbar(ledere) as bar:
        for person, unit, task, name in bar:
            payload = leder_payload(unit, task, name)
            insert("{}/e/{}/create".format(MO_URL, person), payload=payload)


def csv():
    log('Importerer CSV')
    spreadsheets.run(LORA_URL, (CSV_PATH,), False, False, 1, False, False,
                     False, False)


def run(*args, compact=False, **kwargs):
    if not compact:
        csv()
        stillingsbetegnelser()
        lederansvar()
        ledertyper()

    enhed()
    bruger()
    engagement()
    tilknytning()
    leder()
    # Importer orlov?
    # Importer IT?
