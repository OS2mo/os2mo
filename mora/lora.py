#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools

import requests

LORA_URL = 'http://mox/'

session = requests.Session()


def fetch(path, **params):
    r = session.get(LORA_URL + path, params=params)
    r.raise_for_status()

    return r.json()['results'][0]


def login(username, password):
    if username == 'admin' and password == 'secret':
        return {
            "user": 'Administrator',
            "token": 'kaflaflibob',
            "role": ['o-admin'],
        }
    else:
        return None


def logout(user, token):
    return token == 'kaflaflibob'


organisation = functools.partial(fetch, 'organisation/organisation')
organisationenhed = functools.partial(fetch, 'organisation/organisationenhed')
