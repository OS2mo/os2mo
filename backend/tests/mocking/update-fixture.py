#!/usr/bin/env python3
#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Update, i.e. re-fetch, a JSON fixture
'''

import operator
import os
import json
import sys

import requests


def update(p):
    sess = requests.Session()

    with open(p) as fp:
        d = json.load(fp)

    def get(url):
        print(url, file=sys.stderr)
        r = sess.get(url)
        r.raise_for_status()

        return r.json()

    with open(p + '~', 'w') as fp:
        json.dump(
            dict(zip(d, map(get, d))),
            fp,
            indent=2,
            sort_keys=True,
        )

        # ensure trailing newline
        fp.write('\n')

    os.rename(fp.name, p)


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        update(arg)
