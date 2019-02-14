#!/usr/bin/env python3
#
# Copyright (c) 2017-2019, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Create a JSON fixture containing the specified URLs
'''

import json
import sys

import requests


def map_response(r):
    r.raise_for_status()
    return r.url, r.json()


if __name__ == '__main__':
    data = dict(map(map_response, map(requests.get, sys.argv[1:])))

    json.dump(data, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write('\n')
