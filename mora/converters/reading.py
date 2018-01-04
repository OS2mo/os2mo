#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import itertools
import operator

from . import addr
from . import meta

from .. import lora
from .. import util


def list_organisations():
    c = lora.Connector()

    orgs = c.organisation(uuid=c.organisation(bvn='%'))

    def convert(org):
        rootids = c.organisationenhed(overordnet=org['id'])

        # our data model assumes and requires that every organisation
        # has one single root unit; obviously, any org. that doesn't
        # satisfy this requirements isn't intended for us...
        if len(rootids) != 1:
            return None

        rootid = rootids.pop()
        orgunit = c.organisationenhed.get(rootid)
        unitattrs = orgunit['attributter']['organisationenhedegenskaber'][0]
        unit_validity = orgunit['tilstande']['organisationenhedgyldighed'][0]

        reg = org['registreringer'][-1]

        return wrap_in_org(c, org['id'], {
            'name': unitattrs['enhedsnavn'],
            'user-key': unitattrs['brugervendtnoegle'],
            'uuid': rootid,
            'valid-from': util.to_frontend_time(
                unit_validity['virkning']['from'],
            ),
            'valid-to': util.to_frontend_time(
                unit_validity['virkning']['to'],
            ),
            'hasChildren': True,
            'children': [],
            'org': org['id'],
        }, reg)

    return list(filter(None, map(convert, orgs)))


def get_unit_type(typerel) -> dict:
    if not typerel:
        return None

    assert len(typerel) == 1
    assert typerel[0]['uuid']

    typeid = typerel[0]['uuid']

    return get_class(typeid)


def _convert_unit(c, unitid, orgunit, levels):
    if not orgunit:
        return None

    try:
        attrs = orgunit['attributter']['organisationenhedegenskaber'][0]
    except LookupError:
        return None

    rels = orgunit['relationer']

    # Get the current org unit end-date and use this for past and future too
    orgunit_validity = (
        orgunit['tilstande']['organisationenhedgyldighed'][0]['virkning']
    )

    if c.validity == 'present':
        parent = rels['overordnet'][0]['uuid']
        orgid = rels['tilhoerer'][0]['uuid']
    else:
        parent = None
        orgid = None

    if levels > 0:
        childobjs = sorted(
            filter(None, (
                _convert_unit(c, childid, childunit, levels - 1)
                for childid, childunit in
                c.organisationenhed.get_all(tilhoerer=orgid,
                                            overordnet=unitid,
                                            gyldighed='Aktiv')
            )),
            key=lambda r: r['name'].lower(),
        )
        has_children = bool(childobjs)
    else:
        childobjs = []
        has_children = bool(c.organisationenhed(tilhoerer=orgid,
                                                overordnet=unitid,
                                                gyldighed='Aktiv'))

    return {
        'name': attrs['enhedsnavn'],
        'user-key': attrs['brugervendtnoegle'],
        'uuid': unitid,
        'type': get_unit_type(rels['enhedstype']),
        'valid-from': util.to_frontend_time(
            orgunit_validity['from'],
        ),
        'valid-to': util.to_frontend_time(
            orgunit_validity['to'],
        ),
        'hasChildren': has_children,
        'children': childobjs,
        'org': str(orgid),
        'parent': parent if parent and parent != orgid else None,
    }


def full_hierarchies(orgid: str, parentid: str,
                     include_children=True,
                     **loraparams):
    assert isinstance(parentid, str), parentid

    search = dict(
        tilhoerer=orgid,
        overordnet=parentid,
        gyldighed='Aktiv',
    )

    c = lora.Connector(**loraparams)

    return sorted(
        (
            _convert_unit(c, unitid, orgunit, 1)
            for unitid, orgunit in c.organisationenhed.get_all(**search)
        ),
        key=lambda r: r['name'].lower(),
    )


def full_hierarchy(orgid: str, unitid: str,
                   include_children=True,
                   **loraparams):
    assert isinstance(orgid, str)
    assert isinstance(unitid, str)

    c = lora.Connector(**loraparams)
    orgunit = c.organisationenhed.get(unitid)

    return _convert_unit(c, unitid, orgunit, 1)


