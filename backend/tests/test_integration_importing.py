#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import copy
import pprint
import unittest

import freezegun

from mora.service import facet

from . import util


class IntegrationTests(util.LoRATestCase):
    maxDiff = None

    @unittest.skip('test is unstable?!')
    @freezegun.freeze_time('2018-06-01')
    def test_service_with_ballerup(self):
        with util.mock('dawa-ballerup.json', allow_mox=True):
            util.import_fixture('BALLERUP.csv')

        with self.subTest('all facets'):
            self.assertRequestResponse(
                '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/',
                [{'name': 'address_type',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                  '/f/address_type/',
                  'user_key': 'Adressetype',
                  'uuid': '0b4a9cae-5e01-4694-ae92-a1c07d5f2ab2'},
                 {'name': 'association_type',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                  '/f/association_type/',
                  'user_key': 'Tilknytningstype',
                  'uuid': '81b80fa7-b71b-4d33-b528-cae038208758'},
                 {'name': 'engagement_type',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                  '/f/engagement_type/',
                  'user_key': 'Engagementstype',
                  'uuid': 'e041bae1-d830-4072-890c-9fa5b95cf26a'},
                 {'name': 'job_function',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                  '/f/job_function/',
                  'user_key': 'Stillingsbetegnelse',
                  'uuid': '51774dde-bf2c-4100-9059-70d1a1fb1d1f'},
                 {'name': 'leave_type',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                          '/f/leave_type/',
                  'user_key': 'Orlovstype',
                  'uuid': 'd9aa489a-ac93-4769-98e5-19d6d37a919c'},
                 {'name': 'manager_level',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                          '/f/manager_level/',
                  'user_key': 'Lederniveau',
                  'uuid': '5e1186f2-3b41-428e-97c1-ebd680b12488'},
                 {'name': 'manager_type',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                          '/f/manager_type/',
                  'user_key': 'Ledertyper',
                  'uuid': '7f63f302-5277-4ab6-b9d8-073b4a7ffc51'},
                 {'name': 'org_unit_type',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                          '/f/org_unit_type/',
                  'user_key': 'Enhedstype',
                  'uuid': 'd2a8b57a-5913-47c9-8ead-99b9822e27fa'},
                 {'name': 'responsibility',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                          '/f/responsibility/',
                  'user_key': 'Lederansvar',
                  'uuid': '035f1fc2-0d61-47ec-994b-a75a727de8c3'},
                 {'name': 'role_type',
                  'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd'
                          '/f/role_type/',
                  'user_key': 'Rolletype',
                  'uuid': '09c93426-db19-4442-aea8-5ac9ba9573a6'},
                 ],
            )

        with self.subTest('all classes'):
            def get(f):
                r = self.client.get(f['path'])

                if r.status_code != 200:
                    v = (r.status, r.get_data(as_text=True))
                else:
                    v = r.json

                return (f['name'], v)

            all_types = dict(
                map(
                    get,
                    self.client.get(
                        '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/',
                    ).json,
                ),
            )

            pprint.pprint(all_types)

            self.assertEqual(
                sorted(facet.FACETS),
                sorted(all_types),
                'the BALLERUP spreadsheet should include all supported facets',
            )

            def sort_classes(obj):
                obj_copy = copy.deepcopy(obj)
                for v in obj_copy.values():
                    v['data']['items'] = sorted(
                        v['data']['items'], key=lambda x: x['user_key'])
                return obj_copy

            self.assertEqual(
                {
                    'address_type': {
                        'data': {
                            'items': [{
                                'example': '<UUID>',
                                'name': 'Lokation',
                                'scope': 'DAR',
                                'user_key': 'AdresseLokation',
                                'uuid': '031f93c3-6bab-462e-a998-87cad6db3128'
                            },
                                {'example': None,
                                 'name': 'Faxnummer',
                                 'scope': 'PHONE',
                                 'user_key': 'Fax',
                                 'uuid': '26d0da83-f43f-4feb-a7b1-d7c28d56daae'
                                 },
                                {
                                    'example': 'Postboks 29, 4260 Korsbæk',
                                    'name': 'Returadresse',
                                    'scope': 'DAR',
                                    'user_key': 'AdressePostRetur',
                                    'uuid': '2c4d87bd-ad26-4580-'
                                            '982f-7ea90c4512d3'},
                                {'example': '1003259972',
                                 'name': 'P-nummer',
                                 'scope': 'PNUMBER',
                                 'user_key': 'P-nummer',
                                 'uuid': '5988664a-817e-4dea-91d5-3354ec37f27a'
                                 },
                                {
                                    'example': 'hpe@korsbaek.dk',
                                    'name': 'Emailadresse',
                                    'scope': 'EMAIL',
                                    'user_key': 'Email',
                                    'uuid': '80764a2f-6a7b-492c-'
                                            '92d9-96d24ac845ea'},
                                {
                                    'example': '5790001969370',
                                    'name': 'EAN',
                                    'scope': 'EAN',
                                    'user_key': 'EAN',
                                    'uuid': 'a88aa93b-8edc-46ab-'
                                            'bad7-6535f9b765e5'},
                                {'example': '<UUID>',
                                 'name': 'Postadresse',
                                 'scope': 'DAR',
                                 'user_key': 'AdressePost',
                                 'uuid': 'a8c8fe66-2ab1-46ed-ba99-ed05e855d65f'
                                 },
                                {
                                    'example': '+45 3334 9400',
                                    'name': 'Telefonnummer',
                                    'scope': 'PHONE',
                                    'user_key': 'Telefon',
                                    'uuid': 'eb520fe5-eb72-4110-'
                                            'b81d-9c1a129dc22a'},
                                {'example': '<UUID>',
                                 'name': 'Henvendelsessted',
                                 'scope': 'DAR',
                                 'user_key': 'AdresseHenvendelsesSted',
                                 'uuid': 'ff4ed3b4-18fc-42cf-af12-51ac7b9a069a'
                                 }],
                            'offset': 0,
                            'total': 9},
                        'name': 'address_type',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/address_type/',
                        'user_key': 'Adressetype',
                        'uuid': '0b4a9cae-5e01-4694-ae92-a1c07d5f2ab2'},
                    'association_type': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Ansat',
                                'scope': None,
                                'user_key': 'Ansat',
                                'uuid': '39dd14ed-faa9-40bf-9fc9-13c440078458'
                            }],
                            'offset': 0,
                            'total': 1},
                        'name': 'association_type',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/association_type/',
                        'user_key': 'Tilknytningstype',
                        'uuid': '81b80fa7-b71b-4d33-b528-cae038208758'},
                    'engagement_type': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Ansat',
                                'scope': None,
                                'user_key': 'Ansat',
                                'uuid': '351fdf06-102a-4159-a5b4-69922b0ccde9'
                            },
                                {'example': None,
                                 'name': 'Frivillig',
                                 'scope': None,
                                 'user_key': 'Frivillig',
                                 'uuid': 'cb58a4e8-3795-4c01-9729-0c6efd274027'
                                 },
                                {'example': None,
                                 'name': 'Folkevalgt',
                                 'scope': None,
                                 'user_key': 'Folkevalgt',
                                 'uuid': 'd771715e-d0ad-48db-b12e-563ec9212df7'
                                 }],
                            'offset': 0,
                            'total': 3},
                        'name': 'engagement_type',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/engagement_type/',
                        'user_key': 'Engagementstype',
                        'uuid': 'e041bae1-d830-4072-890c-9fa5b95cf26a'},
                    'job_function': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Afdelingschef',
                                'scope': None,
                                'user_key': 'Afdelingschef',
                                'uuid': 'cc9e7333-5031-45f2-b123-d83cbda4b9d5'
                            },
                                {'example': None,
                                 'name': 'Administrativ leder',
                                 'scope': None,
                                 'user_key': 'Administrativ leder',
                                 'uuid': 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee'
                                 },
                                {'example': None,
                                 'name': '… (≈400 flere)',
                                 'scope': None,
                                 'user_key': '… (≈400 flere)',
                                 'uuid': 'f5b8f156-fa4e-46e2-b9e6-51a953166273'
                                 },
                                {'example': None,
                                 'name': 'Afdelingssygeplejerske',
                                 'scope': None,
                                 'user_key': 'Afdelingssygeplejerske',
                                 'uuid': 'fdfa8984-1b78-4014-8c35-f2a59b758bcb'
                                 }],
                            'offset': 0,
                            'total': 4},
                        'name': 'job_function',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/job_function/',
                        'user_key': 'Stillingsbetegnelse',
                        'uuid': '51774dde-bf2c-4100-9059-70d1a1fb1d1f'},
                    'leave_type': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Barselsorlov',
                                'scope': None,
                                'user_key': 'Barselsorlov',
                                'uuid': 'd7ec3a18-3a9d-43c8-ad03-0202c0d044d4'
                            }],
                            'offset': 0,
                            'total': 1},
                        'name': 'leave_type',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/leave_type/',
                        'user_key': 'Orlovstype',
                        'uuid': 'd9aa489a-ac93-4769-98e5-19d6d37a919c'},
                    'manager_level': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Niveau 90',
                                'scope': None,
                                'user_key': 'Niveau 90',
                                'uuid': '7d4d2609-7146-4a20-b9f0-fe4c19701217'
                            }],
                            'offset': 0,
                            'total': 1},
                        'name': 'manager_level',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/manager_level/',
                        'user_key': 'Lederniveau',
                        'uuid': '5e1186f2-3b41-428e-97c1-ebd680b12488'},
                    'manager_type': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Kommunaldirektør',
                                'scope': None,
                                'user_key': 'Kommunaldirektør',
                                'uuid': '08cedf73-852b-4a51-9e8e-d026d83c4915'
                            },
                                {'example': None,
                                 'name': 'Stedfortræder',
                                 'scope': None,
                                 'user_key': 'Stedfortræder',
                                 'uuid': '0b7e086c-7364-4337-8426-a97545249725'
                                 },
                                {'example': None,
                                 'name': 'Systemadministrator',
                                 'scope': None,
                                 'user_key': 'Systemadministrator',
                                 'uuid': '1bc1d585-e0e8-43ac-b7d1-a1519e0b48e5'
                                 },
                                {'example': None,
                                 'name': 'Sekretariatschef',
                                 'scope': None,
                                 'user_key': 'Sekretariatschef',
                                 'uuid': '21f7d83f-5e80-4f16-9a44-8eb2a96014a2'
                                 },
                                {'example': None,
                                 'name': 'Institutionsunderafsnitsleder',
                                 'scope': None,
                                 'user_key': 'Institutionsunderafsnitsleder',
                                 'uuid': '38639c7f-0f90-441b-9bc7-cb8681aa4f55'
                                 },
                                {'example': None,
                                 'name': 'Institutionsafsnitsleder',
                                 'scope': None,
                                 'user_key': 'Institutionsafsnitsleder',
                                 'uuid': '42617c67-b516-4b41-be6f-0cb43bb455f9'
                                 },
                                {'example': None,
                                 'name': 'Afsnitsleder',
                                 'scope': None,
                                 'user_key': 'Afsnitsleder',
                                 'uuid': '48f525f5-4420-49a0-9e95-096e26cfdc9f'
                                 },
                                {'example': None,
                                 'name': 'Teamleder',
                                 'scope': None,
                                 'user_key': 'Teamleder',
                                 'uuid': '58b4060b-b6b9-409a-81aa-9d390af71f61'
                                 },
                                {'example': None,
                                 'name': 'Beredskabschef',
                                 'scope': None,
                                 'user_key': 'Beredskabschef',
                                 'uuid': '6a1e28d1-5c15-439b-bfcd-34de284a8c80'
                                 },
                                {'example': None,
                                 'name': 'Borgmester',
                                 'scope': None,
                                 'user_key': 'Borgmester',
                                 'uuid': '6a6d5c82-a7d1-4488-b687-49daa3910ec1'
                                 },
                                {'example': None,
                                 'name': 'Institutionsleder',
                                 'scope': None,
                                 'user_key': 'Institutionsleder',
                                 'uuid': 'a0a4db8c-a2cd-4e43-baae-288f2b0ed89d'
                                 },
                                {'example': None,
                                 'name': 'Direktør',
                                 'scope': None,
                                 'user_key': 'Direktør',
                                 'uuid': 'd8043094-6f38-4349-9fbb-dc7c28668fa0'
                                 },
                                {'example': None,
                                 'name': 'Chef',
                                 'scope': None,
                                 'user_key': 'Chef',
                                 'uuid': 'ff13e6d0-d43b-4b39-8cd4-742a0365d6c2'
                                 }],
                            'offset': 0,
                            'total': 13},
                        'name': 'manager_type',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/manager_type/',
                        'user_key': 'Ledertyper',
                        'uuid': '7f63f302-5277-4ab6-b9d8-073b4a7ffc51'},
                    'org_unit_type': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Institutionsafsnit',
                                'scope': None,
                                'user_key': 'Institutionsafsnit',
                                'uuid': '04c310a3-42a0-437b-a27c-f9ba41b65e55'
                            },
                                {'example': None,
                                 'name': 'Ledelsessekretariat',
                                 'scope': None,
                                 'user_key': 'Ledelsessekretariat',
                                 'uuid': '18d124f1-19c8-4401-a8ed-cdb5e90accf2'
                                 },
                                {'example': None,
                                 'name': 'Institutionsunderafsnit',
                                 'scope': None,
                                 'user_key': 'Institutionsunderafsnit',
                                 'uuid': '1de0c88a-dca9-4c90-931b-c60c1a0efab4'
                                 },
                                {'example': None,
                                 'name': 'Konsulentfunktion',
                                 'scope': None,
                                 'user_key': 'Konsulentfunktion',
                                 'uuid': '225342e1-7ad3-463c-9aa0-1b0341e9e316'
                                 },
                                {'example': None,
                                 'name': 'Direktørområde',
                                 'scope': None,
                                 'user_key': 'Direktørområde',
                                 'uuid': '26d94be8-e164-4405-b2b3-a73807703b94'
                                 },
                                {'example': None,
                                 'name': 'Afsnit',
                                 'scope': None,
                                 'user_key': 'Afsnit',
                                 'uuid': '3498dd38-5cb5-4c19-a43d-c63ecaefacaf'
                                 },
                                {'example': None,
                                 'name': 'Institution',
                                 'scope': None,
                                 'user_key': 'Institution',
                                 'uuid': '547e6946-abdb-4dc2-ad99-b6042e05a7e4'
                                 },
                                {'example': None,
                                 'name': 'Team',
                                 'scope': None,
                                 'user_key': 'Team',
                                 'uuid': '56cfc7f4-2e54-45e2-af27-90591fb7c664'
                                 },
                                {'example': None,
                                 'name': 'Fagligt Center',
                                 'scope': None,
                                 'user_key': 'Fagligt Center',
                                 'uuid': '59f10075-88f6-4758-bf61-454858170776'
                                 },
                                {'example': None,
                                 'name': 'Andre',
                                 'scope': None,
                                 'user_key': 'Andre',
                                 'uuid': '72e01813-495b-47f7-a71c-4e41dfe82813'
                                 },
                                {'example': None,
                                 'name': 'Supportcenter',
                                 'scope': None,
                                 'user_key': 'Supportcenter',
                                 'uuid': '7c0f22a0-e942-4333-ab69-d716de2ff8ee'
                                 },
                                {'example': None,
                                 'name': 'Kommune',
                                 'scope': None,
                                 'user_key': 'Kommune',
                                 'uuid': 'f2f93f92-d08f-4b76-904f-af9144e23195'
                                 }],
                            'offset': 0,
                            'total': 12},
                        'name': 'org_unit_type',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/org_unit_type/',
                        'user_key': 'Enhedstype',
                        'uuid': 'd2a8b57a-5913-47c9-8ead-99b9822e27fa'},
                    'responsibility': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Beredskabsledelse',
                                'scope': None,
                                'user_key': 'Beredskabsledelse',
                                'uuid': '149a6f1e-3bda-40f8-a5a2-545fb3c12c8f'
                            },
                                {'example': None,
                                 'name': 'IT ledelse',
                                 'scope': None,
                                 'user_key': 'IT ledelse',
                                 'uuid': '1b2f87ac-44ad-402b-8083-e5a399d6e5fb'
                                 },
                                {'example': None,
                                 'name': 'Personale: Sygefravær',
                                 'scope': None,
                                 'user_key': 'Personale: Sygefravær',
                                 'uuid': '29df9de4-b624-4abc-8946-33d39bf1c5ac'
                                 },
                                {'example': None,
                                 'name': 'Ansvar for bygninger og '
                                         'arealer',
                                 'scope': None,
                                 'user_key': 'Ansvar for bygninger og '
                                             'arealer',
                                 'uuid': '31388038-b979-47c8-be08-42d8846661af'
                                 },
                                {'example': None,
                                 'name': 'Personale: Øvrige '
                                         'administrative opgaver',
                                 'scope': None,
                                 'user_key': 'Personale: Øvrige '
                                             'administrative opgaver',
                                 'uuid': '3aefba7a-026f-478c-8cef-48ab176c3c53'
                                 },
                                {'example': None,
                                 'name': 'Økonomi: Overordnet',
                                 'scope': None,
                                 'user_key': 'Økonomi: Overordnet',
                                 'uuid': '4ce843b3-8897-4558-8b9c-5765b4813151'
                                 },
                                {'example': None,
                                 'name': 'Faglig ledelse',
                                 'scope': None,
                                 'user_key': 'Faglig ledelse',
                                 'uuid': '4f1ae448-dfac-4287-99a1-87cc5b4ee9b3'
                                 },
                                {'example': None,
                                 'name': 'Personale: '
                                         'Ansættelse/afskedigelse',
                                 'scope': None,
                                 'user_key': 'Personale: '
                                             'Ansættelse/afskedigelse',
                                 'uuid': '7b587287-af54-421f-b6b2-f1bcd1f1d178'
                                 },
                                {'example': None,
                                 'name': 'Økonomi: Løbende kontering',
                                 'scope': None,
                                 'user_key': 'Økonomi: Løbende '
                                             'kontering',
                                 'uuid': 'a295b388-7d65-4a2b-82eb-2a401a51baeb'
                                 },
                                {'example': None,
                                 'name': 'Personale: MUS kompetence',
                                 'scope': None,
                                 'user_key': 'Personale: MUS kompetence',
                                 'uuid': 'fd438fda-7f94-488a-8345-b05b68b6eac6'
                                 }
                            ],
                            'offset': 0,
                            'total': 10},
                        'name': 'responsibility',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/responsibility/',
                        'user_key': 'Lederansvar',
                        'uuid': '035f1fc2-0d61-47ec-994b-a75a727de8c3'},
                    'role_type': {
                        'data': {
                            'items': [{
                                'example': None,
                                'name': 'Tillidsmand',
                                'scope': None,
                                'user_key': 'Tillidsmand',
                                'uuid': '0838d00d-e2b3-4aa8-a5a5-649c2205ab21'}
                            ],
                            'offset': 0,
                            'total': 1},
                        'name': 'role_type',
                        'path': '/service/o/3a87187c-f25a-40a1-'
                                '8d42-312b2e2b43bd/f/role_type/',
                        'user_key': 'Rolletype',
                        'uuid': '09c93426-db19-4442-aea8-5ac9ba9573a6'}},
                all_types)

        self.assertRequestResponse(
            '/service/o/',
            [{'name': 'Ballerup Kommune',
              'user_key': 'Ballerup Kommune',
              'uuid': '3a87187c-f25a-40a1-8d42-312b2e2b43bd'}],
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/children',
            [{
                'child_count': 3,
                'name': 'Ballerup Kommune',
                'user_key': 'BALLERUP',
                'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                'validity': {
                    'from': '1964-05-24',
                    'to': None,
                },
            }],
        )

        self.assertRequestResponse(
            '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4/children',
            [{'child_count': 0,
              'name': 'Ballerup Bibliotek',
              'user_key': 'BIBLIOTEK',
              'uuid': '921e44d3-2ec0-4c16-9935-2ec7976566dc',
              'validity': {'from': '1993-01-01', 'to': None}},
             {'child_count': 0,
              'name': 'Ballerup Familiehus',
              'user_key': 'FAMILIEHUS',
              'uuid': 'c12393e9-ee1d-4b91-a6a9-a17508c055c9',
              'validity': {'from': '2006-01-01', 'to': None}},
             {'child_count': 0,
              'name': 'Ballerup Idrætspark',
              'user_key': 'IDRÆTSPARK',
              'uuid': 'ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc',
              'validity': {'from': '1993-01-01', 'to': None}}],
        )

        for childid in (
            "921e44d3-2ec0-4c16-9935-2ec7976566dc",
            "c12393e9-ee1d-4b91-a6a9-a17508c055c9",
            "ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc",
        ):
            self.assertRequestResponse(
                '/service/ou/{}/children'.format(childid),
                [],
            )

        self.assertRequestResponse(
            '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4/',
            {
                'name': 'Ballerup Kommune',
                'user_key': 'BALLERUP',
                'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                'org': {
                    'name': 'Ballerup Kommune',
                    'user_key': 'Ballerup Kommune',
                    'uuid': '3a87187c-f25a-40a1-8d42-312b2e2b43bd',
                },
                'org_unit_type': {
                    'example': None,
                    'name': 'Kommune',
                    'scope': None,
                    'user_key': 'Kommune',
                    'uuid': 'f2f93f92-d08f-4b76-904f-af9144e23195',
                },
                'parent': None,
                'validity': {
                    'from': '1964-05-24',
                    'to': None,
                },
            },
        )

        self.assertRequestResponse(
            '/service/ou/c12393e9-ee1d-4b91-a6a9-a17508c055c9/',
            {
                'name': 'Ballerup Familiehus',
                'org': {'name': 'Ballerup Kommune',
                        'user_key': 'Ballerup Kommune',
                        'uuid': '3a87187c-f25a-40a1-8d42-312b2e2b43bd'},
                'org_unit_type': {
                    'example': None,
                    'name': 'Fagligt Center',
                    'scope': None,
                    'user_key': 'Fagligt Center',
                    'uuid': '59f10075-88f6-4758-bf61-454858170776',
                },
                'parent': {
                    'name': 'Ballerup Kommune',
                    'user_key': 'BALLERUP',
                    'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                    'validity': {
                        'from': '1964-05-24',
                        'to': None,
                    },
                },
                'user_key': 'FAMILIEHUS',
                'uuid': 'c12393e9-ee1d-4b91-a6a9-a17508c055c9',
                'validity': {'from': '2006-01-01', 'to': None},
            },
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/ou/',
            {'items': [
                {'name': 'Ballerup Bibliotek',
                 'user_key': 'BIBLIOTEK',
                 'uuid': '921e44d3-2ec0-4c16-9935-2ec7976566dc',
                 'validity': {'from': '1993-01-01',
                              'to': None}},
                {'name': 'Ballerup Kommune',
                 'user_key': 'BALLERUP',
                 'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                 'validity': {'from': '1964-05-24',
                              'to': None}},
                {'name': 'Ballerup Familiehus',
                 'user_key': 'FAMILIEHUS',
                 'uuid': 'c12393e9-ee1d-4b91-a6a9-a17508c055c9',
                 'validity': {'from': '2006-01-01',
                              'to': None}},
                {'name': 'Ballerup Idrætspark',
                 'user_key': 'IDRÆTSPARK',
                 'uuid': 'ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc',
                 'validity': {'from': '1993-01-01',
                              'to': None}}],
             'offset': 0,
             'total': 4},
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/e/',
            {'items': [{'name': 'Sanne Schäff',
                        'uuid': '1ce40e25-6238-4202-9e93-526b348ec745'},
                       {'name': 'Sune Skriver',
                        'uuid': '34705881-8af9-4254-ac3f-31738eae0be8'}],
             'offset': 0,
             'total': 2},
        )

        self.assertRequestResponse(
            '/service/e/1ce40e25-6238-4202-9e93-526b348ec745/',
            {
                "cpr_no": "1011101010",
                "name": "Sanne Sch\u00e4ff",
                "user_key": "sannes",
                "uuid": "1ce40e25-6238-4202-9e93-526b348ec745",
                "org": {
                    "name": "Ballerup Kommune",
                    "user_key": "Ballerup Kommune",
                    "uuid": "3a87187c-f25a-40a1-8d42-312b2e2b43bd",
                },
            },
        )

        self.assertRequestResponse(
            '/service/e/34705881-8af9-4254-ac3f-31738eae0be8/',
            {
                "cpr_no": "0101001010",
                "name": "Sune Skriver",
                "user_key": "sunes",
                "uuid": "34705881-8af9-4254-ac3f-31738eae0be8",
                "org": {
                    "name": "Ballerup Kommune",
                    "user_key": "Ballerup Kommune",
                    "uuid": "3a87187c-f25a-40a1-8d42-312b2e2b43bd",
                },
            },
        )

        with self.subTest('details list'):
            self.assertRequestResponse(
                '/service/e/34705881-8af9-4254-ac3f-31738eae0be8/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': True,
                    'it': False,
                    'leave': False,
                    'role': False,
                    'manager': False,
                },
            )

            self.assertRequestResponse(
                '/service/e/1ce40e25-6238-4202-9e93-526b348ec745/details/',
                {
                    'address': True,
                    'association': True,
                    'engagement': True,
                    'it': False,
                    'leave': True,
                    'role': True,
                    'manager': True,
                },
            )

            self.assertRequestResponse(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4/details/',
                {
                    'address': True,
                    'association': True,
                    'engagement': True,
                    'leave': False,
                    'role': True,
                    'org_unit': True,
                    'manager': True,
                },
            )

            self.assertRequestResponse(
                '/service/ou/921e44d3-2ec0-4c16-9935-2ec7976566dc/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': False,
                    'leave': False,
                    'role': False,
                    'org_unit': True,
                    'manager': False,
                },
            )

            self.assertRequestResponse(
                '/service/ou/c12393e9-ee1d-4b91-a6a9-a17508c055c9/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': False,
                    'leave': False,
                    'role': False,
                    'org_unit': True,
                    'manager': False,
                },
            )

            self.assertRequestResponse(
                '/service/ou/ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc/details/',
                {
                    'address': True,
                    'association': False,
                    'engagement': False,
                    'leave': False,
                    'role': False,
                    'org_unit': True,
                    'manager': False,
                },
            )

        with self.subTest('employee engagement'):
            self.assertRequestResponse(
                '/service/e/34705881-8af9-4254-ac3f-31738eae0be8'
                '/details/engagement',
                [
                    {
                        'job_function': {
                            'example': None,
                            'name': 'Administrativ leder',
                            'scope': None,
                            'user_key': 'Administrativ leder',
                            'uuid': 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee',
                        },
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            }
                        },
                        'person': {
                            'name': 'Sune Skriver',
                            'uuid': '34705881-8af9-4254-ac3f-31738eae0be8',
                        },
                        'engagement_type': {
                            'example': None,
                            'name': 'Ansat',
                            'scope': None,
                            'user_key': 'Ansat',
                            'uuid': '351fdf06-102a-4159-a5b4-69922b0ccde9',
                        },
                        'uuid': 'dd30c279-8bba-43a9-b4b7-6ac96e722f86',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/e/1ce40e25-6238-4202-9e93-526b348ec745'
                '/details/engagement',
                [{
                    'job_function': {
                        'example': None,
                        'name': 'Administrativ leder',
                        'scope': None,
                        'user_key': 'Administrativ leder',
                        'uuid': 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee',
                    },
                    'org_unit': {
                        'name': 'Ballerup Kommune',
                        'user_key': 'BALLERUP',
                        'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                        'validity': {
                            'from': '1964-05-24',
                            'to': None,
                        },
                    },
                    'person': {'name': 'Sanne Schäff',
                               'uuid': '1ce40e25-6238-4202-9e93-526b348ec745'},
                    'engagement_type': {
                        'example': None,
                        'name': 'Ansat',
                        'scope': None,
                        'user_key': 'Ansat',
                        'uuid': '351fdf06-102a-4159-a5b4-69922b0ccde9'},
                    'uuid': '7eadc1d9-19f5-46c7-a6db-f661c3a8fbb9',
                    "validity": {
                        'from': '2018-01-01',
                        'to': None
                    },
                }],
            )

        with self.subTest('unit engagement'):
            self.assertRequestResponse(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
                '/details/engagement',
                [
                    {
                        'job_function': {
                            'example': None,
                            'name': 'Administrativ leder',
                            'scope': None,
                            'user_key': 'Administrativ leder',
                            'uuid': 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee',
                        },
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'person': {
                            'name': 'Sanne Schäff',
                            'uuid': '1ce40e25-6238-4202-9e93-526b348ec745',
                        },
                        'engagement_type': {
                            'example': None,
                            'name': 'Ansat',
                            'scope': None,
                            'user_key': 'Ansat',
                            'uuid': '351fdf06-102a-4159-a5b4-69922b0ccde9',
                        },
                        'uuid': '7eadc1d9-19f5-46c7-a6db-f661c3a8fbb9',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                    {
                        'job_function': {
                            'example': None,
                            'name': 'Administrativ leder',
                            'scope': None,
                            'user_key': 'Administrativ leder',
                            'uuid': 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee',
                        },
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'person': {
                            'name': 'Sune Skriver',
                            'uuid': '34705881-8af9-4254-ac3f-31738eae0be8',
                        },
                        'engagement_type': {
                            'example': None,
                            'name': 'Ansat',
                            'scope': None,
                            'user_key': 'Ansat',
                            'uuid': '351fdf06-102a-4159-a5b4-69922b0ccde9',
                        },
                        'uuid': 'dd30c279-8bba-43a9-b4b7-6ac96e722f86',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('association'):
            self.assertRequestResponse(
                '/service/e/34705881-8af9-4254-ac3f-31738eae0be8'
                '/details/association',
                [],
            )

            self.assertRequestResponse(
                '/service/e/1ce40e25-6238-4202-9e93-526b348ec745'
                '/details/association',
                [
                    {
                        'address': None,
                        'job_function': {
                            'example': None,
                            'name': '… (≈400 flere)',
                            'scope': None,
                            'user_key': '… (≈400 flere)',
                            'uuid': 'f5b8f156-fa4e-46e2-b9e6-51a953166273',
                        },
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'person': {
                            'name': 'Sanne Schäff',
                            'uuid': '1ce40e25-6238-4202-9e93-526b348ec745',
                        },
                        'association_type': {
                            'example': None,
                            'name': 'Ansat',
                            'scope': None,
                            'user_key': 'Ansat',
                            'uuid': '39dd14ed-faa9-40bf-9fc9-13c440078458',
                        },
                        'uuid': 'b4cd77e4-2ba0-47c7-93e9-22f7446abb57',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
                '/details/association',
                [
                    {
                        'address': None,
                        'job_function': {
                            'example': None,
                            'name': '… (≈400 flere)',
                            'scope': None,
                            'user_key': '… (≈400 flere)',
                            'uuid': 'f5b8f156-fa4e-46e2-b9e6-51a953166273',
                        },
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'person': {
                            'name': 'Sanne Schäff',
                            'uuid': '1ce40e25-6238-4202-9e93-526b348ec745',
                        },
                        'association_type': {
                            'example': None,
                            'name': 'Ansat',
                            'scope': None,
                            'user_key': 'Ansat',
                            'uuid': '39dd14ed-faa9-40bf-9fc9-13c440078458',
                        },
                        'uuid': 'b4cd77e4-2ba0-47c7-93e9-22f7446abb57',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('role'):

            self.assertRequestResponse(
                '/service/e/1ce40e25-6238-4202-9e93-526b348ec745'
                '/details/role',
                [
                    {
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'person': {
                            'name': 'Sanne Schäff',
                            'uuid': '1ce40e25-6238-4202-9e93-526b348ec745',
                        },
                        'role_type': {
                            'example': None,
                            'name': 'Tillidsmand',
                            'scope': None,
                            'user_key': 'Tillidsmand',
                            'uuid': '0838d00d-e2b3-4aa8-a5a5-649c2205ab21',
                        },
                        'uuid': '3b204d9b-a0ba-48ad-9c20-778a49b6d3a9',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
                '/details/role',
                [
                    {
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'person': {
                            'name': 'Sanne Schäff',
                            'uuid': '1ce40e25-6238-4202-9e93-526b348ec745',
                        },
                        'role_type': {
                            'example': None,
                            'name': 'Tillidsmand',
                            'scope': None,
                            'user_key': 'Tillidsmand',
                            'uuid': '0838d00d-e2b3-4aa8-a5a5-649c2205ab21',
                        },
                        'uuid': '3b204d9b-a0ba-48ad-9c20-778a49b6d3a9',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('leave'):

            self.assertRequestResponse(
                '/service/e/1ce40e25-6238-4202-9e93-526b348ec745'
                '/details/leave',
                [
                    {
                        'person': {
                            'name': 'Sanne Schäff',
                            'uuid': '1ce40e25-6238-4202-9e93-526b348ec745',
                        },
                        'leave_type': {
                            'example': None,
                            'name': 'Barselsorlov',
                            'scope': None,
                            'user_key': 'Barselsorlov',
                            'uuid': 'd7ec3a18-3a9d-43c8-ad03-0202c0d044d4',
                        },
                        'uuid': 'd82de46c-e266-4810-9e8d-e99a0c9c18d5',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
                '/details/leave',
                [],
            )

        with self.subTest('manager'):

            self.assertRequestResponse(
                '/service/e/1ce40e25-6238-4202-9e93-526b348ec745'
                '/details/manager',
                [
                    {
                        'address': None,
                        'person': {
                            'name': 'Sanne Schäff',
                            'uuid': '1ce40e25-6238-4202-9e93-526b348ec745',
                        },
                        'manager_type': {
                            'example': None,
                            'name': 'Borgmester',
                            'user_key': 'Borgmester',
                            'scope': None,
                            'uuid': '6a6d5c82-a7d1-4488-b687-49daa3910ec1',
                        },
                        'responsibility': [{
                            'example': None,
                            'name': 'Ansvar for bygninger og arealer',
                            'user_key': 'Ansvar for bygninger og arealer',
                            'scope': None,
                            'uuid': '31388038-b979-47c8-be08-42d8846661af',
                        }],
                        'manager_level': {
                            'example': None,
                            'name': 'Niveau 90',
                            'user_key': 'Niveau 90',
                            'scope': None,
                            'uuid': '7d4d2609-7146-4a20-b9f0-fe4c19701217',
                        },
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'uuid': '8fb49f61-db3f-4f61-92c3-8a1dddd8051f',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

            self.assertRequestResponse(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
                '/details/manager',
                [
                    {
                        'address': None,
                        'person': {
                            'name': 'Sanne Schäff',
                            'uuid': '1ce40e25-6238-4202-9e93-526b348ec745',
                        },
                        'manager_type': {
                            'example': None,
                            'name': 'Borgmester',
                            'user_key': 'Borgmester',
                            'scope': None,
                            'uuid': '6a6d5c82-a7d1-4488-b687-49daa3910ec1',
                        },
                        'responsibility': [{
                            'example': None,
                            'name': 'Ansvar for bygninger og arealer',
                            'user_key': 'Ansvar for bygninger og arealer',
                            'scope': None,
                            'uuid': '31388038-b979-47c8-be08-42d8846661af',
                        }],
                        'manager_level': {
                            'example': None,
                            'name': 'Niveau 90',
                            'user_key': 'Niveau 90',
                            'scope': None,
                            'uuid': '7d4d2609-7146-4a20-b9f0-fe4c19701217',
                        },
                        'org_unit': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'uuid': '8fb49f61-db3f-4f61-92c3-8a1dddd8051f',
                        "validity": {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('employee I address'):
            self.assertRequestResponse(
                '/service/e/1ce40e25-6238-4202-9e93-526b348ec745'
                '/details/address',
                [
                    {
                        'address_type': {
                            'example': '+45 3334 9400',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': 'eb520fe5-eb72-4110-b81d-9c1a129dc22a',
                        },
                        'href': 'tel:+4511221122',
                        'name': '11221122',
                        'urn': 'urn:magenta.dk:telefon:+4511221122',
                        'validity': {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Lokation',
                            'scope': 'DAR',
                            'user_key': 'AdresseLokation',
                            'uuid': '031f93c3-6bab-462e-a998-87cad6db3128',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=12.57924839&mlat=55.68113676&zoom=16',
                        'name': 'Pilestræde 43, 3., 1112 København K',
                        'uuid': '0a3f50a0-23c9-32b8-e044-0003ba298018',
                        'validity': {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': 'hpe@korsbaek.dk',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': '80764a2f-6a7b-492c-92d9-96d24ac845ea',
                        },
                        'href': 'mailto:sanne@example.com',
                        'name': 'sanne@example.com',
                        'urn': 'urn:mailto:sanne@example.com',
                        'validity': {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('employee II address'):
            self.assertRequestResponse(
                '/service/e/34705881-8af9-4254-ac3f-31738eae0be8'
                '/details/address',
                [
                    {
                        'address_type': {
                            'example': '+45 3334 9400',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': 'eb520fe5-eb72-4110-b81d-9c1a129dc22a',
                        },
                        'href': 'tel:+4511223344',
                        'name': '11223344',
                        'urn': 'urn:magenta.dk:telefon:+4511223344',
                        'validity': {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': 'hpe@korsbaek.dk',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': '80764a2f-6a7b-492c-92d9-96d24ac845ea',
                        },
                        'href': 'mailto:sune@example.com',
                        'name': 'sune@example.com',
                        'urn': 'urn:mailto:sune@example.com',
                        'validity': {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Lokation',
                            'scope': 'DAR',
                            'user_key': 'AdresseLokation',
                            'uuid': '031f93c3-6bab-462e-a998-87cad6db3128',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=10.18779751&mlat=56.17233057&zoom=16',
                        'name': 'Åbogade 15, 8200 Aarhus N',
                        'uuid': '44c532e1-f617-4174-b144-d37ce9fda2bd',
                        'validity': {
                            'from': '2018-01-01',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('unit address'):
            self.assertRequestResponse(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
                '/details/address',
                [
                    {
                        'address_type': {
                            'example': '+45 3334 9400',
                            'name': 'Telefonnummer',
                            'scope': 'PHONE',
                            'user_key': 'Telefon',
                            'uuid': 'eb520fe5-eb72-4110-b81d-9c1a129dc22a',
                        },
                        'href': 'tel:+4544772000',
                        'name': '44772000',
                        'urn': 'urn:magenta.dk:telefon:+4544772000',
                        'validity': {
                            'from': '1964-05-24',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': '<UUID>',
                            'name': 'Postadresse',
                            'scope': 'DAR',
                            'user_key': 'AdressePost',
                            'uuid': 'a8c8fe66-2ab1-46ed-ba99-ed05e855d65f',
                        },
                        'href': 'https://www.openstreetmap.org/'
                        '?mlon=12.3647784&mlat=55.73404048&zoom=16',
                        'name': 'Hold-An Vej 7, 2750 Ballerup',
                        'uuid': 'bd7e5317-4a9e-437b-8923-11156406b117',
                        'validity': {
                            'from': '1964-05-24',
                            'to': None,
                        },
                    },
                    {
                        'address_type': {
                            'example': 'hpe@korsbaek.dk',
                            'name': 'Emailadresse',
                            'scope': 'EMAIL',
                            'user_key': 'Email',
                            'uuid': '80764a2f-6a7b-492c-92d9-96d24ac845ea',
                        },
                        'href': 'mailto:borger@balk.dk',
                        'name': 'borger@balk.dk',
                        'urn': 'urn:mailto:borger@balk.dk',
                        'validity': {
                            'from': '1964-05-24',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('unit address II'):
            self.assertRequestResponse(
                '/service/ou/921e44d3-2ec0-4c16-9935-2ec7976566dc'
                '/details/address',
                [{'address_type': {
                    'example': '+45 3334 9400',
                    'name': 'Telefonnummer',
                    'scope': 'PHONE',
                    'user_key': 'Telefon',
                    'uuid': 'eb520fe5-eb72-4110-b81d-9c1a129dc22a'},
                  'href': 'tel:+4544773333',
                  'name': '44773333',
                  'urn': 'urn:magenta.dk:telefon:+4544773333',
                  'validity': {
                      'from': '1993-01-01',
                      'to': None}},
                 {'address_type': {
                     'example': '<UUID>',
                     'name': 'Postadresse',
                     'scope': 'DAR',
                     'user_key': 'AdressePost',
                     'uuid': 'a8c8fe66-2ab1-46ed-ba99-ed05e855d65f'},
                  'href': 'https://www.openstreetmap.org/'
                  '?mlon=12.3597027&mlat=55.72970211&zoom=16',
                  'name': 'Banegårdspladsen 1, 2750 Ballerup',
                  'uuid': '99b29a62-01fd-40be-b5fe-8bfc4be35e83',
                  'validity': {
                      'from': '1993-01-01',
                      'to': None}},
                 {'address_type': {
                     'example': 'hpe@korsbaek.dk',
                     'name': 'Emailadresse',
                     'scope': 'EMAIL',
                     'user_key': 'Email',
                     'uuid': '80764a2f-6a7b-492c-92d9-96d24ac845ea'},
                  'href': 'mailto:ballerup-bibliotek@balk.dk',
                  'name': 'ballerup-bibliotek@balk.dk',
                  'urn': 'urn:mailto:ballerup-bibliotek@balk.dk',
                  'validity': {
                      'from': '1993-01-01',
                      'to': None}}],
            )

        with self.subTest('unit address III'):
            self.assertRequestResponse(
                '/service/ou/c12393e9-ee1d-4b91-a6a9-a17508c055c9'
                '/details/address',
                [{'address_type': {
                    'example': '<UUID>',
                    'name': 'Henvendelsessted',
                    'scope': 'DAR',
                    'user_key': 'AdresseHenvendelsesSted',
                    'uuid': 'ff4ed3b4-18fc-42cf-af12-51ac7b9a069a'},
                  'href': 'https://www.openstreetmap.org/'
                  '?mlon=12.40661136&mlat=55.72347773&zoom=16',
                  'name': 'Torvevej 21, 2740 Skovlunde',
                  'uuid': '45b40fc3-bb75-412c-b122-d9df7b0ade94',
                  'validity': {
                      'from': '2006-01-01',
                      'to': None}}],
            )

        with self.subTest('unit address IV'):
            self.assertRequestResponse(
                '/service/ou/ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc'
                '/details/address',
                [{'address_type': {
                    'example': '<UUID>',
                    'name': 'Postadresse',
                    'scope': 'DAR',
                    'user_key': 'AdressePost',
                    'uuid': 'a8c8fe66-2ab1-46ed-ba99-ed05e855d65f'},
                  'href': 'https://www.openstreetmap.org/'
                  '?mlon=12.37008192&mlat=55.71904978&zoom=16',
                  'name': 'Ballerup Idrætsby 38, 2750 Ballerup',
                  'uuid': '9ab45e95-a42a-47c0-b284-e5d2377fc429',
                  'validity': {
                      'from': '1993-01-01',
                      'to': None}},
                 {'address_type': {
                     'example': 'hpe@korsbaek.dk',
                     'name': 'Emailadresse',
                     'scope': 'EMAIL',
                     'user_key': 'Email',
                     'uuid': '80764a2f-6a7b-492c-92d9-96d24ac845ea'},
                  'href': 'mailto:tbri@balk.dk',
                  'name': 'tbri@balk.dk',
                  'urn': 'urn:mailto:tbri@balk.dk',
                  'validity': {
                      'from': '1993-01-01',
                      'to': None}}],
            )

        with self.subTest('unit it systems'):
            self.assertRequestFails(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
                '/details/it',
                400,
            )

        with self.subTest('unit info on employee'):
            self.assertRequestFails(
                '/service/e/34705881-8af9-4254-ac3f-31738eae0be8'
                '/details/org_unit',
                400,
            )

        with self.subTest('unit info I'):
            self.assertRequestResponse(
                '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
                '/details/org_unit',
                [
                    {
                        'name': 'Ballerup Kommune',
                        'user_key': 'BALLERUP',
                        'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                        'org': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'Ballerup Kommune',
                            'uuid': '3a87187c-f25a-40a1-8d42-312b2e2b43bd',
                        },
                        'org_unit_type': {
                            'example': None,
                            'name': 'Kommune',
                            'scope': None,
                            'user_key': 'Kommune',
                            'uuid': 'f2f93f92-d08f-4b76-904f-af9144e23195',
                        },
                        'parent': None,
                        'validity': {
                            'from': '1964-05-24',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('unit info II'):
            self.assertRequestResponse(
                '/service/ou/921e44d3-2ec0-4c16-9935-2ec7976566dc'
                '/details/org_unit',
                [
                    {
                        'name': 'Ballerup Bibliotek',
                        'user_key': 'BIBLIOTEK',
                        'uuid': '921e44d3-2ec0-4c16-9935-2ec7976566dc',
                        'org': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'Ballerup Kommune',
                            'uuid': '3a87187c-f25a-40a1-8d42-312b2e2b43bd',
                        },
                        'org_unit_type': {
                            'example': None,
                            'name': 'Institution',
                            'scope': None,
                            'user_key': 'Institution',
                            'uuid': '547e6946-abdb-4dc2-ad99-b6042e05a7e4',
                        },
                        'parent': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'validity': {
                            'from': '1993-01-01',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('unit info III'):
            self.assertRequestResponse(
                '/service/ou/c12393e9-ee1d-4b91-a6a9-a17508c055c9'
                '/details/org_unit',
                [
                    {
                        'user_key': 'FAMILIEHUS',
                        'uuid': 'c12393e9-ee1d-4b91-a6a9-a17508c055c9',
                        'name': 'Ballerup Familiehus',
                        'org': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'Ballerup Kommune',
                            'uuid': '3a87187c-f25a-40a1-8d42-312b2e2b43bd',
                        },
                        'org_unit_type': {
                            'example': None,
                            'name': 'Fagligt Center',
                            'scope': None,
                            'user_key': 'Fagligt Center',
                            'uuid': '59f10075-88f6-4758-bf61-454858170776',
                        },
                        'parent': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'validity': {
                            'from': '2006-01-01',
                            'to': None,
                        },
                    },
                ],
            )

        with self.subTest('unit info IV'):
            self.assertRequestResponse(
                '/service/ou/ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc'
                '/details/org_unit',
                [
                    {
                        'name': 'Ballerup Idrætspark',
                        'user_key': 'IDRÆTSPARK',
                        'uuid': 'ef04b6ba-8ba7-4a25-95e3-774f38e5d9bc',
                        'org': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'Ballerup Kommune',
                            'uuid': '3a87187c-f25a-40a1-8d42-312b2e2b43bd',
                        },
                        'org_unit_type': {
                            'example': None,
                            'name': 'Institution',
                            'scope': None,
                            'user_key': 'Institution',
                            'uuid': '547e6946-abdb-4dc2-ad99-b6042e05a7e4',
                        },
                        'parent': {
                            'name': 'Ballerup Kommune',
                            'user_key': 'BALLERUP',
                            'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4',
                            'validity': {
                                'from': '1964-05-24',
                                'to': None,
                            },
                        },
                        'validity': {
                            'from': '1993-01-01',
                            'to': None,
                        },
                    },
                ],
            )
