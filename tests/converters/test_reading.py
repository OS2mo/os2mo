#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest
import copy

import freezegun

from mora.converters import meta
from mora import lora
from mora import util

from .. import util as test_util


class SimpleTests(unittest.TestCase):
    maxDiff = None

    def _apply_restrictions_for(self, value, validity=None):
        loraparams, func = lora._get_restrictions_for(validity=validity)

        with self.subTest('checking that effective date has the same effect '
                          'as running at that time'):
            with freezegun.freeze_time('2001-01-01 00:00:00', tz_offset=+1):
                old = lora._get_restrictions_for(validity=validity)
                oldtime = util.unparsedate(util.now().date())

            with freezegun.freeze_time('2011-01-01 00:00:00', tz_offset=+1):
                backdated = lora._get_restrictions_for(validity=validity,
                                                       effective_date=oldtime)

            self.assertEqual(old[0], backdated[0])
            self.assertEqual(old[1]([value]), backdated[1]([value]))

        return func([value])[0]

    @freezegun.freeze_time('2017-12-31 00:00:00', tz_offset=+1)
    @test_util.mock()
    def test_present_restrictions(self, m):
        obj = {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2017-01-01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    },
                ],
            },
        }

        self.assertEquals(obj, self._apply_restrictions_for(obj))
        self.assertEquals(obj, self._apply_restrictions_for(obj, 'present'))

    @freezegun.freeze_time('2017-12-31 00:00:00', tz_offset=+1)
    @test_util.mock()
    def test_past_restrictions(self, m):
        obj = {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2016-01-01",
                            "from_included": True,
                            "to": "2017-01-01",
                            "to_included": False,
                        },
                    },
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2017-01-01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    },
                ],
            },
        }

        # the second entry is current
        expected = copy.deepcopy(obj)
        expected["attributter"]["organisationenhedegenskaber"].pop(1)

        self.assertEquals(expected, self._apply_restrictions_for(obj, 'past'))

    @freezegun.freeze_time('2016-12-31 00:00:00', tz_offset=+1)
    @test_util.mock()
    def test_future_restrictions(self, m):
        obj = {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2016-01-01",
                            "from_included": True,
                            "to": "2017-01-01",
                            "to_included": False,
                        },
                    },
                    {
                        "brugervendtnoegle": "root",
                        "enhedsnavn": "Overordnet Enhed",
                        "virkning": {
                            "from": "2017-01-01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False,
                        },
                    },
                ],
            },
        }

        # the first entry is current
        expected = copy.deepcopy(obj)
        expected["attributter"]["organisationenhedegenskaber"].pop(0)

        actual = self._apply_restrictions_for(obj, 'future')

        self.assertEquals(expected, actual)

    def test_meta(self):
        self.assertEquals(meta.Address.fromstring('asdasdasd'),
                          meta.Address(name='asdasdasd', primary=False))

        self.assertEquals(meta.Address.fromstring(''),
                          meta.Address(name='', primary=False))

        with self.assertRaises(ValueError):
            meta.Address.fromstring('v1337:::::::')

        self.assertEquals(
            meta.PhoneNumber.fromstring(
                'v0:kaflaflibob:00000000-0000-0000-0000-000000000000',
            ),
            meta.PhoneNumber(
                location='00000000-0000-0000-0000-000000000000',
                visibility='kaflaflibob',
            ),
        )

        self.assertEquals(
            meta.PhoneNumber.fromstring(''),
            meta.PhoneNumber(location=None, visibility='internal'),
        )

        with self.assertRaises(ValueError):
            meta.PhoneNumber.fromstring('v1337:::::::')

        with self.assertRaises(ValueError):
            meta.PhoneNumber.fromstring('asdasdasd')


class LoRATest(test_util.TestCase):
    @freezegun.freeze_time('2017-07-28')
    @test_util.mock('role-type-contact-channel.json')
    def test_role_type_contact(self, mock):
        self.assertRequestResponse(
            '/o/59141156-ed0b-457c-9535-884447c5220b'
            '/org-unit/4b8fa170-d30e-43ff-aff3-b9792acfaa7d'
            '/role-types/contact-channel/',
            [
                {
                    "contact-info": "29208081",
                    "location": {
                        "name": "—",
                    },
                    "type": {
                        "name": "Telefonnummer",
                        "prefix": "urn:magenta.dk:telefon:",
                        "user-key": "Telephone_number",
                    },
                    "visibility": {
                        'name': 'Må vises internt',
                        'user-key': 'internal',
                        'uuid': 'ab68b2c2-8ffb-4292-a938-60e3afe0cad0',
                    },
                    "valid-from": "28-07-2017",
                    "valid-to": "infinity"
                }
            ],
        )

    @freezegun.freeze_time('2017-07-28')
    @test_util.mock('reading-organisation.json')
    def test_organisation(self, mock):
        self.assertRequestResponse(
            '/o/',
            [
                {
                    'hierarchy': {
                        'children': [],
                        'hasChildren': True,
                        'name': 'Overordnet Enhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'user-key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                    },
                    'name': 'Aarhus Universitet',
                    'user-key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
            ],
        )

    @freezegun.freeze_time('2017-07-28')
    @test_util.mock('reading-organisation-rootless.json')
    def test_organisation_without_root(self, mock):
        self.assertRequestResponse('/o/', [])

    @freezegun.freeze_time('2017-07-28')
    @test_util.mock('reading-organisation-multiple-roots.json')
    def test_organisation_multiple_roots(self, mock):
        self.assertRequestResponse('/o/', [])

    @freezegun.freeze_time('2017-07-28')
    @test_util.mock('reading-organisation-combined.json')
    def test_organisation_combined(self, mock):
        self.assertRequestResponse(
            '/o/',
            [
                {
                    'hierarchy': {
                        'children': [],
                        'hasChildren': True,
                        'name': 'Overordnet Enhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'user-key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                    },
                    'name': 'Aarhus Universitet',
                    'user-key': 'AU',
                    'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
            ],
        )
