#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import datetime
import itertools
import json
import os
import sys
import uuid

import click
import pyexcel

from . import processors
from .. import util
from .. import lora
from ..service import address


# TODO: don't hardcode these, look into the imported data instead?
ADDRESS_COLUMN_SCOPES = {
    'email': 'EMAIL',
    'telefon': 'PHONE',
    'www': 'WWW',
    'ean': 'EAN',
    'adresse': 'DAR',
}

OPGAVER_COLUMNS = {
    'lederniveau',
    'lederansvar',
    'opgaver'
}


def nolower(s: str) -> str:
    return s if not s or not s.islower() else s.capitalize()


def _make_relation(obj, k):
    val = obj[k]
    valtype = obj.get(k + '_type')

    if not val or val == 'NULL':
        return []
    elif val.startswith('urn:'):
        key = 'urn'
    elif util.is_uuid(val):
        key = 'uuid'
    else:
        raise ValueError('{}: {} is neither a URN nor a UUID!'.format(
            k, val,
        ))

    return [
        {
            key: val,
            'objekttype': valtype,
            'virkning': _make_effect(obj['fra'], obj['til']),
        }
    ]


def _make_addresses_relation(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    r = []

    assert 'adresser' not in obj

    for column, scope in sorted(ADDRESS_COLUMN_SCOPES.items()):
        if column not in obj:
            continue

        v = obj[column]
        t = obj.get(column + '_type')

        if util.is_uuid(v):
            r.append({
                'uuid': v,
                'objekttype': t or 'DAR',
                'virkning': virkning,
            })

        elif v:
            if not isinstance(v, str) or not v.startswith('urn:'):
                if scope == 'PHONE':
                    v = str(v)
                    if not v.startswith('+45'):
                        v = '+45' + v.zfill(8)

                v = address.URN_PREFIXES[scope] + str(v)

            r.append({
                'urn': v,
                'objekttype': t or 'Adresse',
                'virkning': virkning,
            })

    return r


def _make_opgaver_relation(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    r = []

    for column in OPGAVER_COLUMNS:
        v = obj.get(column)
        t = column

        if not v:
            continue

        r.append({
            'uuid': v,
            'objekttype': t if t is not 'opgaver' else None,
            'virkning': virkning,
        })

    return r


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

        else:
            try:
                book = pyexcel.get_book(file_name=p, name_columns_by_row=0)
            except TypeError:
                book = pyexcel.get_book(file_name=p)

            yield from book


def load_data(sheets, exact=False):
    # use an ordered dictionary to ensure consistent walk order if the types
    dest = collections.OrderedDict()

    remap = {
        "funktionstype": "organisatoriskfunktionstype",
    }

    type_formats = {
        'tilknyttedepersoner': ('urn:dk:cpr:person:{:010d}', int),
        'myndighed': ('urn:dk:kommune:{:d}', int),
        'virksomhed': ('urn:dk:cvr:virksomhed:{:d}', int),
    }

    allow_invalid_types = {
        'brugertyper',
    }

    ignore_invalid_types = {
        'organisatoriskfunktionstype',
    }

    for sheet in read_paths(sheets):
        if isinstance(sheet, dict):
            for k, v in sheet.items():
                dest.setdefault(k, []).extend(v)
            continue

        print(sheet.name, file=sys.stderr)

        out = dest.setdefault(sheet.name, [])

        sheet.name_columns_by_row(0)

        headers = [c.lower() for c in sheet.colnames]
        headers = [remap.get(v, v) for v in headers]

        assert len(set(headers)) == len(headers), \
            'duplicate headers in ' + sheet.name

        for i, row in enumerate(sheet.rows()):
            if not any(row):
                continue

            if not i % 5000:
                print(i, file=sys.stderr)

            out.append(dict(map(lambda h, c: (h, c), headers, row)))

    if not exact:
        # optionally generate a CPR number in a reproducible way, for
        # test & dev
        for i, obj in enumerate(itertools.chain.from_iterable(dest.values())):
            # leave some users without a CPR number
            if not i % 100:
                continue

            if 'tilknyttedepersoner' in obj and not obj['tilknyttedepersoner']:
                hired = util.parsedatetime(obj['fra'])

                obj['tilknyttedepersoner'] = int('{:%d%m%y}{:04d}'.format(
                    # randomly assume that everyone was hired on their
                    # 32nd birthday (note: 32 is divible by four,
                    # which is a rather useful property)
                    hired.replace(year=hired.year - 32),
                    i % 10000,
                ))

        # ensure that all objects have an ID
        for i, obj in enumerate(itertools.chain.from_iterable(dest.values())):
            if not obj.get('objektid'):
                obj['objektid'] = str(uuid.uuid4())

    # coerce all dates to strings
    for obj in itertools.chain.from_iterable(dest.values()):
        for k, v in obj.items():
            if isinstance(v, datetime.datetime):
                obj[k] = v.isoformat()
            elif v == '':
                obj[k] = None

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
        postaldistrict = obj.pop('postdistrikt', None)
        postalcode = obj.pop('postnummer', None)
        address = obj.pop('adresse', None)

        if exact or util.is_uuid(address):
            # just use it
            obj['adresse'] = address
            obj['adresse_type'] = obj.get('adresse_type')

        elif address and postalcode and postaldistrict:

            obj['adresse'] = processors.wash_address(address, postalcode,
                                                     postaldistrict)
            obj['adresse_type'] = obj.get('adresse_type')

        else:
            obj['adresse'] = None
            obj['adresse_type'] = None

        for k, v in obj.items():
                val = obj[k]

                if isinstance(val, str):
                    val = val.strip()

                if (
                    not val or
                    val == 'NULL' or
                    util.is_uuid(val) or
                    str(val).startswith('urn:')
                ):
                    continue

                elif k in type_formats:
                    try:
                        fmt, fn = type_formats[k]
                        obj[k] = fmt.format(fn(val if val is not None else i))
                    except ValueError as exc:
                        print('Unknown value {!r} for {}: {}'.format(
                            v, k, exc.args[0],
                        ))

                elif k not in lora.ALL_RELATION_NAMES:
                    continue

                elif k == 'tilknyttetenhed':
                    print(obj)

                    dest['organisationfunktion'].append(dict(
                        objektid=str(uuid.uuid4()),
                        tilknyttedeenheder=v,
                        tilknyttedebrugere=obj['objektid'],
                        tilknyttedeorganisationer=(
                            obj['tilknyttedeorganisationer']
                        ),
                        funktionsnavn='Tilknytning',
                        brugervendtnoegle='42',
                        fra=obj['fra'],
                        til=obj['til'],
                    ))

                    del obj[k]

                elif val in uuid_mapping:
                    obj[k] = uuid_mapping[val]

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

        print('importing {} {}...'.format(len(sheet), title),
              file=sys.stderr)

        for i, obj in enumerate(sheet, 1):
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
                        "eksempel",
                        "omfang",
                        "titel",
                        "retskilde",
                        "aendringsnotat",
                        "soegeord",
                    )
                    if k in obj
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
                "redaktoerer",
                "sideordnede",
                "mapninger",
                "tilfoejelser",
                "erstatter",
                "lovligekombinationer",
            )
            if k in obj
        },

        "tilstande": {
            "klassepubliceret": [
                {
                    "publiceret": nolower(obj['publiceret']),
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
                    'uuid': obj[k] if obj[k] and len(obj[k]) == 32 else None,
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
                        'gyldighed': nolower(obj['gyldighed']),
                        'virkning': virkning,
                    },
                ],
            },
            'relationer': {
                k: _make_relation(obj, k)
                for k in (
                    "adresser",
                    "ansatte",
                    "branche",
                    "myndighed",
                    "myndighedstype",
                    "opgaver",
                    "overordnet",
                    "produktionsenhed",
                    "skatteenhed",
                    "tilhoerer",
                    "tilknyttedebrugere",
                    "tilknyttedeenheder",
                    "tilknyttedefunktioner",
                    "tilknyttedeinteressefaellesskaber",
                    "tilknyttedeitsystemer"
                    "tilknyttedeorganisationer",
                    "tilknyttedepersoner",
                    "virksomhed",
                    "virksomhedstype",
                )
                if k in obj
            },
        }


