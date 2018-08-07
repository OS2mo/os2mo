#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from concurrent import futures
import collections
import csv
import datetime
import json
import operator
import re
import functools

import click
from werkzeug import datastructures

from ..service import address
from ..service import common
from .. import app
from .. import lora
from .. import util

DATE_PATTERN = re.compile(r'\d{2}-\d{2}-\d{4}')
NUMBER_PATTERN = re.compile(r'\d+')
TIME_COLUMNS = (
    'OrgMapFraDato', 'OrgMapTilDato', 'Loadtime',
    'OrgMapFraDato_2', 'OrgMapTilDato_2', 'Loadtime_2',
    'fradato', 'tildato',
)

ORGID = '59141156-ed0b-457c-9535-884447c5220b'

DUMMY_UUID = '00000000-0000-0000-0000-000000000000'

ORG = {
    "attributter": {
        "organisationegenskaber": [
            {
                "brugervendtnoegle": "Aarhus Kommune",
                "organisationsnavn": "Aarhus Kommune",
                "virkning": {
                    "from": "1976-01-01 00:00:00+01",
                    "to": "infinity",
                },
            },
        ],
    },
    "relationer": {
        "myndighed": [
            {
                "urn": "urn:dk:kommune:751",
                "virkning": {
                    "from": "1976-01-01 00:00:00+01",
                    "to": "infinity",
                },
            },
        ],
        "virksomhed": [
            {
                "urn": "urn:dk:cvr:virksomhed:55133018",
                "virkning": {
                    "from": "1976-01-01 00:00:00+01",
                    "to": "infinity",
                },
            },
        ],
    },
    "tilstande": {
        "organisationgyldighed": [
            {
                "gyldighed": "Aktiv",
                "virkning": {
                    "from": "1976-01-01 00:00:00+01",
                    "to": "infinity",
                },
            },
        ],
    },
}


@functools.lru_cache()
def get_facet(facet_name,
              dry_run=True, verbose=True):
    c = lora.Connector()
    facetids = c.facet(
        bvn=facet_name, ansvarlig=ORGID,
        publiceret='Publiceret',
    )

    if len(facetids) > 1:
        raise ValueError('multiple facets for {!r}!'.format(facet_name))
    elif len(facetids) == 1:
        return facetids[0]

    facetobj = {
        "attributter": {
            "facetegenskaber": [
                {
                    "brugervendtnoegle": facet_name,
                }
            ]
        },
        "tilstande": {
            "facetpubliceret": [
                {
                    "publiceret": "Publiceret",
                }
            ]
        },
        "relationer": {
            # "facettilhoerer": [
            #     {
            #         "objekttype": "klassifikation",
            #         "uuid": None,
            #     }
            # ],
            "ansvarlig": [
                {
                    "objekttype": "organisation",
                    "uuid": ORGID
                }
            ]
        }
    }

    common._set_virkning(facetobj,
                         common._create_virkning(util.NEGATIVE_INFINITY,
                                                 util.POSITIVE_INFINITY))

    click.secho('creating facet {}'.format(facet_name), bold=verbose)

    if verbose:
        click.echo(json.dumps(facetobj, indent=2))

    if dry_run:
        return DUMMY_UUID

    return c.facet.create(facetobj)


