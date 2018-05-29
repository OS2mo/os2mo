#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools

import requests

FORMATTERS = [
    lambda vejnavn, husnummer, postnummer:
    {
        'vejnavn': vejnavn,
        'husnr': husnummer,
        'postnr': postnummer,
        'fuzzy': 'true',
        'struktur': 'mini'
    },
    lambda vejnavn, husnummer, postnummer:
    {
        'q': vejnavn,
        'husnr': husnummer,
        'postnr': postnummer,
        'fuzzy': 'true',
        'struktur': 'mini'
    },
    lambda vejnavn, husnummer, postnummer:
    {
        'q': vejnavn,
        'etage': "",
        'husnr': husnummer,
        'postnr': postnummer,
        'fuzzy': 'true',
        'struktur': 'mini'
    },
]


@functools.lru_cache()
def lookup(vejnavn, husnummer, bynavn, postnummer):
    for formatter in FORMATTERS:
        params = formatter(vejnavn, husnummer, postnummer)
        r = requests.get("http://dawa.aws.dk/adresser/", params=params)
        if len(r.json()) == 1:
            return r.json()[0]['id']
