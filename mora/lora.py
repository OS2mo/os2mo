#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools

import requests

from . import util

LORA_URL = 'http://mox/'

session = requests.Session()


def get(path, uuid, validity=None):
    uuid = str(uuid)

    if validity and validity != 'present':
        now = util.now()

        if validity == 'future':
            def should_include(o):
                s = o['virkning']['from']
                return s != '-infinity' and util.parsedate(s) > now

            params = {
                'virkningfra': str(now),
                'virkningtil': 'infinity',
            }

        elif validity == 'past':
            def should_include(o):
                s = o['virkning']['to']
                return s != 'infinity' and util.parsedate(s) < now

            params = {
                'virkningfra': '-infinity',
                'virkningtil': str(now),
            }
        else:
            raise ValueError('invalid validity {!r}'.format(validity))
    else:
        should_include = None
        params = {}

    r = session.get('{}{}/{}'.format(LORA_URL, path, uuid), params=params)
    r.raise_for_status()

    assert (len(r.json()) == 1 and
            len(r.json()[uuid]) == 1 and
            len(r.json()[uuid][0]['registreringer']) == 1)

    obj = r.json()[uuid][0]['registreringer'].pop()

    if should_include:
        for key in 'relationer', 'attributter', 'tilstande':
            for relvals in obj.get(key, {}).values():
                relvals[:] = [val for val in relvals if should_include(val)]

    return obj


def fetch(path, **params):
    r = session.get(LORA_URL + path, params=params)
    r.raise_for_status()

    objs = r.json()['results'][0]

    return objs


def create(path, obj):
    r = session.post(LORA_URL + path, json=obj)
    r.raise_for_status()
    return r.json()['uuid']


def update(path, obj):
    r = session.put(LORA_URL + path, json=obj)
    r.raise_for_status()
    return r.json()['uuid']


organisation = functools.partial(fetch, 'organisation/organisation')
organisation.get = functools.partial(get, 'organisation/organisation')

organisationenhed = functools.partial(fetch, 'organisation/organisationenhed')
organisationenhed.get = \
    functools.partial(get, 'organisation/organisationenhed')

klasse = functools.partial(fetch, 'klassifikation/klasse')
klasse.get = functools.partial(get, 'klassifikation/klasse')
