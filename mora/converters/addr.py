#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import re

import requests

from .. import lora

session = requests.Session()

MUNICIPALITY_CODE_PATTERN = re.compile('urn:dk:kommune:(\d+)')


def get_address(addrid: str):
    'Obtain an address from DAWA'

    # unfortunately, we cannot live with struktur=mini, as it omits
    # the formatted address :(

    r = session.get(
        'http://dawa.aws.dk/adresser/' + addrid,
        params={
            'noformat': '1',
        },
    )
    if r.status_code == 404:
        raise KeyError(addrid)

    r.raise_for_status()

    return r.json()


def find_address(query: str, municipality: str=None):
    addrs = requests.get(
        'http://dawa.aws.dk/adresser/autocomplete',
        params={
            'noformat': '1',
            'kommunekode': municipality,
            'q': query,
        },
    ).json()

    for addrinfo in addrs:
        yield {
            "UUID_EnhedsAdresse": addrinfo['adresse']['id'],
            "postdistrikt": addrinfo['adresse']['postnrnavn'],
            "postnr": addrinfo['adresse']['postnr'],
            "vejnavn": addrinfo['tekst'],
        }


def autocomplete_address(query: str, orgid: str):
    if orgid:
        org = lora.organisation.get(orgid)

        for myndighed in org['relationer']['myndighed']:
            m = MUNICIPALITY_CODE_PATTERN.fullmatch(myndighed.get('urn', ''))

            if m:
                code = int(m.group(1))
                break
        else:
            return 'No local municipality found!', 501
    else:
        code = None

    return list(find_address(query, code))
