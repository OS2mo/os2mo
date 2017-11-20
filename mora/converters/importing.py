#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import functools
import uuid

import openpyxl

from .. import util
from .. import lora


def convert(fp):
    wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)

    for sheet in wb:
        yield from convert_sheet(sheet)


def convert_sheet(sheet):
    @functools.lru_cache(10000)
    def wash_address(k):
        r = lora.session.get('http://dawa.aws.dk/datavask/adresser',
                             params={'betegnelse': k})
        r.raise_for_status()
        return r.json()

    cache = collections.OrderedDict()
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

    for clsid in sorted(classes):
        yield 'PUT', '/klassifikation/klasse/' + clsid, {
            "attributter": {
                "klasseegenskaber": [
                    {
                        "brugervendtnoegle": "Afdeling" + clsid[:3],
                        "titel": "Afdeling " + clsid[:3],
                        "beskrivelse": "Dette er en afdeling",
                        "virkning": {
                            "from": "-infinity",
                            "to": "infinity",
                            'from_included': False,
                            'to_included': False
                        },
                    }
                ]
            },
            "tilstande": {
                "klassepubliceret": [
                    {
                        "publiceret": "Publiceret",
                        "virkning": {
                            "from": "-infinity",
                            "to": "infinity",
                            'from_included': False,
                            'to_included': False
                        },
                    }
                ]
            }
        }

    for i, obj in enumerate(cache.values()):
        if i % 100 == 0:
            print(i)

        virkning = {
            'from': util.to_lora_time(obj['fra']),
            'to': util.to_lora_time(obj['til'] or 'infinity'),
            'from_included': True,
            'to_included': False,
        }

        nullrelation = [{
            'uuid': None,
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
                            'urn': 'urn:dk:kommune:{}'.format(
                                obj['myndighed'],
                            ),
                            'virkning': virkning,
                        }
                    ] if obj['myndighed'] else nullrelation,
                    'myndighedstype': [
                        {
                            'urn': 'urn:oio:objekttype:{}'.format(
                                obj['myndighedstype'],
                            ),
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

                addrinfo = wash_address(
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