def convert_organisationenhed(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

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
                    'gyldighed': nolower(obj['gyldighed']),
                    'virkning': virkning,
                },
            ],
        },
        'relationer': {
            'adresser': _make_addresses_relation(obj),
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
                    if k in obj
                }),
            ],
        },

        'relationer': {
            k: _make_relation(obj, k)
            for k in (
                "tilhoerer",
                "tilknyttedeorganisationer",
                "tilknyttedeenheder",
                "tilknyttedefunktioner",
                "tilknyttedebrugere",
                "tilknyttedeinteressefaellesskaber",
                "tilknyttedeitsystemer",
                "tilknyttedepersoner",
                "systemtyper",
                "opgaver",
                "adresser"
            )
            if k in obj
        },

        "tilstande": {
            "itsystemgyldighed": [
                {
                    "gyldighed": nolower(obj['gyldighed']),
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
                        "opbygning",
                        "ophavsret",
                        "plan",
                        "supplement",
                        "retskilde",
                    )
                    if k in obj
                }),
            ],
        },

        'relationer': {
            k: _make_relation(obj, k)
            for k in (
                "ejer",
                "ansvarlig",
                "facettilhoerer",
                "redaktoerer",
            )
            if k in obj
        },

        "tilstande": {
            "facetpubliceret": [
                {
                    "publiceret": nolower(obj['publiceret']),
                    "virkning": virkning,
                },
            ],
        },
    }


