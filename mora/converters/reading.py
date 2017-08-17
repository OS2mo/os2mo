#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import itertools
import operator
import uuid

from . import addr
from . import meta

from .. import lora
from .. import util


def list_organisations():
    orgs = lora.organisation(uuid=lora.organisation(bvn='%'))

    def convert(org):
        rootids = lora.organisationenhed(overordnet=org['id'])

        # our data model assumes and requires that every organisation
        # has one single root unit; obviously, any org. that doesn't
        # satisfy this requirements isn't intended for us...
        if len(rootids) != 1:
            return None

        rootid = rootids.pop()
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

    return list(filter(None, map(convert, orgs)))


def full_hierarchies(orgid: str, parentid: str,
                     include_children=True,
                     **loraparams):
    assert isinstance(parentid, str), parentid

    kwargs = dict(
        include_children=include_children,
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
                   **loraparams):
    assert isinstance(orgid, str)
    assert isinstance(unitid, str)

    kwargs = dict(
        include_children=False,
        **loraparams,
    )

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
        'children': (
            full_hierarchies(orgid, unitid, **kwargs)
            if include_children else []
        ),
        'org': str(orgid),
        'parent': parent if parent and parent != orgid else None,
    }

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


def get_contact_channels(unitid, **loraparams):
    orgunit = lora.organisationenhed.get(unitid, **loraparams)

    if not orgunit:
        return None

    def convert_address(obj):
        info = meta.PhoneNumber.fromstring(
            obj['virkning'].get('notetekst'),
        )

        return {
            "contact-info": obj['urn'][len(meta.PHONE_PREFIX):],
            # "name": "telefon 12345678",
            'location': _get_location(info.location),
            'visibility': {
                'user-key': info.visibility,
                'uuid': meta.PHONE_VISIBILITY_UUIDS[info.visibility],
                'name': meta.PHONE_VISIBILITIES[info.visibility],
            },
            "type": {
                "name": meta.PHONE_NUMBER_DESC,
                "prefix": meta.PHONE_PREFIX,
                "user-key": 'Telephone_number',
            },
            "valid-from": util.to_frontend_time(
                obj['virkning']['from'],
            ),
            "valid-to": util.to_frontend_time(
                obj['virkning']['to'],
            ),
        }

    return [
        convert_address(addr)
        for addr in orgunit['relationer'].get('adresser', [])
        if addr.get('urn', '').startswith(meta.PHONE_PREFIX)
    ]


def _get_location(addrid, name=None):
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


def get_locations(unitid, **loraparams):
    orgunit = lora.organisationenhed.get(unitid, **loraparams)

    if not orgunit:
        return []

    def convert_addr(addrobj: dict) -> dict:
        """
        Converts a LoRa address object to the appropriate frontend format, i.e.
        the function converts an object like this:
        {
            "uuid": "0a3f50c3-5556-32b8-e044-0003ba298018",
            "virkning": {
                "from": "2017-07-10 22:00:00+00",
                "from_included": true,
                "notetekst": "v0:0:j",
                "to": "2017-07-18 22:00:00+00",
                "to_included": false
            }
        }
        :param addrobj: The LoRa (UUID) address obejct to convert
        :return: Address object in frontend format
        """
        addrmeta = meta.Address.fromstring(
            addrobj['virkning'].get('notetekst'),
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
        for addr in orgunit['relationer'].get('adresser', [])
        if addr.get('uuid', '')
    ]


def get_contact_properties():
    return [
        {
            'user-key': k,
            'name': v,
            'uuid': k,
        }
        for k, v in meta.PHONE_VISIBILITIES.items()
    ]


def get_contact_types():
    return [
        {
            "name": "Phone Number",
            "prefix": "urn:magenta.dk:telefon:",
            "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
        },
    ]


