#!/usr/bin/env python3
#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import argparse
import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(
    description='Import some test data into LoRa',
)

parser.add_argument('server', type=str)

args = parser.parse_args()

headers = {'Content-type': 'application/json'}
client = requests.session()


def _get_json(filename):
    with open(filename, 'r') as f:
        l = f.readlines()
    json_str = ''.join(l)
    return json.loads(json_str)


def create(p1, p2, data_dict):
    url = '/'.join((args.server, p1, p2))
    res = client.post(url, data=json.dumps(data_dict), headers=headers, verify=False)
    uuid = res.json()['uuid']
    if not res.status_code == 201:
        raise 'Creation failed!'
    else:
        print('Creation successful (%s): %s' % (url, uuid))
    return uuid


### Create Klasser ###
data_dict = _get_json('create_klasse_fakultet.json')
uuid_klasse_fakultet = create('klassifikation', 'klasse', data_dict)

data_dict = _get_json('create_klasse_afdeling.json')
uuid_klasse_afdeling = create('klassifikation', 'klasse', data_dict)


### Create organisation ###
data_dict = _get_json('create_organisation_AU.json')
uuid_org_AU = create('organisation', 'organisation', data_dict)


### Create root OrgEnhed ###
data_dict = _get_json('create_organisationenhed_root.json')
data_dict['relationer']['tilhoerer'][0]['uuid'] = uuid_org_AU
data_dict['relationer']['enhedstype'][0]['uuid'] = uuid_klasse_afdeling
uuid_orgEnhed_root = create('organisation', 'organisationenhed', data_dict)


### Create two child OrgEnheder ###
data_dict = _get_json('create_organisationenhed_hum.json')
data_dict['relationer']['tilhoerer'][0]['uuid'] = uuid_org_AU
data_dict['relationer']['enhedstype'][0]['uuid'] = uuid_klasse_fakultet
data_dict['relationer']['overordnet'][0]['uuid'] = uuid_orgEnhed_root
uuid_orgEnhed_hum = create('organisation', 'organisationenhed', data_dict)


data_dict = _get_json('create_organisationenhed_samf.json')
data_dict['relationer']['tilhoerer'][0]['uuid'] = uuid_org_AU
data_dict['relationer']['enhedstype'][0]['uuid'] = uuid_klasse_fakultet
data_dict['relationer']['overordnet'][0]['uuid'] = uuid_orgEnhed_root
uuid_orgEnhed_samf = create('organisation', 'organisationenhed', data_dict)