def wrap_in_org(connector, orgid, value, org=None):
    if not org:
        org = connector.organisation.get(orgid)

    orgattrs = org['attributter']['organisationegenskaber'][0]
    org_validity = org['tilstande']['organisationgyldighed'][0]

    return {
        'hierarchy': value,
        'name': orgattrs['organisationsnavn'],
        'user-key': orgattrs['brugervendtnoegle'],
        'uuid': orgid,
        'valid-from': util.to_frontend_time(
            org_validity['virkning']['from'],
        ),
        'valid-to': util.to_frontend_time(
            org_validity['virkning']['to'],
        ),
    }


def unit_history(orgid, unitid):
    # TODO: verify orgid?

    c = lora.Connector()
    regs = c.organisationenhed.get(unitid, registreretfra='-infinity',
                                   registrerettil='infinity')

    for reg in regs:
        yield {
            'changedBy': reg['brugerref'],
            'object': unitid,
            'date': util.to_frontend_time(
                reg['fratidspunkt']['tidsstempeldatotid'],
            ),
            'from': util.to_frontend_time(
                reg['fratidspunkt']['tidsstempeldatotid'],
            ),
            'to': util.to_frontend_time(
                reg['tiltidspunkt']['tidsstempeldatotid'],
            ),
            'section': reg['livscykluskode'],
            'action': reg.get('note'),
        }


def _convert_class(classid, clazz):
    attrs = clazz['attributter']['klasseegenskaber'][0]

    return {
        'uuid': classid,
        'name': (attrs.get('titel') or attrs.get('beskrivelse') or
                 attrs['brugervendtnoegle']),
        'userKey': attrs['brugervendtnoegle'],
        'user-key': attrs['brugervendtnoegle'],
    }


def get_classes(facet_name: str):
    c = lora.Connector()
    facetids = c.facet(bvn=facet_name)

    classes = c.klasse.get_all(facet=facetids)

    return sorted(itertools.starmap(_convert_class,
                                    classes),
                  key=operator.itemgetter('name'))


def get_class(uuid):
    if not uuid:
        return None

    cls = lora.klasse.get(uuid=uuid)

    return cls and _convert_class(uuid, cls)


def get_contact_channels(userid=None, orgid=None, unitid=None, **loraparams):
    c = lora.Connector(**loraparams)

    if userid:
        assert not unitid
        scope = c.bruger
        objid = userid
    elif unitid:
        scope = c.organisationenhed
        objid = unitid

    def convert_address(obj):
        if obj['urn'].startswith(meta.PHONE_PREFIX):
            info = meta.PhoneNumber.fromstring(
                obj.get('objekttype'),
            )
            t = {
                "name": meta.PHONE_NUMBER_DESC,
                "prefix": meta.PHONE_PREFIX,
                "user-key": 'Telephone_number',
            }

            return {
                "contact-info": obj['urn'][len(meta.PHONE_PREFIX):],
                "name": meta.PHONE_NUMBER_DESC,
                'location': _get_location(info.location),
                'visibility': {
                    'user-key': info.visibility,
                    'uuid': meta.PHONE_VISIBILITY_UUIDS[info.visibility],
                    'name': meta.PHONE_VISIBILITIES[info.visibility],
                },
                "type": t,
                "phone-type": t,
                "valid-from": util.to_frontend_time(
                    obj['virkning']['from'],
                ),
                "valid-to": util.to_frontend_time(
                    obj['virkning']['to'],
                ),
            }

        elif obj['urn'].startswith(meta.MAIL_PREFIX):
            info = meta.PhoneNumber.fromstring(
                obj.get('objekttype'),
            )
            t = {
                "name": meta.MAIL_ADDRESS_DESC,
                "prefix": meta.MAIL_PREFIX,
                "user-key": 'Email',
            }

            return {
                "contact-info": obj['urn'][len(meta.MAIL_PREFIX):],
                "name": meta.MAIL_ADDRESS_DESC,
                "location": _get_location(info.location),
                'visibility': {
                    'user-key': info.visibility,
                    'uuid': meta.PHONE_VISIBILITY_UUIDS[info.visibility],
                    'name': meta.PHONE_VISIBILITIES[info.visibility],
                },
                "phone-type": t,
                "type": t,
                "valid-from": util.to_frontend_time(
                    obj['virkning']['from'],
                ),
                "valid-to": util.to_frontend_time(
                    obj['virkning']['to'],
                ),
            }

        else:
            raise NotImplementedError(obj['urn'])

    return [
        convert_address(addr)
        for start, end, obj in scope.get_effects(objid, {
            'relationer': (
                'adresser',
            )
        })
        for addr in obj['relationer'].get('adresser', [])
        if addr.get('urn', '')
    ]