@functools.lru_cache(maxsize=None)
def get_class(facet_name, class_name, user_key='', scope='', example='',
              dry_run=True, verbose=True):
    c = lora.Connector()

    facetid = get_facet(facet_name, dry_run, verbose)

    classids = c.klasse(
        titel=class_name or '%',
        bvn=user_key or '%',
        eksempel=example or '%',
        omfang=scope or '%',
        ansvarlig=ORGID,
        facet=facetid,
        publiceret='Publiceret',
    )

    if len(classids) > 1:
        raise ValueError('multiple classes for {!r}!'.format(class_name))
    elif len(classids) == 1:
        return classids[0]

    classobj = {
        "attributter": {
            "klasseegenskaber": [
                {
                    "brugervendtnoegle": user_key,
                    "eksempel": example,
                    "omfang": scope,
                    "titel": class_name,
                }
            ]
        },
        "tilstande": {
            "klassepubliceret": [
                {
                    "publiceret": "Publiceret",
                }
            ]
        },
        "relationer": {
            "facet": [
                {
                    "objekttype": "facet",
                    "uuid": facetid,
                }
            ],
            "ansvarlig": [
                {
                    "objekttype": "organisation",
                    "uuid": ORGID
                }
            ]
        }
    }

    common._set_virkning(classobj,
                         common._create_virkning(util.NEGATIVE_INFINITY,
                                                 util.POSITIVE_INFINITY))

    click.secho('creating class {}'.format(class_name),
                bold=verbose)

    if verbose:
        click.echo(json.dumps(classobj, indent=2))

    if dry_run:
        return DUMMY_UUID

    return c.klasse.create(classobj)


def get_address(value, class_name, user_key, scope, example,
                dry_run=True, verbose=True):
    classid = get_class('Adressetype', class_name, user_key, scope, example,
                        dry_run, verbose)

    assert isinstance(value, (str, int)), 'not an address: {!r}'.format(value)

    return {
        'type': 'address',
        'value': str(value),
        'address_type': {
            'example': example,
            'name': class_name,
            'scope': scope,
            'user_key': user_key,
            'uuid': classid,
        },
    }


class CustomReader(csv.DictReader):
    def __next__(self):
        d = super().__next__()

        for k, v in d.items():
            if not v or v == 'NULL':
                d[k] = None
            elif k in TIME_COLUMNS:
                d[k] = util.parsedatetime(v, None)
            elif isinstance(v, str) and NUMBER_PATTERN.fullmatch(v):
                d[k] = int(v)

        if 'ParentOrgenhedID' not in d:
            levels = [d['Niveau{}_OrgenhedID'].format(i)
                      for i in range(20, 0, -1)
                      if d.get('Niveau{}_OrgenhedID')]

            d['ParentOrgenhedID'] = levels[1] if levels else 0

        return datastructures.ImmutableDict(d)

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = next(self.reader)
            except StopIteration:
                pass
            self.line_num = self.reader.line_num

            for fieldname, indices in datastructures.MultiDict(
                (fn, i)
                for i, fn in enumerate(self._fieldnames)
            ).lists():
                for i, index in enumerate(indices[1:], 2):
                    self._fieldnames[index] += '_' + str(i)

        return self._fieldnames


def read_sheet(path, encoding, delimiter):
    with open(path, 'rt', encoding=encoding) as fp:
        return list(CustomReader(fp, strict=True, delimiter=delimiter or ';'))


ADDRESS_COLUMN_TYPES = {
    'Email': {
        'class_name': 'Emailadresse',
        'user_key': 'email-address',
        'scope': 'EMAIL',
        'example': 'user@example.com',
    },
    'TLF': {
        'class_name': 'Hovednummer',
        'user_key': 'phone',
        'scope': 'PHONE',
        'example': '89402000',
    },
    'Fax': {
        'class_name': 'Telefax',
        'user_key': 'fax',
        'scope': 'PHONE',
        'example': '89402000',
    },
    'Webadresse': {
        'class_name': 'Webaddresse',
        'user_key': 'website',
        'scope': 'WWW',
        'example': 'https://www.aarhus.dk',
    },
    'Ekspeditionstid': {
        'class_name': 'Ekspeditionstid',
        'user_key': 'opening-hours',
        'scope': 'TEXT',
        'example': 'Hverdage 10.00 - 17.00',
    },
    'TLFtid': {
        'class_name': 'Telefontid',
        'user_key': 'phone-hours',
        'scope': 'TEXT',
        'example': 'Hverdage 10.00 - 17.00',
    },
}


