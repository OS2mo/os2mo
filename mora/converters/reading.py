#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from .. import lora


def list_organisations():
    orgs = lora.organisation(uuid=lora.organisation(bvn='%'))

    def convert(org):
        rootid = lora.organisationenhed(overordnet=org['id'])[0]
        orgunit = lora.organisationenhed.get(rootid)
        unitattrs = orgunit['attributter']['organisationenhedegenskaber'][0]

        reg = org['registreringer'][-1]
        attrs = reg['attributter']['organisationegenskaber'][0]
        return wrap_in_org(org['id'], {
            'name': unitattrs['enhedsnavn'],
            'user-key': unitattrs['brugervendtnoegle'],
            'uuid': rootid,
            'valid-from': unitattrs['virkning']['from'],
            'valid-to': unitattrs['virkning']['to'],
            'hasChildren': True,
            'children': [],
            'org': org['id'],
        }, reg)

    return list(map(convert, orgs))


def full_hierarchies(orgid: str, parentid: str, **kwargs):
    assert isinstance(parentid, str), parentid

    unitids = lora.organisationenhed(tilhoerer=orgid, overordnet=parentid)

    return sorted(
        (full_hierarchy(orgid, unitid, **kwargs)
         for unitid in unitids),
        key=lambda r: r['name'].lower(),
    )


def full_hierarchy(orgid: str, unitid: str, include_children=True,
                   include_parents=False, include_activename=False):
    assert isinstance(orgid, str)
    assert isinstance(unitid, str)

    kwargs = dict(
        include_children=False,
        include_parents=include_parents,
        include_activename=include_activename,
    )

    orgunit = lora.organisationenhed.get(unitid)
    attrs = orgunit['attributter']['organisationenhedegenskaber'][0]
    rels = orgunit['relationer']

    children = lora.organisationenhed(tilhoerer=orgid, overordnet=unitid)
    parent = rels['overordnet'][0]['uuid']

    r = {
        'name': attrs['enhedsnavn'],
        'user-key': attrs['brugervendtnoegle'],
        'uuid': unitid,
        'valid-from': attrs['virkning']['from'],
        'valid-to': attrs['virkning']['to'],
        'hasChildren': bool(children),
        'org': str(orgid),
        'parent': parent if parent != orgid else None,
    }

    if include_parents:
        assert not include_children, 'including both parents and children?'

        r["parent-object"] = (
            full_hierarchy(orgid, parent, **kwargs)
            if parent != orgid else None
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

    return {
            'hierarchy': value,
            'name': orgattrs['organisationsnavn'],
            'user-key': orgattrs['brugervendtnoegle'],
            'uuid': orgid,
            'valid-from': orgattrs['virkning']['from'],
            'valid-to': orgattrs['virkning']['to'],
        }
