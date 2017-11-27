#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os

from mora.converters import importing

from .. import util


class ImportTest(util.LoRATestCase):
    maxDiff = None

    def test_import(self):
        virkning_class = {
            'from': '-infinity',
            'from_included': False,
            'to': 'infinity',
            'to_included': False,
        }
        virkning_org = {
            'from': '2012-01-01T00:00:00+01:00',
            'from_included': True,
            'to': 'infinity',
            'to_included': False,
        }
        virkning_unit = {
            'from': '2016-01-01T00:00:00+01:00',
            'from_included': True,
            'to': 'infinity',
            'to_included': False,
        }

        expected = [
            (
                'PUT',
                '/organisation/organisation'
                '/59141156-ed0b-457c-9535-884447c5220b',
                {
                    'attributter': {
                        'organisationegenskaber': [
                            {
                                'brugervendtnoegle': 'Aarhus Kommune',
                                'organisationsnavn': 'Aarhus Kommune',
                                'virkning': virkning_org,
                            },
                        ],
                    },
                    'note': None,
                    'relationer': {
                        'myndighed': [
                            {
                                'urn': 'urn:dk:kommune:751',
                                'virkning': virkning_org,
                            },
                        ],
                        'myndighedstype': [
                            {
                                'urn': 'urn:oio:objekttype:Kommune',
                                'virkning': virkning_org,
                            },
                        ],
                        'virksomhed': [
                            {
                                'urn': 'urn:dk:cvr:55133018',
                                'virkning': virkning_org,
                            },
                        ],
                    },
                    'tilstande': {
                        'organisationgyldighed': [
                            {
                                'gyldighed': 'Aktiv',
                                'virkning': virkning_org,
                            },
                        ],
                    },
                },
            ),
            (
                'PUT',
                '/klassifikation/klasse/0034fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                {
                    'attributter': {
                        'klasseegenskaber': [
                            {
                                'beskrivelse': 'Dette er en afdeling',
                                'brugervendtnoegle': 'Afdeling003',
                                'titel': 'Afdeling 003',
                                'virkning': virkning_class,
                            },
                        ],
                    },
                    'tilstande': {
                        'klassepubliceret': [
                            {
                                'publiceret': 'Publiceret',
                                'virkning': virkning_class,
                            },
                        ],
                    },
                },
            ),
            (
                'PUT',
                '/klassifikation/klasse/9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                {
                    'attributter': {
                        'klasseegenskaber': [
                            {
                                'beskrivelse': 'Dette er en afdeling',
                                'brugervendtnoegle': 'Afdeling933',
                                'titel': 'Afdeling 933',
                                'virkning': virkning_class,
                            },
                        ],
                    },
                    'tilstande': {
                        'klassepubliceret': [
                            {
                                'publiceret': 'Publiceret',
                                'virkning': virkning_class,
                            },
                        ],
                    },
                },
            ),
            (
                'PUT',
                '/organisation/organisationenhed'
                '/0c388d43-a88a-42e0-9f37-4107cac08836',
                {
                    'attributter': {
                        'organisationenhedegenskaber': [
                            {
                                'brugervendtnoegle': 'HAVNEN',
                                'enhedsnavn': 'Aarhus Havn',
                                'virkning': virkning_unit,
                            },
                        ],
                    },
                    'note': None,
                    'relationer': {
                        'adresser': [
                            {
                                'gyldighed': 'Aktiv',
                                'urn': 'urn:magenta.dk:telefon:+4512345678',
                                'virkning': virkning_unit,
                            },
                            {
                                'gyldighed': 'Aktiv',
                                'uuid': 'afc933a9-2468-40a8-b1b7-919ccc18667b',
                                'virkning': virkning_unit,
                            },
                        ],
                        'enhedstype': [
                            {
                                'uuid': '9334fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                                'virkning': virkning_unit,
                            },
                        ],
                        'overordnet': [
                            {
                                'uuid': '85219a34-a9ca-4fc6-ad34-48019f5dfc44',
                                'virkning': virkning_unit,
                            },
                        ],
                        'tilhoerer': [
                            {
                                'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                                'virkning': virkning_unit,
                            },
                        ],
                        'tilknyttedeenheder': [
                            {
                                'urn': ('urn:kmd.dk:'
                                        'administrativenhedsid:70070'),
                                'virkning': virkning_unit,
                            },
                        ],
                    },
                    'tilstande': {
                        'organisationenhedgyldighed': [
                            {
                                'gyldighed': 'Aktiv',
                                'virkning': virkning_unit,
                            },
                        ],
                    },
                },
            ),
            (
                'PUT',
                '/organisation/organisationenhed'
                '/85219a34-a9ca-4fc6-ad34-48019f5dfc44',
                {
                    'attributter': {
                        'organisationenhedegenskaber': [
                            {
                                'brugervendtnoegle': 'ÅRHUS',
                                'enhedsnavn': 'Aarhus Kommune',
                                'virkning': virkning_unit,
                            },
                        ],
                    },
                    'note': None,
                    'relationer': {
                        'adresser': [
                            {
                                'gyldighed': 'Aktiv',
                                'urn': 'urn:magenta.dk:telefon:+4587654321',
                                'virkning': virkning_unit,
                            },
                            {
                                'gyldighed': 'Aktiv',
                                'uuid': '9b9a6a18-ffb7-4ece-a7f1-5368812e4719',
                                'virkning': virkning_unit,
                            },
                        ],
                        'enhedstype': [
                            {
                                'uuid': '0034fa1f-b1ef-4764-8505-c5b9ca43aaa9',
                                'virkning': virkning_unit,
                            },
                        ],
                        'overordnet': [
                            {
                                'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                                'virkning': virkning_unit,
                            },
                        ],
                        'tilhoerer': [
                            {
                                'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                                'virkning': virkning_unit,
                            },
                        ],
                        'tilknyttedeenheder': [
                            {
                                'urn': 'urn:kmd.dk:administrativenhedsid:325',
                                'virkning': virkning_unit,
                            },
                        ],
                    },
                    'tilstande': {
                        'organisationenhedgyldighed': [
                            {
                                'gyldighed': 'Aktiv',
                                'virkning': virkning_unit,
                            },
                        ],
                    },
                },
            ),
        ]

        p = os.path.join(util.BASE_DIR, 'sandbox', 'AAK',
                         'AARHUS_minified.xlsx')
        self.assertEqual(expected, list(importing.convert([p])))

class MockTests(util.TestCase):
    maxDiff = None

    @util.mock('importing.json')
    def test_load(self, m):
        expected = util.get_fixture('MAGENTA_01.json')

        self.assertEqual(expected, importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ]))

        self.assertEqual(expected, importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ], exact=True))

        self.assertEqual(expected, importing.load_data([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.xlsx'),
        ]))

    @util.mock()
    def test_convert(self, m):
        data = util.get_fixture('MAGENTA_01.json')

        # JSON converts tuples to lists - convert them back
        expected = list(map(tuple, util.get_fixture('MAGENTA_01-result.json')))

        with open('/tmp/x.json', 'w') as fp:
            import json
            json.dump(
                list(importing.convert([
                    os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
                ])),
                fp,
                indent=2, sort_keys=True,
            )

        self.assertEqual(sorted(expected), sorted(importing.convert([
            os.path.join(util.FIXTURE_DIR, 'MAGENTA_01.json'),
        ])))