def convert_unit(units_by_id, unit,
                 dry_run=True, verbose=True):
    # TODO: create address fields from Adresse1, Adresse2,
    # Ekspeditionstid, Email, Fax, Postbox, Postdistrikt, Postnr, TLF,
    # TLFtid & Webadresse
    addresses = []

    for column_name, mapping in ADDRESS_COLUMN_TYPES.items():
        value = unit.get(column_name)

        if not value:
            continue

        if mapping['scope'] == 'WWW' and ':' not in value:
            value = 'http://' + value

        addresses.append(get_address(
            value,
            **mapping,
            dry_run=dry_run, verbose=verbose,
        ))

    parent = units_by_id.get(unit['ParentOrgenhedID'])

    return '/service/ou/create', {
        'uuid': unit['OrgenhedUUID'],
        'name': unit['OrgenhedNavn'],
        'user_key': str(unit['OrgenhedID']),
        "parent": {
            "uuid": parent['OrgenhedUUID'] if parent else ORGID,
        },
        'validity': {
            'from': util.to_iso_time(unit['OrgMapFraDato']),
            'to': util.to_iso_time(unit['OrgMapTilDato']),
        },
        'addresses': addresses,
    }


def convert_employee(empl):
    # TODO: convert addresses too?

    return '/service/e/create', datastructures.ImmutableDict(
        uuid=empl['uuid'],
        name=empl['Kaldenavn'],
        # TODO: re-enable CPR when we get proper ones
        # cpr_no=empl['CPR'] and '{:010d}'.format(empl['CPR']),
        user_key=empl['Azident'],
        org=datastructures.ImmutableDict(uuid=ORGID),
    )


def convert_engagement(units_by_uuid, empl, dry_run=True, verbose=True):

    userid = empl['uuid']
    unitid = empl['uuid_2']

    if unitid.lower() not in units_by_uuid:
        click.secho(
            'unit {!r} for {!r} not found!'.format(unitid, empl['Azident']),
            bold=True, fg='red',
        )

        return None

    return '/service/e/{}/create'.format(userid), [
        {
            'type': 'engagement',
            'org_unit': {
                'uuid': unitid,
            },
            'engagement_type': {
                'uuid': get_class(
                    'Engagementstype', 'Ikke Angivet', 'N/A',
                    dry_run=dry_run, verbose=verbose,
                ),
            },
            'job_function': empl.get('Stilling') and {
                'uuid': get_class(
                    'Stillingsbetegnelse', empl['Stilling'],
                    dry_run=dry_run, verbose=verbose,
                ),
            },
            'validity': {
                'from': util.to_iso_time(empl['fradato']),
                'to': util.to_iso_time(empl['tildato']),
            }
        }
    ]


def convert_association(units_by_id, empl,
                        dry_run=True, verbose=True):
    try:
        userid = empl['uuid']
        unitid = units_by_id[empl['Tjsted_OrgenhedID']]['OrgenhedUUID']
    except KeyError:
        return None

    return '/service/e/{}/create'.format(userid), [
        {
            'type': 'association',
            'org_unit': {
                'uuid': unitid,
            },
            'association_type': {
                'uuid': get_class('Tilknytningstype', 'Tjenestested',
                                  dry_run=dry_run, verbose=verbose),
            },
            'job_function': empl.get('Stilling') and {
                'uuid': get_class(
                    'Stillingsbetegnelse', empl['Stilling'],
                    dry_run=dry_run, verbose=verbose,
                ),
            },
            'validity': {
                'from': util.to_iso_time(empl['fradato']),
                'to': util.to_iso_time(empl['tildato']),
            }
        }
    ]


