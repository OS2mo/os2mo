#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import datetime
import functools
import itertools
import json
import os
import random
import sys
import uuid

import openpyxl

from .. import util
from .. import lora


def _make_relation(obj, k):
    val = obj[k]

    if not val:
        key = 'uuid'
        val = None
    elif val.startswith('urn:'):
        key = 'urn'
    elif util.is_uuid(val):
        key = 'uuid'
    else:
        raise ValueError('{} is neither a URN nor a UUID!'.format(
            val,
        ))

    return [
        {
            key: val,
            'virkning': _make_effect(obj['fra'], obj['til']),
        }
    ]


@functools.lru_cache(10000)
def _wash_address(k):
    r = lora.session.get('http://dawa.aws.dk/datavask/adresser',
                         params={'betegnelse': k})
    r.raise_for_status()
    return r.json()


def _make_effect(from_, to):
    return {
        'from': util.to_lora_time(from_),
        'to': util.to_lora_time(to or 'infinity'),
        'from_included': True,
        'to_included': False,
    }


def read_paths(paths):
    for p in paths:
        fmt = os.path.splitext(p)[-1].lower()

        if fmt == '.json':
            with open(p) as fp:
                yield json.load(fp)

        elif fmt == '.xlsx':
            yield from openpyxl.load_workbook(
                p, read_only=True, data_only=True,
            )

        else:
            raise ValueError('bad format ' + fmt)


def load_data(sheets, exact=False):
    dest = {}

    remap = {
        "funktionstype": "organisatoriskfunktionstype",
    }

    type_formats = {
        'tilknyttedepersoner': 'urn:dk:cpr:person:{:010d}',
        'myndighed': 'urn:dk:kommune:{:d}',
        'virksomhed': 'urn:dk:cvr:virksomhed:{:d}',
    }

    allow_invalid_types = {
        'adresse',
        'brugertyper',
    }

    ignore_invalid_types = {
        'organisatoriskfunktionstype',
    }

    for sheet in read_paths(sheets):
        if isinstance(sheet, dict):
            dest.update(sheet)
            continue

        out = dest[sheet.title] = []

        print(sheet.title, file=sys.stderr)

        headers = [c.value.lower() for c in sheet[1]]
        headers = [remap.get(v, v) for v in headers]

        for i, row in enumerate(sheet.iter_rows(min_row=2), 2):
            if not i % 5000:
                print(i, file=sys.stderr)

            row = [cell.value for cell in row]

            if not any(row):
                continue

            out.append(dict(map(lambda h, c: (h, c), headers, row)))

    # optionally generate a CPR number in a reproducible way, for test & dev
    if not exact:
        for i, obj in enumerate(itertools.chain.from_iterable(dest.values())):
            # leave some users without a CPR number
            if not i % 100:
                continue

            if 'tilknyttedepersoner' in obj and not obj['tilknyttedepersoner']:
                hired = util.parsedatetime(obj['fra'])

                obj['tilknyttedepersoner'] = int('{:%Y%m%d}{:04d}'.format(
                    # randomly assume that everyone was hired on their 32nd birthday
                    # (note: 32 is divible by four, which is a rather useful)
                    hired.replace(year=hired.year - 32),
                    i % 10000,
                ))

    # ensure that all objects have an ID
    for i, obj in enumerate(itertools.chain.from_iterable(dest.values())):
        if not obj['objektid']:
            obj['objektid'] = str(uuid.uuid4())

    # coerce all dates to strings
    for obj in itertools.chain.from_iterable(dest.values()):
        for k, v in obj.items():
            if isinstance(v, datetime.datetime):
                obj[k] = v.isoformat()

    # some items in the spreadsheet refer to other rows by their bvn
    uuid_mapping = {
        obj['brugervendtnoegle']: obj['objektid']
        for obj in itertools.chain.from_iterable(dest.values())
    }

    # inject some missing UUID mappings?
    uuid_mapping.setdefault(
        'Organisation Aarhus',
        uuid_mapping.get('Aarhus kommune',
                         '59141156-ed0b-457c-9535-884447c5220b')
    )

    for i, obj in enumerate(itertools.chain.from_iterable(dest.values())):
            for k, v in obj.items():
                if k not in lora.ALL_RELATION_NAMES:
                    continue

                val = obj[k]

                if not val or util.is_uuid(val) or str(val).startswith('urn:'):
                    continue

                elif val in uuid_mapping:
                    obj[k] = uuid_mapping[val]

                elif k in type_formats:
                    obj[k] = type_formats[k].format(
                        val if val is not None else i,
                    )

                elif k in allow_invalid_types:
                    pass

                else:
                    if k not in ignore_invalid_types:
                        print('BAD VALUE {!r} for {} in {}'.format(
                            val, k, json.dumps(obj, indent=2, sort_keys=True),
                        ), file=sys.stderr)
                    obj[k] = None

    return dest