def convert_bruger(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    if obj['brugertyper']:
        obj['brugertyper'] = 'urn:' + obj['brugertyper']

    rels = {
        k: _make_relation(obj, k)
        for k in (
            "tilhoerer",
            "adresser",
            "brugertyper",
            "opgaver",
            "tilknyttedeenheder",
            "tilknyttedefunktioner",
            "tilknyttedeinteressefaellesskaber",
            "tilknyttedeorganisationer",
            "tilknyttedepersoner",
            "tilknyttedeitsystemer",
        )
        if k in obj
    }

    rels['adresser'] = _make_addresses_relation(obj)

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
                    if k in obj
                }),
            ],
        },

        'relationer': rels,

        "tilstande": {
            "brugergyldighed": [
                {
                    "gyldighed": nolower(obj['gyldighed']),
                    "virkning": virkning,
                },
            ],
        },
    }


def convert_organisationfunktion(obj):
    virkning = _make_effect(obj['fra'], obj['til'])

    rels = {
        k: _make_relation(obj, k)
        for k in (
            "organisatoriskfunktionstype",
            "adresser",
            "tilknyttedebrugere",
            "tilknyttedeenheder",
            "tilknyttedeorganisationer",
            "tilknyttedeitsystemer",
            "tilknyttedeinteressefaellesskaber",
            "tilknyttedepersoner",
        )
        if k in obj
    }

    if not obj.keys().isdisjoint(OPGAVER_COLUMNS):
        rels['opgaver'] = _make_opgaver_relation(obj)

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
                    if k in obj
                }),
            ],
        },

        'relationer': rels,

        "tilstande": {
            "organisationfunktiongyldighed": [
                {
                    "gyldighed": nolower(obj['gyldighed']),
                    "virkning": virkning,
                },
            ],
        },
    }


def run(target, sheets, dry_run, verbose, jobs, failfast,
        include, check, exact, **kwargs):

    if any(kwargs.values()):
        unsupported_args = [k for k in sorted(kwargs) if kwargs[k]]

        raise click.BadOptionUsage(
            'unsupported arguments: {}'.format(', '.join(unsupported_args)),
        )

    start = util.now()

    sheetlines = convert(sheets, include=include, exact=exact)

    if dry_run:
        for method, path, obj in sheetlines:
            print(method, path,
                  json.dumps(obj, indent=2))

        return

    def fail(r, exc):
        if verbose:
            print(r.url)
        print(*exc.args)
        if failfast:
            raise exc

    # only use grequests for parallel workloads -- and import it
    # lazily to avoid deadlocks caused by its horrible monkey patches
    # to builtins
    if jobs > 1:  # pragma: no cover
        import grequests

        responses = grequests.imap(
            (
                grequests.request(
                    method if not check else 'GET',
                    target + path.rstrip('/'),
                    json=obj,
                    session=lora.session,
                )
                for method, path, obj in sheetlines
            ),
            size=jobs,
            exception_handler=fail,
        )
    else:
        responses = (
            lora.session.request(
                method if not check else 'GET',
                target + path.rstrip('/'),
                json=obj,
            )
            for method, path, obj in sheetlines
        )

    total = 0

    for r in responses:
        if verbose:
            print(r.url)

        if check:
            if r.ok:
                print('EXISTS:', r.request.path_url)
            elif r.status_code == 404:
                print('CREATE:', r.request.path_url)

        elif not r.ok:
            try:
                print(r.status_code, r.json())
            except ValueError:
                print(r.status_code, r.text)

        if failfast:
            r.raise_for_status()
        else:
            total += 1

    duration = util.now() - start

    print('imported {} objects in {} ({} per second)'.format(
        total, duration, total / duration.total_seconds(),
    ))