def run(target, sheets, dry_run, verbose, jobs, failfast,
        delimiter, charset, **kwargs):
    if any(kwargs.values()):
        unsupported_args = ['--{}'.format(k.replace('_', '-'))
                            for k in sorted(kwargs) if kwargs[k]]

        raise click.BadOptionUsage(
            unsupported_args,
            'unsupported arguments: {}'.format(', '.join(unsupported_args)),
        )

    if len(sheets) != 2:
        raise ValueError('only 2 sheets supported, not {}'.format(len(sheets)))

    click.secho('reading...', bold=True)

    sheet_rows = [
        read_sheet(sheet, charset, delimiter)
        for sheet in sheets
    ]

    click.secho('loading organisational units...', bold=True)

    all_units = sorted(
        (
            d.copy()
            for d in {
                datastructures.ImmutableDict(
                    (k, v)
                    for k, v in unit.items()
                    if not k.endswith('_2')
                )
                for rows in sheet_rows
                for unit in rows
                if 'ParentOrgenhedID' in unit and 'BrugerID' not in unit
            } | {
                datastructures.ImmutableDict(
                    (k[:-2], v)
                    for k, v in unit.items()
                    if k.endswith('_2')
                )
                for rows in sheet_rows
                for unit in rows
                if 'ParentOrgenhedID_2' and 'BrugerID' not in unit
            }
        ),
        key=operator.itemgetter('OrgenhedID'),
    )

    units_by_id = {
        unit['OrgenhedID']: unit
        for unit in all_units
    }

    units_by_uuid = {
        unit['OrgenhedUUID'].lower(): unit
        for unit in all_units
    }

    children = datastructures.OrderedMultiDict(
        (unit['ParentOrgenhedID'], unit)
        for unit in sorted(units_by_id.values(),
                           key=operator.itemgetter('OrgenhedID'))
    )

    def walk_units(units):
        for unit in units:
            yield unit

            yield from walk_units(children.getlist(unit['OrgenhedID']))

    click.secho('loading employees...', bold=True)

    all_employees = {
        datastructures.ImmutableDict(empl.items())
        for rows in sheet_rows
        for empl in rows
        if 'BrugerID' in empl
    }

    click.secho('loading classes...', bold=True)

    job_functions = {
        function_name: get_class('Stillingsbetegnelse', function_name,
                                 dry_run=dry_run, verbose=verbose)
        for function_name in sorted({
            empl['Stilling']
            for empl in all_employees
            if empl.get('Stilling') and isinstance(empl['Stilling'], str)
        })
    }

    click.secho('apply fixups...', bold=True)

    def handler(obj):
        if isinstance(obj, datetime.date):
            return util.to_iso_time(obj)
        else:
            return None

    def ensure_unit(unit, start, end, reason):
        if unit['OrgMapFraDato'] > start:
            click.secho(
                'adjusting start of {!r} ({}) from {} to {} due to {}'
                .format(
                    unit['OrgenhedNavn'],
                    unit['OrgenhedID'],
                    unit['OrgMapFraDato'].date(),
                    start.date(),
                    reason,
                ),
                fg='yellow')
            unit['OrgMapFraDato'] = start

        if unit['OrgMapTilDato'] < end:
            click.secho(
                'adjusting end of {!r} from {} to {} due to {}'
                .format(
                    unit['OrgenhedNavn'],
                    unit['OrgMapTilDato'].date(),
                    end.date(),
                    reason,
                ),
                fg='yellow')
            unit['OrgMapTilDato'] = end

    for employee in all_employees:
        new_employee = dict(employee)
        assert new_employee == employee

        workplace = units_by_uuid.get(employee['uuid_2'].lower())

        if not isinstance(employee.get('Stilling'), str):
            new_employee['Stilling'] = None

        if not workplace:
            click.secho(
                'missing place of work {Tjsted_Navn!r} ({Tjsted_OrgenhedID}) '
                'for {Kaldenavn}!'
                .format(json.dumps(employee, indent=2, default=handler),
                        **employee),
                fg='yellow',
            )

        else:
            ensure_unit(workplace, employee['fradato'], employee['tildato'],
                        "position of " + employee['Azident'])

        associated = units_by_id.get(employee['Tjsted_OrgenhedID'])

        if not associated:
            click.secho(
                'missing associated unit {uuid_2} for {Kaldenavn}!'
                .format(json.dumps(employee, indent=2, default=handler),
                        **employee),
                fg='yellow',
            )

            del new_employee['Tjsted_OrgenhedID']
        elif not (
            employee['fradato'] <= employee['Loadtime'] < employee['tildato']
        ):
            # TODO: I think we only know the very latest place of work?
            del new_employee['Tjsted_OrgenhedID']

        else:
            ensure_unit(associated, employee['fradato'], employee['tildato'],
                        "workplace of " + employee['Azident'])

        if new_employee != employee:
            all_employees.remove(employee)
            all_employees.add(datastructures.ImmutableDict(new_employee))

    roots = [unit for unit in all_units if not unit['ParentOrgenhedID']]

    for unit in reversed(list(walk_units(roots))):
        parent = units_by_id.get(unit['ParentOrgenhedID'])

        if parent and unit['OrgMapFraDato'] < parent['OrgMapFraDato']:
            click.secho(
                'adjusting start from {} to {} since {!r} ({}) does not '
                'overlap {!r} ({})'
                .format(
                    parent['OrgMapFraDato'].date(),
                    unit['OrgMapFraDato'].date(),
                    parent['OrgenhedNavn'],
                    parent['OrgenhedID'],
                    unit['OrgenhedNavn'],
                    unit['OrgenhedID'],
                ),
                fg='yellow')

            parent['OrgMapFraDato'] = unit['OrgMapFraDato']

        if parent and unit['OrgMapTilDato'] > parent['OrgMapTilDato']:
            click.secho(
                'adjusting termination from {} to {} since {!r} ({}) does not '
                'overlap {!r} ({})'
                .format(
                    parent['OrgMapTilDato'].date(),
                    unit['OrgMapTilDato'].date(),
                    parent['OrgenhedNavn'],
                    parent['OrgenhedID'],
                    unit['OrgenhedNavn'],
                    unit['OrgenhedID'],
                ),
                fg='yellow')

            parent['OrgMapTilDato'] = unit['OrgMapTilDato']

    click.secho('converting...', bold=True)

    request_chunks = collections.OrderedDict()

    request_chunks['units'] = [
        convert_unit(units_by_id, unit, dry_run, verbose)
        for unit in walk_units(roots)
    ]

    request_chunks['employees'] = [
        convert_employee(empl) for empl in all_employees
    ]

    request_chunks['engagements'] = list(
        filter(None, (convert_engagement(units_by_uuid, empl, dry_run, verbose)
                      for empl in all_employees))
    )

    request_chunks['associations'] = list(
        filter(None, (convert_association(units_by_id, empl,
                                          dry_run, verbose)
                      for empl in all_employees))
    )

    c = lora.Connector()

    if c.organisation(uuid=ORGID):
        click.echo('organisation already exists!')

    else:
        click.secho('writing organisation...', bold=True)

        if verbose:
            click.echo(json.dumps(ORG, indent=2))

        if not dry_run:
            orgid = c.organisation.create(ORG, ORGID)

            assert orgid == ORGID

    client = app.app.test_client()

    for request_type, post_requests in request_chunks.items():
        click.secho('writing {}...'.format(request_type), bold=True)

        failures = 0

        if request_type == 'units':
            worker_count = 1
        else:
            worker_count = jobs

        with futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            futuremap = {
                executor.submit(client.post, path, json=req): (path, req)
                for path, req in post_requests
            }

            with click.progressbar(
                futures.as_completed(futuremap),
                length=len(post_requests),
                label=request_type,
                show_pos=True,
                width=0,
            ) as bar:
                for future in bar:
                    path, req = futuremap[future]

                    resp = future.result()
                    ok = 200 <= resp.status_code < 300

                    if verbose or not ok:
                        bar.secho(path, bold=True)
                        bar.echo(json.dumps(req, indent=2))

                    if not ok:
                        bar.secho('ERROR: ' + resp.status, bold=True, fg='red')
                        bar.echo(json.dumps(resp.json, indent=2))

                        if failfast:
                            for f in futuremap:
                                f.cancel()
                            raise click.Abort()
                        else:
                            failures += 1

        if failures:
            print(failures, 'failed')