def _get_location(addrid: str, name=None) -> dict:
    if not addrid:
        return {
            "name": name or util.PLACEHOLDER,
        }

    info = addr.get_address(addrid)

    return {
        "name": name or info['adressebetegnelse'],
        "uuid": info['id'],
        "vejnavn": info['adressebetegnelse'],
        "user-key": info['kvhx'],
        "valid-from": util.to_frontend_time(
            info['historik']['oprettet'],
        ),
        "valid-to": "infinity"
    }


def get_locations(userid: str=None, orgid: str=None, unitid: str=None,
                  **loraparams) -> list:
    c = lora.Connector(**loraparams)

    assert bool(userid) ^ bool(unitid), 'must specify one user or one unit'

    if userid is not None:
        scope = c.bruger
        objid = userid
    elif unitid is not None:
        scope = c.organisationenhed
        objid = unitid

    def convert_addr(addrobj: dict) -> dict:
        """
        Converts a LoRa address object to the appropriate frontend format, i.e.
        the function converts an object like this:
        {
            "uuid": "0a3f50c3-5556-32b8-e044-0003ba298018",
            "objekttype": "v0:0:j",
            "virkning": {
                "from": "2017-07-10 22:00:00+00",
                "from_included": true,
                "to": "2017-07-18 22:00:00+00",
                "to_included": false
            }
        }
        :param addrobj: The LoRa (UUID) address obejct to convert
        :return: Address object in frontend format
        """
        addrmeta = meta.Address.fromstring(
            addrobj.get('objekttype'),
        )

        location = _get_location(addrobj['uuid'], addrmeta.name)

        return {
            "location": location,
            "name": addrmeta.name or util.PLACEHOLDER,
            "org-unit": unitid,
            "primaer": addrmeta.primary,
            "role-type": "location",
            "uuid": addrobj['uuid'],
            "user-key": addrobj['uuid'],
            "valid-from": util.to_frontend_time(
                addrobj['virkning']['from'],
            ),
            "valid-to": util.to_frontend_time(
                addrobj['virkning']['to'],
            ),
        }

    return [
        convert_addr(addr)
        for start, end, obj in scope.get_effects(objid, {
            'relationer': (
                'adresser',
            )
        })
        for addr in obj['relationer'].get('adresser', [])
        if addr.get('uuid', '')
    ]


def get_contact_properties() -> list:
    return [
        {
            'user-key': k,
            'name': v,
            'uuid': k,
        }
        for k, v in meta.PHONE_VISIBILITIES.items()
    ]


def get_contact_types() -> list:
    return [
        {
            "name": meta.PHONE_NUMBER_DESC,
            "prefix": meta.PHONE_PREFIX,
            "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
        },
        {
            "name": meta.MAIL_ADDRESS_DESC,
            "prefix": meta.MAIL_PREFIX,
            "uuid": "c88aca96-eab9-42e9-ba6d-4f3868234573"
        },
    ]


def get_orgunit(unitid: str, include_parents=True, **loraparams):
    assert isinstance(unitid, str)

    c = lora.Connector(**loraparams)
    r = []

    for start, end, orgunit in c.organisationenhed.get_effects(
        unitid,
        {
            'attributter': (
                'organisationenhedegenskaber',
            ),
            'relationer': (
                'enhedstype',
                'overordnet',
                'tilhoerer',
            ),
            'tilstande': (
                'organisationenhedgyldighed',
            ),
        },
    ):

        states = orgunit['tilstande']['organisationenhedgyldighed']

        if not states or any(s.get('gyldighed') != 'Aktiv' for s in states):
            continue

        rels = orgunit['relationer']
        try:
            props = orgunit['attributter']['organisationenhedegenskaber'][0]
        except IndexError:
            continue

        try:
            parentid = rels['overordnet'][0]['uuid']
        except IndexError:
            parentid = None

        try:
            orgid = rels['tilhoerer'][0]['uuid']
        except IndexError:
            orgid = None

        r.append({
            'activeName': props['enhedsnavn'],
            'name': props['enhedsnavn'],
            'user-key': props['brugervendtnoegle'],
            'uuid': unitid,
            'valid-from': util.to_frontend_time(start),
            'valid-to': util.to_frontend_time(end),
            'org': str(orgid),
            'parent': parentid if parentid and parentid != orgid else None,
            'parent-object': (
                get_orgunit(
                    parentid,
                    include_parents=False,
                    virkningfra=util.to_lora_time(start),
                    virkningtil=util.to_lora_time(end),
                ).pop()
                if include_parents and parentid and parentid != orgid else None
            ),
            'type': get_unit_type(rels['enhedstype']),
        })

    return r


