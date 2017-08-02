#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import operator

from . import addr

from .. import lora
from .. import util


def list_organisations():
    orgs = lora.organisation(uuid=lora.organisation(bvn='%'))

    def convert(org):
        rootid = lora.organisationenhed(overordnet=org['id'])[0]
        orgunit = lora.organisationenhed.get(rootid)
        unitattrs = orgunit['attributter']['organisationenhedegenskaber'][0]
        unit_validity = orgunit['tilstande']['organisationenhedgyldighed'][0]

        reg = org['registreringer'][-1]

        return wrap_in_org(org['id'], {
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

    return list(map(convert, orgs))


def full_hierarchies(orgid: str, parentid: str,
                     include_children=True,
                     include_parents=False,
                     include_activename=False,
                     **loraparams):
    assert isinstance(parentid, str), parentid

    kwargs = dict(
        include_children=include_children,
        include_parents=include_parents,
        include_activename=include_activename,
        **loraparams,
    )

    unitids = lora.organisationenhed(
        tilhoerer=orgid,
        overordnet=parentid,
        gyldighed='Aktiv',
        **loraparams,
    )

    return sorted(
        filter(None, (full_hierarchy(orgid, unitid, **kwargs)
                      for unitid in unitids)),
        key=lambda r: r['name'].lower(),
    )


def full_hierarchy(orgid: str, unitid: str,
                   include_children=True,
                   include_parents=False,
                   include_activename=False,
                   **loraparams):
    assert isinstance(orgid, str)
    assert isinstance(unitid, str)

    kwargs = dict(
        include_children=False,
        include_parents=include_parents,
        include_activename=include_activename,
    )
    kwargs.update(loraparams)

    orgunit = lora.organisationenhed.get(unitid, **loraparams)

    if not orgunit:
        return None

    # TODO: check validity?

    try:
        attrs = orgunit['attributter']['organisationenhedegenskaber'][0]
    except LookupError:
        return None

    rels = orgunit['relationer']

    # Get the current org unit end-date and use this for past and future too
    current_orgunit = lora.organisationenhed.get(uuid=unitid)
    orgunit_validity = current_orgunit['tilstande'][
        'organisationenhedgyldighed'][0]['virkning']

    children = lora.organisationenhed(tilhoerer=orgid, overordnet=unitid,
                                      gyldighed='Aktiv',
                                      **loraparams)

    unit_types = orgunit['relationer']['enhedstype']
    if unit_types:
        # TODO: should we pass on loraparams? perhaps, but not validity
        unit_type = lora.klasse.get(uuid=unit_types[0]['uuid'])
    else:
        unit_type = None

    validity = loraparams.get('validity')
    if not validity or validity == 'present':
        parent = rels['overordnet'][0]['uuid']
        orgid = rels['tilhoerer'][0]['uuid']
    else:
        parent = None

    r = {
        'name': attrs['enhedsnavn'],
        'user-key': attrs['brugervendtnoegle'],
        'uuid': unitid,
        'type': {
            'name': unit_type['attributter']['klasseegenskaber'][0]['titel']
            if unit_type else ''  # TODO: problem with ['klasseegenskaber'][0]?
        },
        'valid-from': util.to_frontend_time(
            orgunit_validity['from'],
        ),
        'valid-to': util.to_frontend_time(
            orgunit_validity['to'],
        ),
        'hasChildren': bool(children),
        'org': str(orgid),
        'parent': parent if parent and parent != orgid else None,
    }

    if include_parents:
        assert not include_children, 'including both parents and children?'

        r["parent-object"] = (
            full_hierarchy(orgid, parent, **kwargs)
            if parent and parent != orgid else None
        )
    else:
        r['children'] = (
            full_hierarchies(orgid, unitid, **kwargs)
            if include_children else []
        )

    if include_activename:
        r['activeName'] = attrs['enhedsnavn']

    return r


def wrap_in_org(orgid, value, org=None):
    if not org:
        org = lora.organisation.get(orgid)

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

    regs = lora.organisationenhed.get(unitid, registreretfra='-infinity',
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


def _convert_class(clazz):
    reg = clazz['registreringer'][-1]
    attrs = reg['attributter']['klasseegenskaber'][0]

    return {
        'uuid': clazz['id'],
        'name': attrs['titel'],
        'userKey': attrs['brugervendtnoegle']
    }


def get_classes():
    # TODO: we need to somehow restrict the available classes to
    # sensible options; a classification hierarchy, perhaps, or only
    # those related to or listed in our organisation?
    classes = lora.klasse(uuid=lora.klasse(bvn='%'))

    return sorted(map(_convert_class,
                      classes),
                  key=operator.itemgetter('name'))


PHONE_PREFIX = 'urn:magenta.dk:telefon:'
PHONE_NUMBER_DESC = 'Telefonnummer'


def get_contact_channel(unitid, **loraparams):
    orgunit = lora.organisationenhed.get(unitid, **loraparams)

    if not orgunit:
        return None

    return [
        {
            "contact-info": addr['urn'][len(PHONE_PREFIX):],
            # "name": "telefon 12345678",
            'location': {
                'uuid': '00000000-0000-0000-0000-000000000000',
            },
            "type": {
                "name": PHONE_NUMBER_DESC,
                "prefix": PHONE_PREFIX,
                "user-key": "Telephone_number",
            },
            "valid-from": util.to_frontend_time(
                addr['virkning']['from'],
            ),
            "valid-to": util.to_frontend_time(
                addr['virkning']['to'],
            ),
        }
        for addr in orgunit['relationer'].get('adresser', [])
        if addr.get('urn', '').startswith(PHONE_PREFIX)
    ]


def get_location(unitid, **loraparams):
    orgunit = lora.organisationenhed.get(unitid, **loraparams)

    if not orgunit:
        return None

    def convert_addr(addrobj):
        addrinfo = addr.get_address(addrobj['uuid'])

        note = addrobj['virkning'].get('notetekst')
        meta = addr.AddressMeta.fromstring(note)

        return {
            "location": {
                "vejnavn": addrinfo['adressebetegnelse'],
                "user-key": addrinfo['kvhx'],
                "uuid": addrinfo['id'],
                "valid-from": util.to_frontend_time(
                    addrinfo['historik']['oprettet'],
                ),
                "valid-to": "infinity"
            },
            "name": meta.name,
            "org-unit": unitid,
            "primaer": meta.primary,
            "role-type": "location",
            "uuid": addrinfo['id'],
            "valid-from": util.to_frontend_time(
                addrobj['virkning']['from'],
            ),
            "valid-to": util.to_frontend_time(
                addrobj['virkning']['to'],
            ),
        }

    return [
        convert_addr(addr)
        for addr in orgunit['relationer'].get('adresser', [])
        if addr.get('uuid', '')
    ]