def _get_one_orgunit(orgid: str, unitid: str, include_parents=True,
                     **loraparams):
    assert isinstance(orgid, str), '{!r} is not a string!'.format(orgid)
    assert isinstance(unitid, str), '{!r} is not a string!'.format(unitid)

    orgunit = lora.organisationenhed.get(unitid, **loraparams)

    if not orgunit:
        return None

    rels = orgunit['relationer']
    props = orgunit['attributter']['organisationenhedegenskaber'][0]
    state = orgunit['tilstande']['organisationenhedgyldighed'][0]

    if state['gyldighed'] != 'Aktiv':
        return None

    try:
        parentid = rels['overordnet'][0]['uuid']
    except IndexError:
        parentid = None

    try:
        orgid = rels['tilhoerer'][0]['uuid']
    except IndexError:
        pass

    # get the 'current' information for the type, although we don't
    # expect them to change much
    assert not rels['enhedstype'] or len(rels['enhedstype']) == 1
    unit_type = (
        lora.klasse.get(uuid=rels['enhedstype'][0]['uuid'])
        if rels['enhedstype'] else None
    )

    start = loraparams.get('virkningfra', '-infinity')
    end = loraparams.get('virkningtil', 'infinity')

    if start == '-infinity':
        start = state['virkning']['from']

    if end == 'infinity':
        end = state['virkning']['to']

    return {
        'activeName': props['enhedsnavn'],
        'name': props['enhedsnavn'],
        'user-key': props['brugervendtnoegle'],
        'uuid': unitid,
        'valid-from': util.to_frontend_time(start),
        'valid-to': util.to_frontend_time(end),
        'org': str(orgid),
        'parent': parentid if parentid and parentid != orgid else None,
        'parent-object': (
            _get_one_orgunit(orgid, parentid,
                             include_parents=False, **loraparams)
            if include_parents and parentid and parentid != orgid else None
        ),
        'type': {
            'name': unit_type['attributter']['klasseegenskaber'][0]['titel']
            if unit_type else ''  # TODO: problem with ['klasseegenskaber'][0]?
        },
    }


def get_orgunit(orgid: str, unitid: str, include_parents=True, **loraparams):
    assert isinstance(orgid, str)
    assert isinstance(unitid, str)

    validity = loraparams.pop('validity', None) or 'present'

    if validity == 'present':
        yield _get_one_orgunit(
            orgid, unitid, include_parents, **loraparams,
        )

        return

    today = util.parsedatetime(
        loraparams.get('effective_date', util.today()),
    )
    tomorrow = today + datetime.timedelta(days=1)

    if validity == 'past':
        loraparams.update(virkningfra='-infinity', virkningtil=today)

        def requirement_func(s):
            return util.parsedatetime(s) < today
    elif validity == 'future':
        loraparams.update(virkningfra=tomorrow, virkningtil='infinity')

        def requirement_func(s):
            return util.parsedatetime(s) > tomorrow
    else:
        raise ValueError('invalid validity {!r}'.format(validity))

    orgunit = lora.organisationenhed.get(unitid, **loraparams)

    if not orgunit:
        return

    chunks = set()

    relevant = {
        ('attributter', 'organisationenhedegenskaber'),
        ('relationer', 'enhedstype'),
        ('relationer', 'overordnet'),
        ('relationer', 'tilhoerer'),
        ('tilstande', 'organisationenhedgyldighed'),
    }

    for group in 'attributter', 'relationer', 'tilstande':
        for key in orgunit[group]:
            for entry in orgunit[group][key]:
                if(group, key) in relevant:
                    chunks.update([entry['virkning']['from'],
                                   entry['virkning']['to']])

    chunks = sorted(filter(requirement_func, chunks))

    for start, end in zip(chunks, chunks[1:]):
        orgunit = _get_one_orgunit(
            orgid, unitid, include_parents,
            virkningfra=start, virkningtil=end,
        )

        if orgunit:
            yield orgunit


def list_orgunits(query, **loraparams):
    if isinstance(query, uuid.UUID):
        return [str(query)]

    try:
        return [str(uuid.UUID(query))]
    except (ValueError, TypeError):
        pass

    return lora.organisationenhed(enhedsnavn=query or '%', **loraparams)


def get_orgunits(orgid, unitids, **loraparams):
    def _get(unitid):
        yield from get_orgunit(orgid, unitid, **loraparams)

    return list(filter(None, itertools.chain.from_iterable(map(
        _get,
        unitids,
    ))))