def convert(paths, include=None, exact=False):
    print('loading input...', file=sys.stderr)
    sheets = load_data(paths, exact=exact)

    for title, sheet in sheets.items():
        try:
            func = globals()['convert_' + title]
        except KeyError:
            print('cannot convert {}!'.format(title), file=sys.stderr)
            continue

        if include and title not in include:
            print('skipping {}!'.format(title), file=sys.stderr)
            continue

        print('importing {} {}...'.format(len(sheet) - 1, title),
              file=sys.stderr)

        for i, obj in enumerate(sheet[1:], 1):
            if not i % 500:
                print(i)

            yield func(obj)


def convert_klasse(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    return 'PUT', '/klassifikation/klasse/' + obj['objektid'], {
        'note': obj['note'],
        "attributter": {
            "klasseegenskaber": [
                dict(virkning=virkning, **{
                    k: obj[k]
                    for k in (
                        "brugervendtnoegle",
                        "beskrivelse",
                        # "eksempel",
                        "omfang",
                        "titel",
                        # "retskilde",
                        "aendringsnotat",
                        # "soegeord",
                    )
                }),
            ],
        },

        'relationer': {
            k: _make_relation(obj, k)
            for k in (
                "ejer",
                "ansvarlig",
                "overordnetklasse",
                "facet",
                # "redaktoerer",
                # "sideordnede",
                "mapninger",
                # "tilfoejelser",
                # "erstatter",
                # "lovligekombinationer",
            )
        },

        "tilstande": {
            "klassepubliceret": [
                {
                    "publiceret": obj['publiceret'],
                    "virkning": virkning,
                },
            ],
        },
    }


def convert_klassifikation(obj):
    objectid = obj['objektid']

    return 'PUT', '/klassifikation/klassifikation/' + objectid, {
        'note': obj['note'],
        "attributter": {
            "klassifikationegenskaber": [
                {
                    "brugervendtnoegle": obj['brugervendtnoegle'],
                    "beskrivelse": obj['beskrivelse'],
                    "ophavsret": obj['ophavsret'],
                    "kaldenavn": obj['kaldenavn'],
                    "virkning": _make_effect(obj['fra'], obj['til']),
                }
            ]
        },

        'relationer': {
            k: [
                {
                    'uuid': obj[k] if len(obj[k]) == 32 else None,
                    'virkning': _make_effect(obj['fra'], obj['til']),
                },
            ]
            for k in ('ansvarlig', 'ejer')
        },

        "tilstande": {
            "klassifikationpubliceret": [
                {
                    "publiceret": "Publiceret",
                    "virkning": _make_effect(obj['fra'], obj['til']),
                }
            ]
        }
    }


def convert_organisation(obj):
        virkning = _make_effect(obj['fra'], obj['til'])

        return 'PUT', '/organisation/organisation/' + obj['objektid'], {
            'note': obj['note'],
            'attributter': {
                'organisationegenskaber': [
                    {
                        'organisationsnavn': obj['brugervendtnoegle'],
                        'brugervendtnoegle': obj['brugervendtnoegle'],
                        'virkning': virkning,
                    },
                ],
            },
            'tilstande': {
                'organisationgyldighed': [
                    {
                        'gyldighed': obj['gyldighed'],
                        'virkning': virkning,
                    },
                ],
            },
            'relationer': {
                'virksomhed': [
                    {
                        'urn': 'urn:dk:cvr:{}'.format(obj['virksomhed']),
                        'virkning': virkning,
                    }
                ],
                'myndighed': [
                    {
                        'urn': 'urn:dk:kommune:{}'.format(
                            obj['myndighed'],
                        ),
                        'virkning': virkning,
                    }
                ],
                'myndighedstype': [
                    {
                        'urn': 'urn:oio:objekttype:{}'.format(
                            obj['myndighedstype'],
                        ),
                        'virkning': virkning,
                    }
                ],
            }
        }


def convert_organisationenhed(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    addresses = []
    telefon = obj['telefon']
    if obj['postnummer']:
        pass

    if isinstance(telefon, str):
        telefon = telefon.strip()

    if telefon:
        urn = 'urn:magenta.dk:telefon:+45{:08d}'.format(telefon)
        addresses.append({
            'urn': urn,
            'gyldighed': obj['gyldighed'],
            'virkning': virkning,
        })

    if obj['postnummer']:
        if str(obj['postnummer']) == '8100':
            postalcode = 8000
        else:
            postalcode = obj['postnummer']

        if obj['adresse'] == 'Rådhuset':
            address = 'Rådhuspladsen 2'
        else:
            address = obj['adresse']

        addrinfo = _wash_address(
            '{}, {} {}'.format(
                address, postalcode, obj['postdistrikt']
            )
        )

        if len(addrinfo['resultater']) == 1:
            addresses.append({
                'uuid': addrinfo['resultater'][0]['adresse']['id'],
                'gyldighed': obj['gyldighed'],
                'virkning': virkning,
            })

    r = {
        'note': obj['note'],
        'attributter': {
            'organisationenhedegenskaber': [
                {
                    'enhedsnavn': obj['enhedsnavn'],
                    'brugervendtnoegle': obj['brugervendtnoegle'],
                    'virkning': virkning,
                },
            ],
        },
        'tilstande': {
            'organisationenhedgyldighed': [
                {
                    'gyldighed': obj['gyldighed'],
                    'virkning': virkning,
                },
            ],
        },
        'relationer': {
            'adresser': addresses,
            'tilhoerer': [
                {
                    'uuid': obj['tilhoerer'],
                    'virkning': virkning,
                }
            ],
            'tilknyttedeenheder': [
                {
                    'urn': obj['tilknyttedeenheder'],
                    'virkning': virkning,
                }
            ],
            'enhedstype': [
                {
                    'uuid': obj['enhedstype'],
                    'virkning': virkning,
                }
            ],
            'overordnet': [
                {
                    # stash the ORG ID in 'overordnet' --
                    # technically, this violates the
                    # standards, but enables simple queries
                    # for root org units
                    'uuid': obj['overordnet'] or obj['tilhoerer'],
                    'virkning': virkning,
                }
            ],
        }
    }

    return (
        'PUT', '/organisation/organisationenhed/' + obj['objektid'], r,
    )


def convert_itsystem(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    return 'PUT', '/organisation/itsystem/' + obj['objektid'], {
        'note': obj['note'],
        "attributter": {
            "itsystemegenskaber": [
                dict(virkning=virkning, **{
                    k: obj[k]
                    for k in (
                        "brugervendtnoegle",
                        "itsystemnavn",
                        "itsystemtype",
                        "konfigurationreference",
                    )
                }),
            ],
        },

        'relationer': {
            k: _make_relation(obj, k)
            for k in (
                "tilhoerer",
                "tilknyttedeorganisationer",
                # "tilknyttedeenheder",
                # "tilknyttedefunktioner",
                # "tilknyttedebrugere",
                # "tilknyttedeinteressefaellesskaber",
                # "tilknyttedeitsystemer",
                # "tilknyttedepersoner",
                # "systemtyper",
                # "opgaver",
                # "adresser"
            )
        },

        "tilstande": {
            "itsystemgyldighed": [
                {
                    "gyldighed": obj['gyldighed'],
                    "virkning": virkning,
                },
            ],
        },
    }


def convert_facet(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    return 'PUT', '/klassifikation/facet/' + obj['objektid'], {
        'note': obj['note'],
        "attributter": {
            "facetegenskaber": [
                dict(virkning=virkning, **{
                    k: obj[k]
                    for k in (
                        "brugervendtnoegle",
                        "beskrivelse",
                        # "opbygning",
                        # "ophavsret",
                        # "plan",
                        # "supplement",
                        # "retskilde",
                    )
                }),
            ],
        },

        'relationer': {
            k: _make_relation(obj, k)
            for k in (
                "ejer",
                "ansvarlig",
                "facettilhoerer",
                # "redaktoerer",
            )
        },

        "tilstande": {
            "facetpubliceret": [
                {
                    "publiceret": obj['publiceret'],
                    "virkning": virkning,
                },
            ],
        },
    }


def convert_bruger(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    obj['adresser'] = 'urn:mailto:' + obj['email'] if obj['email'] else None

    if obj['brugertyper']:
        obj['brugertyper'] = 'urn:' + obj['brugertyper']

    return 'PUT', '/organisation/bruger/' + obj['objektid'], {
        'note': obj['note'],
        "attributter": {
            "brugeregenskaber": [
                dict(virkning=virkning, **{
                    k: obj[k]
                    for k in (
                        "brugervendtnoegle",
                        "brugernavn",
                        "brugertype",
                    )
                }),
            ],
        },

        'relationer': {
            k: _make_relation(obj, k)
            for k in (
                "tilhoerer",
                "adresser",
                "brugertyper",
                # "opgaver",
                # "tilknyttedeenheder",
                # "tilknyttedefunktioner",
                # "tilknyttedeinteressefaellesskaber",
                # "tilknyttedeorganisationer",
                "tilknyttedepersoner",
                # "tilknyttedeitsystemer",
            )
        },

        "tilstande": {
            "brugergyldighed": [
                {
                    "gyldighed": obj['gyldighed'],
                    "virkning": virkning,
                },
            ],
        },
    }


def convert_organisationfunktion(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    return 'PUT', '/organisation/organisationfunktion/' + obj['objektid'], {
        'note': obj['note'],
        "attributter": {
            "organisationfunktionegenskaber": [
                dict(virkning=virkning, **{
                    k: obj[k]
                    for k in (
                        "brugervendtnoegle",
                        "funktionsnavn",
                    )
                }),
            ],
        },

        'relationer': {
            k: _make_relation(obj, k)
            for k in (
                "organisatoriskfunktionstype",
                # "adresser",
                # "opgaver",
                "tilknyttedebrugere",
                "tilknyttedeenheder",
                "tilknyttedeorganisationer",
                # "tilknyttedeitsystemer",
                # "tilknyttedeinteressefaellesskaber",
                # "tilknyttedepersoner",
            )
        },

        "tilstande": {
            "organisationfunktiongyldighed": [
                {
                    "gyldighed": obj['gyldighed'],
                    "virkning": virkning,
                },
            ],
        },
    }