def list_orgunits(*, limit=1000, start=0, **loraparams):
    return lora.Connector().organisationenhed(
        maximalantalresultater=start + limit,
        **loraparams,
    )[-limit:]


def get_orgunits(unitids, **loraparams):
    def _get(unitid):
        yield from get_orgunit(unitid, **loraparams)

    return list(filter(None, itertools.chain.from_iterable(map(
        _get,
        unitids,
    ))))


def list_employees(*, limit=1000, start=0, **loraparams):
    return lora.Connector().bruger(
        maximalantalresultater=start + limit,
        **loraparams,
    )[-limit:]


def get_employees(uuids, **loraparams):
    def convert(r):
        userid = r['id']
        user = r['registreringer'][0]

        rels = user['relationer']
        props = user['attributter']['brugeregenskaber'][0]

        cpr = rels['tilknyttedepersoner'][0].get('urn')
        if cpr and cpr.startswith('urn:dk:cpr:person:'):
            cpr = cpr[18:]

        return {
            "uuid": userid,
            "user-key": cpr,
            "name": props["brugernavn"],
            "nick-name": props["brugervendtnoegle"],
        }

    return [
        convert(empl)
        for chunk in util.splitlist(uuids, 20)
        for empl in lora.Connector(**loraparams).bruger(uuid=chunk)
    ]


def _convert_engagement(funcid, start, end, effect):
    props = effect['attributter']['organisationfunktionegenskaber'][0]
    rels = effect['relationer']

    emplid = rels['tilknyttedebrugere'][-1]['uuid']
    empl = get_employees([emplid], effective_date=start)[-1]

    unitid = rels['tilknyttedeenheder'][-1]['uuid']
    orgid = rels['tilknyttedeorganisationer'][-1]['uuid']

    titleid = rels['opgaver'][-1].get('uuid') if rels.get('opgaver') else None

    r = {
        "job-title": (
            get_class(titleid)
            if titleid
            else {
                "uuid": funcid,
                "user-key": props['brugervendtnoegle'],
                "name": props['funktionsnavn']
            }
        ),
        "type": get_class(
            rels['organisatoriskfunktionstype'][-1].get('uuid'),
        ),
        "org-unit": get_orgunit(unitid,
                                include_parents=False,
                                virkningfra=util.to_lora_time(start),
                                virkningtil=util.to_lora_time(end))[-1],
        "org": None,  # unused
        "uuid": funcid,
        "person": emplid,
        "person-name": empl['name'],
        "role-type": "engagement",
        "valid-from": util.to_frontend_time(start),
        "valid-to": util.to_frontend_time(end),
    }

    return r


def get_engagements(orgid=None, unitid=None, userid=None, **loraparams):
    c = lora.Connector(**loraparams)

    search = {}

    if unitid is not None:
        search['tilknyttedeenheder'] = str(unitid)
    if userid is not None:
        search['tilknyttedebrugere'] = str(userid)

    # disregard orgid, as the original frontend gets it wrong

    return [
        _convert_engagement(funcid, start, end, effect)

        for funcid in c.organisationfunktion(**search)
        for start, end, effect in c.organisationfunktion.get_effects(
            funcid,
            {
                'relationer': (
                    'opgaver',
                    'organisatoriskfunktionstype',
                    'tilknyttedeenheder',
                ),
                'tilstande': (
                    'organisationfunktiongyldighed',
                ),
            },
            {
                'attributter': (
                    'organisationfunktionegenskaber',
                ),
                'relationer': (
                    'tilhoerer',
                    'tilknyttedebrugere',
                    'tilknyttedeorganisationer',
                ),
            },
        )
        if effect.get('tilstande')
                 .get('organisationfunktiongyldighed')[0]
                 .get('gyldighed') == 'Aktiv'
    ]
