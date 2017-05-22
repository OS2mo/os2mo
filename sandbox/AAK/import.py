#!/usr/bin/env python3
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import argparse
import datetime
import itertools
import json
import os
import shelve
import sys
import uuid

import grequests
import openpyxl
import requests
import tzlocal


def _dt2str(dt):
    '''Convert a datetime to string

    We consider anything before 1900 or after y9k as "infinity"

    '''

    if not isinstance(dt, datetime.datetime):
        return dt
    elif dt.year >= 9000:
        return 'infinity'
    elif dt.year < 1900:
        return '-infinity'
    else:
        if not dt.tzinfo:
            dt = tzlocal.get_localzone().localize(dt)

        return dt.isoformat()


ADDR_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'addr.db')


class AddrCache(shelve.DbfilenameShelf):
    def __init__(self):
        super().__init__(ADDR_CACHE_FILE, 'c', 4)

    def __getitem__(self, k):
        try:
            return super().__getitem__(k)
        except KeyError:
            r = requests.get('http://dawa.aws.dk/datavask/adresser',
                             params={'betegnelse': k})
            r.raise_for_status()
            d = self[k] = r.json()
            return d


def _read_sheet(sheet):
    now = datetime.datetime.now(tzlocal.get_localzone())
    cache = {}
    classes = set()
    rows = sheet.rows

    headers = [c.value for c in next(rows)]

    print('importing {} {}'.format(
        sheet.max_row, sheet.title,
    ))

    for row in rows:
        # unpack the row into a dict of the values
        obj = dict(map(lambda h, c: (h, c.value), headers, row))

        # ensure the object has an ID
        if not obj['objektid']:
            obj['objektid'] = str(uuid.uuid4())

        cache[obj['brugervendtnoegle']] = obj
        if 'enhedstype' in obj:
            classes.add(obj['enhedstype'])

    for clsid in classes:
        yield 'PUT', '/klassifikation/klasse/' + clsid, {
            "attributter": {
                "klasseegenskaber": [
                    {
                        "brugervendtnoegle": "Afdeling",
                        "titel": "Afdeling",
                        "beskrivelse": "Dette er en afdeling",
                        "virkning": {
                            "from": _dt2str(now),
                            "to": "infinity",
                        },
                    }
                ]
            },
            "tilstande": {
                "klassepubliceret": [
                    {
                        "publiceret": "Publiceret",
                        "virkning": {
                            "from": _dt2str(now),
                            "to": "infinity",
                        },
                    }
                ]
            }
        }

    for i, obj in enumerate(cache.values()):
        if i % 50 == 0:
            print(i)

        virkning = {
            'from': _dt2str(obj['fra']),
            'to': _dt2str(obj['til']) or 'infinity',
        }
        nullrelation = [{
            'virkning': virkning,
        }]

        if sheet.title == 'organisation':
            yield 'PUT', '/organisation/organisation/' + obj['objektid'], {
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
                    ] if obj['virksomhed'] else nullrelation,
                    'myndighed': [
                        {
                            'urn': 'urn:dk:kommune:{}'.format(obj['myndighed']),
                            'virkning': virkning,
                        }
                    ] if obj['myndighed'] else nullrelation,
                    'myndighedstype': [
                        {
                            'urn': 'urn:oio:objekttype:' + obj['myndighedstype'],
                            'virkning': virkning,
                        }
                    ] if obj['myndighedstype'] else nullrelation,
                }
            }

        elif sheet.title == 'organisationenhed':
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

                with AddrCache() as addrcache:
                    addrinfo = addrcache[
                        '{}, {} {}'.format(
                            address, postalcode, obj['postdistrikt']
                        )
                    ]

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
                    'adresser': addresses or nullrelation,
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
                            'uuid': (
                                cache[obj['overordnet']]['objektid']
                                if obj['overordnet']
                                else obj['tilhoerer']
                            ),
                            'virkning': virkning,
                        }
                    ],
                }
            }

            yield ('PUT', '/organisation/organisationenhed/' + obj['objektid'],
                   r)
        else:
            raise ValueError(sheet.title)


def import_file(url, fp, verbose=False):
    wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
    sheetlines = itertools.chain.from_iterable(map(_read_sheet, wb))

    if not url:
        for method, path, obj in sheetlines:
            print(method, path,
                  json.dumps(obj, check_circular=False, indent=2))
        return

    session = grequests.Session()
    requests = (
        grequests.request(
            method, url + path, session=session,
            # reload the object to break duplicate entries
            json=json.loads(json.dumps(obj, check_circular=False)),
        )
        for method, path, obj in sheetlines
    )

    def fail(r, exc):
        if verbose:
            print(r.url)
        print(*exc.args)

    for r in grequests.imap(requests, size=6, exception_handler=fail):
        if verbose:
            print(r.url)

        if not r.ok:
            try:
                print(r.status_code, r.json())
            except ValueError:
                print(r.status_code, r.text)
        r.raise_for_status()


def main(argv):
    parser = argparse.ArgumentParser(
        description='Import an Excel spreadsheet into LoRa',
    )

    parser.add_argument('spreadsheet', type=argparse.FileType('rb'),
                        help='the spreadsheet to import')
    parser.add_argument('server', type=str,
                        help='URL', nargs='?')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='show requests')

    args = parser.parse_args(argv)

    import_file(args.server, args.spreadsheet, args.verbose)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
