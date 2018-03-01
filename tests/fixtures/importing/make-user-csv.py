#!/usr/bin/env python3
#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import csv
import datetime
import itertools
import sys
import uuid

# list of names obtained from Statistics Denmark
first_names = [
    'Anne',
    'Kirsten',
    'Mette',
    'Hanne',
    'Anna',
    'Helle',
    'Susanne',
    'Lene',
    'Maria',
    'Marianne',
    'Lone',
    'Camilla',
    'Inge',
    'Pia',
    'Karen',
    'Bente',
    'Louise',
    'Charlotte',
    'Jette',
    'Tina',
    'Peter',
    'Jens',
    'Michael',
    'Lars',
    'Henrik',
    'Thomas',
    'Søren',
    'Jan',
    'Christian',
    'Martin',
    'Niels',
    'Anders',
    'Morten',
    'Jesper',
    'Jørgen',
    'Hans',
    'Mads',
    'Per',
    'Ole',
    'Rasmus',
]

last_names = [
    'Nielsen',
    'Jensen',
    'Hansen',
    'Pedersen',
    'Andersen',
    'Christensen',
    'Larsen',
    'Sørensen',
    'Rasmussen',
    'Jørgensen',
    'Petersen',
    'Madsen',
    'Kristensen',
    'Olsen',
    'Thomsen',
    'Christiansen',
    'Poulsen',
    'Johansen',
    'Møller',
    'Mortensen',
]

first_birthday = datetime.date(1950, 1, 1)
start_day = datetime.date(1900, 1, 1)

csv_fields = (
    'objektid',
    'note',
    'fra',
    'til',
    'brugervendtnoegle',
    'brugernavn',
    'adresse',
    'postnummer',
    'postdistrikt',
    'adresse_type',
    'email',
    'email_type',
    'telefon',
    'telefon_type',
    'brugertype',
    'brugertyper',
    'tilhoerer',
    'gyldighed',
    'tilknyttedepersoner',
)

writer = csv.DictWriter(sys.stdout, csv_fields)
writer.writeheader()

for i, (first_name, last_name) in enumerate(
    itertools.product(first_names, last_names)
):
    name = ' '.join((first_name, last_name))

    # assign CPR numbers sequentially
    cpr = '{:%Y%m%d}{:04d}'.format(
        first_birthday + datetime.timedelta(days=i),
        i % 10000,
    )

    # and use nice and reproducable UUIDs
    objectid = str(uuid.uuid3(
        uuid.NAMESPACE_URL,
        'http://mox.magenta.dk/person-{}'.format(cpr),
    ))

    writer.writerow({
        'objektid': objectid,
        'brugernavn': '{} {}'.format(first_name, last_name),
        'brugervendtnoegle': 'User{}'.format(i),
        'note': 'Auto-genereret bruger #{}'.format(i),
        'tilknyttedepersoner': cpr,
        'fra': start_day.isoformat(),
        'tilhoerer': '3a87187c-f25a-40a1-8d42-312b2e2b43bd',
        'gyldighed': 'Aktiv',
    })
