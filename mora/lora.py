#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import copy
import datetime
import functools
import typing

import requests

from . import util

LORA_URL = 'http://mox/'

session = requests.Session()
session.verify = True


def _check_response(r):
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if r.status_code == 400 and r.json():
            raise ValueError(r.json()['message'])
        else:
            raise

    return r


def _get_restrictions_for(*,
                          effective_date: str=None, validity: str=None,
                          **params) -> (dict, typing.Callable):
    '''Get URL parameters for restricting effects by the specified period
    rather than today/now.

    All other parameters wind up in the dict as-is.

    Return a pair containing the mapping/parameters, and a function
    for processing elements.

    '''

    restrictions = {}

    if not effective_date:
        today = util.now().date()
    else:
        today = util.parsedatetime(effective_date).date()

    tomorrow = today + datetime.timedelta(days=1)

    if not validity or validity == 'present':
        should_include = None

        restrictions.update(
            virkningfra=str(today),
            virkningtil=str(tomorrow),
        )

    elif validity == 'future':
        def should_include(o):
            s = o['virkning']['from']
            return s != '-infinity' and util.parsedatetime(s).date() > today

        restrictions.update(
            virkningfra=str(tomorrow),
            virkningtil='infinity',
        )

    elif validity == 'past':
        def should_include(o):
            s = o['virkning']['to']
            return s != 'infinity' and util.parsedatetime(s).date() <= today

        restrictions.update(
            virkningfra='-infinity',
            virkningtil=str(today),
        )

    else:
        raise ValueError('invalid validity {!r}'.format(validity))

    restrictions.update(params)

    if should_include:
        def apply_restriction_func(entries):
            keys = 'relationer', 'attributter', 'tilstande'
            r = []

            for entry in copy.deepcopy(entries):
                for typekey in keys:
                    typeval = entry.get(typekey, {})

                    for itemkey in list(typeval):
                        typeval[itemkey][:] = filter(should_include,
                                                     typeval[itemkey])

                if any(entry.get(key) for key in keys):
                    r.append(entry)

            return r

    else:
        def apply_restriction_func(entries):
            return entries

    return restrictions, apply_restriction_func


def get(path, uuid, **params):
    uuid = str(uuid)

    loraparams, apply_restriction_func = _get_restrictions_for(**params)

    r = session.get('{}{}/{}'.format(LORA_URL, path, uuid),
                    params=loraparams)
    _check_response(r)

    assert (len(r.json()) == 1 and
            len(r.json()[uuid]) == 1)

    registrations = r.json()[uuid][0]['registreringer']

    if params.keys() & {'registreretfra', 'registrerettil'}:
        return registrations

    assert len(registrations) == 1

    return apply_restriction_func(registrations)[0]


def fetch(path, **params):
    loraparams, apply_restriction_func = _get_restrictions_for(**params)

    r = session.get(LORA_URL + path, params=loraparams)
    _check_response(r)

    try:
        objs = r.json()['results'][0]
    except IndexError:
        return []

    return apply_restriction_func(objs)


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
