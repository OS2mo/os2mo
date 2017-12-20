#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import unittest

import freezegun

from mora import lora
from mora import settings
from mora import util as mora_util
from mora.converters import meta

from .. import util as test_util


class SimpleTests(unittest.TestCase):
    maxDiff = None

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

    @test_util.mock()
    @freezegun.freeze_time('2001-01-01', tz_offset=1)
    def test_get_effects(self, m):
        URL = (
            settings.LORA_URL + 'organisation/organisationenhed?'
            'uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=2001-01-02T00%3A00%3A00%2B01%3A00'
            '&virkningtil=infinity'
        )
        m.get(
            URL,
            complete_qs=True,
            json={
                "results":
                [[{
                    "id": "00000000-0000-0000-0000-000000000000",
                    "registreringer": [{
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": v,
                                    "virkning": {
                                        "from": mora_util.to_lora_time(
                                            t1,
                                        ),
                                        "from_included": True,
                                        "to": mora_util.to_lora_time(
                                            t2,
                                        ),
                                        "to_included": False
                                    }
                                }
                                for t1, t2, v in [
                                    ('01-01-1900', '01-01-2100', 'Aktiv'),
                                    ('01-01-2100', '01-01-2300', 'Inaktiv'),
                                    ('01-01-2300', '01-01-2500', 'Aktiv'),
                                    ('01-01-2500', '01-01-2700', 'Inaktiv'),
                                    ('01-01-2700', '01-01-2900', 'Aktiv'),
                                    ('01-01-2900', '01-01-3100', 'Inaktiv'),
                                    ('01-01-3100', '01-01-3300', 'Aktiv'),
                                ]
                            ]
                        },
                    }]
                }]]
            },
        )

        c = lora.Connector(validity='future')

        self.assertEquals(
            [
                (
                    "2100-01-01 00:00:00+01:00",
                    "2300-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2100-01-01T00:00:00+01:00",
                                        "to": "2300-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2300-01-01 00:00:00+01:00",
                    "2500-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2300-01-01T00:00:00+01:00",
                                        "to": "2500-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2500-01-01 00:00:00+01:00",
                    "2700-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2500-01-01T00:00:00+01:00",
                                        "to": "2700-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2700-01-01 00:00:00+01:00",
                    "2900-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2700-01-01T00:00:00+01:00",
                                        "to": "2900-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "2900-01-01 00:00:00+01:00",
                    "3100-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Inaktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "2900-01-01T00:00:00+01:00",
                                        "to": "3100-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                ),
                (
                    "3100-01-01 00:00:00+01:00",
                    "3300-01-01 00:00:00+01:00",
                    {
                        "tilstande": {
                            "organisationenhedgyldighed": [
                                {
                                    "gyldighed": "Aktiv",
                                    "virkning": {
                                        "from_included": True,
                                        "to_included": False,
                                        "from": "3100-01-01T00:00:00+01:00",
                                        "to": "3300-01-01T00:00:00+01:00"
                                    }
                                }
                            ]
                        }
                    }
                )
            ],
            [
                (str(start), str(end), entry)
                for start, end, entry in
                c.organisationenhed.get_effects(
                    '00000000-0000-0000-0000-000000000000',
                    relevant={
                        'tilstande': (
                            'organisationenhedgyldighed',
                        ),
                    },
                )
            ],
        )


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
                    "name": "Telefonnummer",
                    "phone-type": {
                        "name": "Telefonnummer",
                        "prefix": "urn:magenta.dk:telefon:",
                        "user-key": "Telephone_number",
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


@freezegun.freeze_time('2017-06-01')
class TemporalTests(test_util.TestCase):
    @test_util.mock('reading_orgunit.json')
    def test_orgunit_past(self, mock):
        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
            '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
            '/?validity=past',
            [
                {
                    'activeName': 'Afdeling for Fremtidshistorik',
                    'name': 'Afdeling for Fremtidshistorik',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                    'parent-object': {
                        'activeName': 'Historisk Institut',
                        'name': 'Historisk Institut',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                        'parent-object': None,
                        'type': {
                            'name': 'Institut',
                            'user-key': 'inst',
                            'userKey': 'inst',
                            'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                        },
                        'user-key': 'hist',
                        'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                        'valid-from': '01-01-2016',
                        'valid-to': '01-01-2019',
                    },
                    'type': {
                        'name': 'Afdeling',
                        'user-key': 'afd',
                        'userKey': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'user-key': 'frem',
                    'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                    'valid-from': '01-01-2016',
                    'valid-to': '01-01-2017',
                },
            ],
        )

    @test_util.mock('reading_orgunit.json')
    def test_orgunit_present(self, mock):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/?validity=present',
                [
                    {
                        'activeName': 'Afdeling for Samtidshistorik',
                        'name': 'Afdeling for Samtidshistorik',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                        'parent-object': {
                            'activeName': 'Historisk Institut',
                            'name': 'Historisk Institut',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'parent-object': None,
                            'type': {
                                'name': 'Institut',
                                'user-key': 'inst',
                                'userKey': 'inst',
                                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                            },
                            'user-key': 'hist',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'valid-from': '01-01-2016',
                            'valid-to': '01-01-2019',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'valid-from': '01-01-2017',
                        'valid-to': '01-01-2018',
                    },
                ]
            )

    @test_util.mock('reading_orgunit.json')
    def test_orgunit_future(self, mock):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/?validity=future',
                [
                    {
                        'activeName': 'Afdeling for Fortidshistorik',
                        'name': 'Afdeling for Fortidshistorik',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                        'parent-object': {
                            'activeName': 'Historisk Institut',
                            'name': 'Historisk Institut',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'parent-object': None,
                            'type': {
                                'name': 'Institut',
                                'user-key': 'inst',
                                'userKey': 'inst',
                                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                            },
                            'user-key': 'hist',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'valid-from': '01-01-2016',
                            'valid-to': '01-01-2019',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'user-key': 'afd',
                            'userKey': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'valid-from': '01-01-2018',
                        'valid-to': '01-01-2019',
                    },
                ]
            )

    @test_util.mock('reading_orgunit.json')
    def test_location_past(self, mock):
        with self.subTest('location'):
            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/role-types/location'
                '/?validity=past',
                404,
            )

            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/role-types/location'
                '/?validity=past',
                404,
            )

    @test_util.mock('reading_orgunit.json')
    def test_location_present(self, mock):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/role-types/location'
                '/?validity=present',
                [
                    {
                        'location': {
                            'name': 'Kontor',
                            'user-key': '07515902___1_______',
                            'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                            'valid-from': '2014-05-05T19:07:48.577000+00:00',
                            'valid-to': 'infinity',
                            'vejnavn': 'Nordre Ringgade 1, 8000 Aarhus C',
                        },
                        'name': 'Kontor',
                        'org-unit': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'primaer': True,
                        'role-type': 'location',
                        'user-key': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'valid-from': '01-01-2016',
                        'valid-to': '01-01-2019',
                    },
                ],
            )

            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/role-types/location'
                '/?validity=present',
                [
                    {
                        "location": {
                            "name": "Kontor",
                            "user-key": "07515902___1_______",
                            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                            "valid-from": "2014-05-05T19:07:48.577000+00:00",
                            "valid-to": "infinity",
                            "vejnavn": "Nordre Ringgade 1, 8000 Aarhus C"
                        },
                        "name": "Kontor",
                        "org-unit": "da77153e-30f3-4dc2-a611-ee912a28d8aa",
                        "primaer": True,
                        "role-type": "location",
                        "user-key": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                        "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                        "valid-from": "01-01-2016",
                        "valid-to": "01-01-2019"
                    }
                ],
            )

    @test_util.mock('reading_orgunit.json')
    def test_location_future(self, mock):
            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/role-types/location'
                '/?validity=future',
                404,
            )

            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/role-types/location'
                '/?validity=future',
                404,
            )

    @test_util.mock('reading_orgunit.json')
    def test_contact_channel_past(self, mock):
            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/role-types/contact-channel'
                '/?validity=past',
                404,
            )

            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/role-types/contact-channel'
                '/?validity=past',
                404,
            )

    @test_util.mock('reading_orgunit.json')
    def test_contact_channel_present(self, mock):
            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/role-types/contact-channel'
                '/?validity=present',
                404,
            )

            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/role-types/contact-channel'
                '/?validity=present',
                [
                    {
                        "contact-info": "+4587150000",
                        "location": {
                            "name": "Nordre Ringgade 1, 8000 Aarhus C",
                            "user-key": "07515902___1_______",
                            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                            "valid-from": "2014-05-05T19:07:48.577000+00:00",
                            "valid-to": "infinity",
                            "vejnavn": "Nordre Ringgade 1, 8000 Aarhus C"
                        },
                        "name": "Telefonnummer",
                        "phone-type": {
                            "name": "Telefonnummer",
                            "prefix": "urn:magenta.dk:telefon:",
                            "user-key": "Telephone_number",
                        },
                        "type": {
                            "name": "Telefonnummer",
                            "prefix": "urn:magenta.dk:telefon:",
                            "user-key": "Telephone_number"
                        },
                        "valid-from": "01-01-2016",
                        "valid-to": "01-01-2019",
                        "visibility": {
                            "name": "M\u00e5 vises eksternt",
                            "user-key": "external",
                            "uuid": "c67d7315-a0a2-4238-a883-f33aa7ddabc2"
                        }
                    }
                ],
            )

    @test_util.mock('reading_orgunit.json')
    def test_contact_channel_future(self, mock):
            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/04c78fc2-72d2-4d02-b55f-807af19eac48'
                '/role-types/contact-channel'
                '/?validity=future',
                404,
            )

            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/da77153e-30f3-4dc2-a611-ee912a28d8aa'
                '/role-types/contact-channel'
                '/?validity=future',
                404,
            )
