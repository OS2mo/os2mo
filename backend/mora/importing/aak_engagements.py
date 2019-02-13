#
# Copyright (c) 2017-2019, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import functools
import json

import click
import grequests
import pyexcel
import requests

from .. import lora
from .. import util
from ..service import common

from . import processors


def run(sheets, target, delimiter, include, jobs, **kwargs):
    click.echo('loading...')

    if any(kwargs.values()):
        unsupported_args = [k for k in sorted(kwargs) if kwargs[k]]

        raise click.BadOptionUsage(
            'unsupported arguments: {}'.format(', '.join(unsupported_args)),
        )

    if len(sheets) != 1:
        raise ValueError('only 1 sheet supported, not {}'.format(len(sheets)))

    sheet = pyexcel.get_sheet(file_name=sheets[0],
                              delimiter=delimiter or ';',
                              name_columns_by_row=0)

    # convert header names to lowercase, for consistency, and
    # strip any UTF-8 BOM
    headers = [c.lower().lstrip('\ufeff').strip() for c in sheet.colnames]

    session = requests.Session()

    @functools.lru_cache()
    def getclass(orgid, typename, **kwargs):
        r = session.get(
            '{}/service/o/{}/f/{}'.format(target.rstrip('/'),
                                          orgid, typename),
            headers={
                'X-Requested-With': 'XMLHttpRequest',
            },
        )

        assert r.ok

        for addrtype in r.json()['data']['items']:
            if all(addrtype[k] == v for k, v in kwargs.items()):
                return addrtype

    c = lora.Connector()

    unitids = set(map(
        str.lower,
        sheet.column[headers.index('tilknyttetenhed')],
    ))
    units = dict(c.organisationenhed.get_all(uuid=unitids))

    users = collections.OrderedDict()
    userrels = collections.defaultdict(collections.OrderedDict)

    missing_engagements = collections.Counter()

    with click.progressbar(
        sheet.rows(),
        label='processing',
        show_pos=True,
        width=0,
        length=sheet.number_of_rows(),
    ) as bar:
        for row in bar:
            obj = dict(zip(headers, row))

            userid = obj['objektid']
            orgid = obj['tilhoerer']
            unitid = obj['tilknyttetenhed'].lower()

            # fixup for aarhus
            if orgid == '3a87187c-f25a-40a1-8d42-312b2e2b43bd':
                orgid = "a5769433-09df-4f92-98ae-a3e45501da88"

            user = {
                "name": obj['brugernavn'],
                "user_key": obj['brugervendtnoegle'],
                "uuid": obj['objektid'],
                "org": {
                    "uuid": orgid,
                },
            }

            if include and all(s not in obj['brugernavn']
                               for s in include):
                continue

            if (
                obj['tilknyttedepersoner'] and
                obj['tilknyttedepersoner'] != 'NULL'
            ):
                user['cpr_no'] = obj['tilknyttedepersoner']

            if userid in users:
                assert users[userid] == user
            else:
                users[userid] = user

            addrid = processors.wash_address(obj['adresse'],
                                             obj['postnummer'],
                                             obj['postdistrikt'])

            validity = {
                'from': util.to_iso_time(obj['fra']),
                'to': util.to_iso_time(obj['til']),
            }

            if unitid not in units:
                missing_engagements[userid] += 1

            else:
                validity['from'] = util.to_iso_time(max(
                    util.parsedatetime(obj['fra']),
                    common.get_effect_from(
                        units[unitid]['tilstande']
                        ['organisationenhedgyldighed'][0],
                    ),
                ))

                userrels[userid][unitid] = {
                    "type": "engagement",
                    "org_unit": {
                        "uuid": unitid,
                    },
                    "engagement_type": getclass(orgid, "engagement_type"),
                    'validity': validity,
                }

            if addrid:
                userrels[userid][addrid] = {
                    'type': 'address',
                    'address_type': getclass(orgid, "address_type",
                                             user_key="AdresseLokation"),
                    'uuid': addrid,
                    'validity': validity,
                }

            if obj['email'] and obj['email'] != 'NULL':
                userrels[userid][obj['email']] = {
                    'type': 'address',
                    'address_type': getclass(orgid, "address_type",
                                             user_key="Email"),
                    'value': obj['email'],
                    'validity': validity,
                }

            if obj['telefon'] and obj['telefon'] != 'NULL':
                userrels[userid][obj['telefon']] = {
                    'type': 'address',
                    'address_type': getclass(orgid, "address_type",
                                             user_key="Telefon"),
                    'value': str(obj['telefon']),
                    'validity': validity,
                }

    if unitids != units.keys():
        click.secho(
            '{} missing units affecting {} engagements!'.format(
                len(unitids) - len(units),
                sum(missing_engagements.values()),
            ),
            fg='red', bold=True,
        )

    with click.progressbar(users.values(),
                           label='creating employees',
                           show_pos=True, width=0) as bar:

        for r in grequests.imap(
            (
                grequests.post(target.rstrip('/') + '/service/e/create',
                               session=session, json=user)
                for user in bar
            ),
            size=jobs,
        ):
            if not r.ok:
                click.secho('error creating:', fg='red', bold=True)
                click.echo('< {}\n> {}'.format(
                    json.dumps(user, indent=2),
                    r.text,
                ))

    with click.progressbar(label='connecting employees',
                           length=sum(map(len, userrels.values())),
                           show_pos=True, width=0) as bar:

        for r in grequests.imap(
            (
                grequests.post(
                    '{}/service/e/{}/create'.format(target.rstrip('/'),
                                                    userid),
                    session=session, json=list(req.values()),
                )
                for userid, req in userrels.items()
            ),
            size=jobs,
        ):
            # this is kind of horrible, but requests give us no easy
            # way of extract the original parameter to the request
            # from the response
            bar.update(len(json.loads(r.request.body.decode('utf-8'))))

            if not r.ok:
                click.secho('error connecting:', fg='red', bold=True)
                click.echo('< {}\n> {}'.format(
                    json.dumps(user, indent=2),
                    r.text,
                ))
