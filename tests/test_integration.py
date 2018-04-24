#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import uuid

import freezegun
import requests

from mora import lora
from mora import settings

from . import util


class IntegrationTests(util.LoRATestCase):
    maxDiff = None

    def test_sanity(self):
        r = requests.get(self.lora_url)
        self.assertTrue(r.ok)
        self.assertEqual(r.json().keys(), {'site-map'})

    def test_empty(self):
        r = requests.get(self.lora_url)
        self.assertTrue(r.ok)
        self.assertEqual(r.json().keys(), {'site-map'})

    def test_verify_relation_names(self):
        '''Verify that our list of relation names is correct.'''
        attrs = set()
        rels = set()

        def get(p):
            r = lora.session.get(settings.LORA_URL.rstrip('/') + p)
            r.raise_for_status()
            return r.json()

        for rule in get('/site-map')['site-map']:
            if rule.endswith('fields'):
                r = get(rule)

                attrs.update(r['attributter']['egenskaber'])
                rels.update(r['relationer_nul_til_en'])
                rels.update(r['relationer_nul_til_mange'])

        # I wish relation and attribute names were disjoint :(
        self.assertEqual(rels & attrs, {'interessefaellesskabstype'})

        rels -= {'interessefaellesskabstype'}

        self.assertEqual(rels, lora.ALL_RELATION_NAMES)
