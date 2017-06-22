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


def _check_response(r):
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if r.status_code == 400 and r.json():
            raise ValueError(r.json()['message'])
        else:
            raise

    return r


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
    _check_response(r)

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
    _check_response(r)

    try:
        objs = r.json()['results'][0]
    except IndexError:
        return []

    return objs


def create(path, obj, uuid=None):
    if uuid:
        r = session.put('{}{}/{}'.format(LORA_URL, path, uuid), json=obj)
        _check_response(r)
        return uuid
    else:
        r = session.post(LORA_URL + path, json=obj)
        _check_response(r)
        return r.json()['uuid']


def delete(path, uuid):
    r = session.delete('{}{}/{}'.format(LORA_URL, path, uuid))
    _check_response(r)


def update(path, obj):
    r = session.put(LORA_URL + path, json=obj)
    _check_response(r)
    return r.json()['uuid']


def login(username, password):
    if username == 'admin' and password == 'secret':
        return {
            "user": 'Administrator',
            "token": 'kaflaflibob',
            "role": [],
        }
    else:
        return None


def logout(user, token):
    return token == 'kaflaflibob'


organisation = functools.partial(fetch, 'organisation/organisation')
organisation.get = functools.partial(get, 'organisation/organisation')
organisation.delete = functools.partial(delete, 'organisation/organisation')

organisationenhed = functools.partial(fetch, 'organisation/organisationenhed')
organisationenhed.get = \
    functools.partial(get, 'organisation/organisationenhed')
organisationenhed.delete = \
    functools.partial(delete, 'organisation/organisationenhed')

klasse = functools.partial(fetch, 'klassifikation/klasse')
klasse.get = functools.partial(get, 'klassifikation/klasse')
klasse.delete = functools.partial(delete, 'klassifikation/klasse')
