#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os

import freezegun

from . import util


class IntegrationTests(util.LoRATestCase):
    maxDiff = None

    @freezegun.freeze_time('2017-06-01')
    def test_with_import(self):
        util.import_fixture('MAGENTA_01.json')

        with self.subTest('org unit types'):
                self.assertRequestResponse(
                    '/mo/org-unit/type',
                    [
                        {
                            "name": "Afdeling",
                            "user-key": "Afdeling",
                            "userKey": "Afdeling",
                            "uuid": "ac8206d0-b807-44f1-9a29-f252b926917e"
                        },
                        {
                            "name": "Center",
                            "user-key": "Center",
                            "userKey": "Center",
                            "uuid": "8cce4b27-4bfe-4627-a61e-75792148d7a9"
                        },
                        {
                            "name": "Direktion",
                            "user-key": "Direktion",
                            "userKey": "Direktion",
                            "uuid": "d60db620-7c2b-4a76-b15e-ae3478a4f2f9"
                        },
                        {
                            "name": "Enhed",
                            "user-key": "Enhed",
                            "userKey": "Enhed",
                            "uuid": "5b6d3b8c-7047-4c32-8fde-5d6e0e6c972f"
                        },
                        {
                            "name": "Forvaltning",
                            "user-key": "Forvaltning",
                            "userKey": "Forvaltning",
                            "uuid": "7def0dc1-2982-40d6-ac20-7315b42325aa"
                        },
                        {
                            "name": "Kontor",
                            "user-key": "Kontor",
                            "userKey": "Kontor",
                            "uuid": "333b3660-438b-4a5a-9982-2790ed4626d8"
                        },
                        {
                            "name": "Projekt",
                            "user-key": "Projekt",
                            "userKey": "Projekt",
                            "uuid": "254c6782-9fef-478a-89b3-c043ca7cb0e9"
                        },
                        {
                            "name": "Sekretariat",
                            "user-key": "Sekretariat",
                            "userKey": "Sekretariat",
                            "uuid": "f24b718c-951d-4152-9b1b-d62d824527d1"
                        }
                    ],
                )

        with self.subTest('engagement types'):
            self.assertRequestResponse(
                '/mo/role-types/engagement/facets/type/classes/',
                [
                    {
                        "name": "Abonnent",
                        "user-key": "Abonnent",
                        "userKey": "Abonnent",
                        "uuid": "1e87ea79-f53e-4a9b-8e74-52bb6e164e4f"
                    },
                    {
                        "name": "Administrerende direkt\u00f8r",
                        "user-key": "Administrerende direkt\u00f8r",
                        "userKey": "Administrerende direkt\u00f8r",
                        "uuid": "cddeb3c0-3b5c-4489-919d-aac6cdc48cd4"
                    },
                    {
                        "name": "Administrerende direkt\u00f8r",
                        "user-key": "Administrerende direkt\u00f8r",
                        "userKey": "Administrerende direkt\u00f8r",
                        "uuid": "f38a3f87-4134-472f-9aaf-ca3b78d73a51"
                    },
                    {
                        "name": "Bestyrelsesformand",
                        "user-key": "Bestyrelsesformand",
                        "userKey": "Bestyrelsesformand",
                        "uuid": "1e0af001-cc2b-4870-b248-3a8592f6e41f"
                    },
                    {
                        "name": "Bestyrelsesmedlem",
                        "user-key": "Bestyrelsesmedlem",
                        "userKey": "Bestyrelsesmedlem",
                        "uuid": "8b9156c0-3b33-4885-8102-154081439e0a"
                    },
                    {
                        "name": "Brugeradministrator",
                        "user-key": "Brugeradministrator",
                        "userKey": "Brugeradministrator",
                        "uuid": "e3b24743-d65b-44ab-b257-4f33bcfa0ea8"
                    },
                    {
                        "name": "Brugerrolle",
                        "user-key": "Brugerrolle",
                        "userKey": "Brugerrolle",
                        "uuid": "a4a86b47-2b38-4475-a5fa-9b07a724f0c6"
                    },
                    {
                        "name": "Chef",
                        "user-key": "Chef",
                        "userKey": "Chef",
                        "uuid": "e0aecf9a-57f8-404d-8643-bb1cf724852c"
                    },
                    {
                        "name": "Chefkonsulent",
                        "user-key": "Chefkonsulent",
                        "userKey": "Chefkonsulent",
                        "uuid": "348a8b36-e2f8-48d2-8737-35c912b4cba4"
                    },
                    {
                        "name": "Direkt\u00f8r",
                        "user-key": "Direkt\u00f8r",
                        "userKey": "Direkt\u00f8r",
                        "uuid": "58d437de-520f-4580-9cae-e3883fd300d1"
                    },
                    {
                        "name": "Direkt\u00f8r",
                        "user-key": "Direkt\u00f8r",
                        "userKey": "Direkt\u00f8r",
                        "uuid": "ed927f2b-164e-4fbb-981d-5d17f46e574b"
                    },
                    {
                        "name": "Enhedsrolle",
                        "user-key": "Enhedsrolle",
                        "userKey": "Enhedsrolle",
                        "uuid": "bd8cb10c-7522-4db9-8bfc-c62c75df4396"
                    },
                    {
                        "name": "Itsystemrolle",
                        "user-key": "Itsystemrolle",
                        "userKey": "Itsystemrolle",
                        "uuid": "e49e41e7-72af-4a0f-beae-88aa5e1594b9"
                    },
                    {
                        "name": "Konsulent",
                        "user-key": "Konsulent",
                        "userKey": "Konsulent",
                        "uuid": "725235dd-fa5d-473d-857a-db2f73e98d36"
                    },
                    {
                        "name": "Konsulent - Digitalisering",
                        "user-key": "Konsulent - Digitalisering",
                        "userKey": "Konsulent - Digitalisering",
                        "uuid": "213aa7bc-7519-4e98-916e-053ea2f8b193"
                    },
                    {
                        "name": "Konsulent - IT",
                        "user-key": "Konsulent - IT",
                        "userKey": "Konsulent - IT",
                        "uuid": "5975f035-d903-4d53-90b7-6ca9ac1bb023"
                    },
                    {
                        "name": "Konsulent - IT arkitektur",
                        "user-key": "Konsulent - IT arkitektur",
                        "userKey": "Konsulent - IT arkitektur",
                        "uuid": "c0aafd84-7f02-45f1-bf39-5e67f8b36e82"
                    },
                    {
                        "name": "Konsulent - Implementering",
                        "user-key": "Konsulent - Implementering",
                        "userKey": "Konsulent - Implementering",
                        "uuid": "434348ee-d341-4c3d-b4cf-a03877894f82"
                    },
                    {
                        "name": "Konsulent - Jura",
                        "user-key": "Konsulent - Jura",
                        "userKey": "Konsulent - Jura",
                        "uuid": "3334f965-c020-4ae9-99d0-923baccaaf0f"
                    },
                    {
                        "name": "Konsulent - Projektleder",
                        "user-key": "Konsulent - Projektleder",
                        "userKey": "Konsulent - Projektleder",
                        "uuid": "4944055e-46ab-4a6a-bd45-017f3a9d9eb8"
                    },
                    {
                        "name": "Konsulent - Sikkerhed",
                        "user-key": "Konsulent - Sikkerhed",
                        "userKey": "Konsulent - Sikkerhed",
                        "uuid": "bebb1f27-3d5f-4b92-a35d-5732a50ce184"
                    },
                    {
                        "name": "Konsulent - Teknik",
                        "user-key": "Konsulent - Teknik",
                        "userKey": "Konsulent - Teknik",
                        "uuid": "e90772d1-7279-47e6-abfe-2085ef867202"
                    },
                    {
                        "name": "Kontorchef",
                        "user-key": "Kontorchef",
                        "userKey": "Kontorchef",
                        "uuid": "74028761-31ce-44af-8d2e-12b065094be0"
                    },
                    {
                        "name": "Leder",
                        "user-key": "Leder",
                        "userKey": "Leder",
                        "uuid": "6fd38cb6-4836-4e4c-a5de-148bc9824eaf"
                    },
                    {
                        "name": "Medarbejder",
                        "user-key": "Medarbejder",
                        "userKey": "Medarbejder",
                        "uuid": "dfba6e03-c3aa-46fc-a357-d638602cd90c"
                    },
                    {
                        "name": "Objektrolle",
                        "user-key": "Objektrolle",
                        "userKey": "Objektrolle",
                        "uuid": "3922e7db-3694-4cc7-9f06-350c3bd6ddb0"
                    },
                    {
                        "name": "Organisationsrolle",
                        "user-key": "Organisationsrolle",
                        "userKey": "Organisationsrolle",
                        "uuid": "2cb2aa58-4f6c-46ca-bae0-68b4d587df14"
                    },
                    {
                        "name": "Procesejer",
                        "user-key": "Procesejer",
                        "userKey": "Procesejer",
                        "uuid": "3b9cadd5-d488-4e97-a16d-f8e128cd7ac4"
                    },
                    {
                        "name": "Procesrolle",
                        "user-key": "Procesrolle",
                        "userKey": "Procesrolle",
                        "uuid": "eeb488ea-3f0c-4f33-9c92-c93cda82e8e1"
                    },
                    {
                        "name": "Projektrolle",
                        "user-key": "Projektrolle",
                        "userKey": "Projektrolle",
                        "uuid": "cc6756b5-30f0-4877-b7f1-cae1179bf852"
                    },
                    {
                        "name": "Ressourceperson",
                        "user-key": "Ressourceperson",
                        "userKey": "Ressourceperson",
                        "uuid": "db41761d-c4eb-4d00-98a2-e9f81fadd45c"
                    },
                    {
                        "name": "Souchef",
                        "user-key": "Souchef",
                        "userKey": "Souchef",
                        "uuid": "bce9038b-2423-4f3a-ac5f-ef0f212d322d"
                    },
                    {
                        "name": "Specialkonsulent",
                        "user-key": "Specialkonsulent",
                        "userKey": "Specialkonsulent",
                        "uuid": "7bb70272-8d2d-48f6-a5a8-9eb1b526c5d5"
                    },
                    {
                        "name": "Stedfortr\u00e6der",
                        "user-key": "Stedfortr\u00e6der",
                        "userKey": "Stedfortr\u00e6der",
                        "uuid": "08963109-1bfd-4066-a2c3-296dcdc56e0e"
                    },
                    {
                        "name": "Stedfortr\u00e6der",
                        "user-key": "Stedfortr\u00e6der",
                        "userKey": "Stedfortr\u00e6der",
                        "uuid": "e7294990-1288-405d-ad63-b8bda06a8aae"
                    },
                    {
                        "name": "Student",
                        "user-key": "Student",
                        "userKey": "Student",
                        "uuid": "a3723019-811a-4697-803f-14012ce6ba03"
                    },
                    {
                        "name": "Superbruger",
                        "user-key": "Superbruger",
                        "userKey": "Superbruger",
                        "uuid": "65fff4d2-6528-43d3-8a5b-bda363ada897"
                    },
                    {
                        "name": "Supporter",
                        "user-key": "Supporter",
                        "userKey": "Supporter",
                        "uuid": "7008dce8-3151-4f9b-a248-cfa21ea46a7d"
                    },
                    {
                        "name": "Systemadministrator",
                        "user-key": "Systemadministrator",
                        "userKey": "Systemadministrator",
                        "uuid": "6fd90212-a4cb-4734-b128-85095d9db53c"
                    },
                    {
                        "name": "Systemejer",
                        "user-key": "Systemejer",
                        "userKey": "Systemejer",
                        "uuid": "aa6b1ab5-3d7b-43e7-8c76-4a627c03e979"
                    }
                ],
            )

        with self.subTest('job titles'):
            self.assertRequestResponse(
                '/mo/role-types/engagement/facets/job-title/classes/',
                [
                    {
                        "name": "Ceremonimester",
                        "user-key": "Ceremonimester",
                        "userKey": "Ceremonimester",
                        "uuid": "66ba8830-9faa-467e-8723-0c256c196273"
                    },
                    {
                        "name": "Tinglaver",
                        "user-key": "Tinglaver",
                        "userKey": "Tinglaver",
                        "uuid": "9c2dc91e-4e48-4748-aa76-b1a95bf1ee9e"
                    }
                ],
            )

        with self.subTest('organisations'):
            self.assertRequestResponse(
                '/service/o/',
                [{'name': 'Aarhus Kommune',
                  'user_key': 'Aarhus Kommune',
                  'uuid': '59141156-ed0b-457c-9535-884447c5220b'},
                 {'name': 'Magenta ApS',
                  'user_key': 'Magenta ApS',
                  'uuid': '8efbd074-ad2a-4e6a-afec-1d0b1891f566'}],
            )

            self.assertRequestResponse(
                '/mo/o/',
                [
                    {
                        'hierarchy': {
                            'children': [],
                            'hasChildren': True,
                            'name': 'Aarhus Kommune',
                            'org': '59141156-ed0b-457c-9535-884447c5220b',
                            'user-key': 'ÅRHUS',
                            'uuid': '746eeba3-30a9-4c0a-8d22-c6f34af1095f',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        'name': 'Aarhus Kommune',
                        'user-key': 'Aarhus Kommune',
                        'uuid': '59141156-ed0b-457c-9535-884447c5220b',
                        'valid-from': '01-01-1976',
                        'valid-to': 'infinity',
                    },
                    {
                        'hierarchy': {
                            'children': [],
                            'hasChildren': True,
                            'name': 'Magenta ApS',
                            'org': '8efbd074-ad2a-4e6a-afec-1d0b1891f566',
                            'user-key': 'MAGENTA',
                            'uuid': '01e479c4-66ef-42aa-877e-15f0512f792c',
                            'valid-from': '15-11-1999',
                            'valid-to': 'infinity',
                        },
                        'name': 'Magenta ApS',
                        'user-key': 'Magenta ApS',
                        'uuid': '8efbd074-ad2a-4e6a-afec-1d0b1891f566',
                        'valid-from': '15-11-1999',
                        'valid-to': 'infinity',
                    },
                ],
            )

        with self.subTest('users'):
            for user in self.client.get('/mo/e/').json:
                self.assertRegex(user['user-key'], r'\A\d{10}\Z')

            self.assertRequestResponse(
                '/service/o/8efbd074-ad2a-4e6a-afec-1d0b1891f566/e/',
                [{'name': 'Hans Bruger',
                  'uuid': '9917e91c-e3ee-41bf-9a60-b024c23b5fe3'},
                 {'name': 'Joe User',
                  'uuid': 'cd2dcfad-6d34-4553-9fee-a7023139a9e8'},
                 {'name': 'MAAAAAM',
                  'uuid': 'f715a2c9-a425-4cc9-b69b-7d89aaedece4'}],
            )

            self.assertRequestResponse(
                '/mo/e/',
                [
                    {
                        "name": "Hans Bruger",
                        "nick-name": "bruger",
                        "user-key": '1011101010',
                        "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3"
                    },
                    {
                        'name': 'Joe User',
                        'nick-name': 'user',
                        'user-key': '0101001010',
                        'uuid': 'cd2dcfad-6d34-4553-9fee-a7023139a9e8',
                    },
                    {
                        'name': 'MAAAAAM',
                        'nick-name': 'mam',
                        'user-key': '1402840002',
                        'uuid': 'f715a2c9-a425-4cc9-b69b-7d89aaedece4'
                    },
                ]
            )

        with self.subTest('get user by cpr'):

            self.assertRequestResponse(
                '/mo/e/1011101010/',
                {
                    "name": "Hans Bruger",
                    "nick-name": "bruger",
                    "user-key": "1011101010",
                    "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3",
                },
            )

            self.assertRequestResponse(
                '/mo/e/0101001010/',
                {
                    "name": "Joe User",
                    "nick-name": "user",
                    "user-key": "0101001010",
                    "uuid": "cd2dcfad-6d34-4553-9fee-a7023139a9e8"
                },
            )

            self.assertRequestResponse(
                '/mo/e/1402840002/',
                {
                    "name": "MAAAAAM",
                    "nick-name": "mam",
                    "user-key": "1402840002",
                    "uuid": "f715a2c9-a425-4cc9-b69b-7d89aaedece4"
                },
            )

        with self.subTest('searches'):
            # searching must work
            self.assertRequestResponse(
                '/mo/e/?query=Hans',
                [
                    {
                        "name": "Hans Bruger",
                        "nick-name": "bruger",
                        "user-key": "1011101010",
                        "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3",
                    },
                ],
            )

            self.assertRequestResponse(
                '/mo/e/?query=MAAAAAM',
                [
                    {
                        "name": "MAAAAAM",
                        "nick-name": "mam",
                        "user-key": "1402840002",
                        "uuid": "f715a2c9-a425-4cc9-b69b-7d89aaedece4"
                    },
                ],
            )

            self.assertRequestResponse(
                '/mo/e/?query=maaaaam',
                [
                    {
                        "name": "MAAAAAM",
                        "nick-name": "mam",
                        "user-key": "1402840002",
                        "uuid": "f715a2c9-a425-4cc9-b69b-7d89aaedece4"
                    },
                ],
            )

            # we must also match the bvn
            self.assertRequestResponse(
                '/mo/e/?query=mam',
                [
                    {
                        "name": "MAAAAAM",
                        "nick-name": "mam",
                        "user-key": "1402840002",
                        "uuid": "f715a2c9-a425-4cc9-b69b-7d89aaedece4"
                    },
                ],
            )

            # 10 digits means a CPR number
            self.assertRequestResponse(
                '/mo/e/?query=1011101010',
                [
                    {
                        "name": "Hans Bruger",
                        "nick-name": "bruger",
                        "user-key": "1011101010",
                        "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3",
                    },
                ],
            )

            # ...but partial matches must not work
            self.assertRequestFails(
                '/mo/e/?query=101110101',
                404,
            )

            self.assertRequestFails(
                '/mo/e/?query=0000000000',
                404,
            )

        with self.subTest('get user by uuid'):
            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3/',
                {
                    "name": "Hans Bruger",
                    "nick-name": "bruger",
                    "user-key": '1011101010',
                    "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3"
                },
            )

            self.assertRequestResponse(
                '/mo/e/cd2dcfad-6d34-4553-9fee-a7023139a9e8/',
                {
                    "name": "Joe User",
                    "nick-name": "user",
                    "user-key": "0101001010",
                    "uuid": "cd2dcfad-6d34-4553-9fee-a7023139a9e8"
                },
            )

            self.assertRequestResponse(
                '/mo/e/f715a2c9-a425-4cc9-b69b-7d89aaedece4/',
                {
                    "name": "MAAAAAM",
                    "nick-name": "mam",
                    "user-key": "1402840002",
                    "uuid": "f715a2c9-a425-4cc9-b69b-7d89aaedece4"
                },
            )

        with self.subTest('get user engagements'):
            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/engagement/',
                [
                    {
                        'job-title': {
                            'name': 'Fest',
                            'user-key': '336273',
                            'uuid': '5c104648-56b4-46e8-bd08-501736843177',
                        },
                        'org': None,
                        'org-unit': {
                            'activeName': 'Hovedkvarteret',
                            'name': 'Hovedkvarteret',
                            'org': '8efbd074-ad2a-4e6a-afec-1d0b1891f566',
                            'parent': '01e479c4-66ef-42aa-877e-15f0512f792c',
                            'parent-object': None,
                            'type': {
                                'name': 'Kontor',
                                'user-key': 'Kontor',
                                'userKey': 'Kontor',
                                'uuid': '333b3660-438b-4a5a-9982-2790ed4626d8',
                            },
                            'user-key': 'MAGENTA-HQ',
                            'uuid': '514e8a8e-2d3f-4789-9237-0492688d5024',
                            'valid-from': '15-11-1999',
                            'valid-to': 'infinity',
                        },
                        'person': '9917e91c-e3ee-41bf-9a60-b024c23b5fe3',
                        'person-name': 'Hans Bruger',
                        'role-type': 'engagement',
                        'type': {
                            'name': 'Tinglaver',
                            'user-key': 'Tinglaver',
                            'userKey': 'Tinglaver',
                            'uuid': '9c2dc91e-4e48-4748-aa76-b1a95bf1ee9e',
                        },
                        'uuid': '5c104648-56b4-46e8-bd08-501736843177',
                        'valid-from': '14-02-2016',
                        'valid-to': 'infinity',
                    },
                ],
            )

            self.assertRequestResponse(
                '/mo/e/cd2dcfad-6d34-4553-9fee-a7023139a9e8'
                '/role-types/engagement/',
                [
                    {
                        "job-title": {
                            "name": "Hest",
                            "user-key": "398538",
                            "uuid": "a0324d15-5317-45b0-a320-7466670463b1",
                        },
                        "org": None,
                        "org-unit": {
                            "activeName": "Aarhuskontoret",
                            "name": "Aarhuskontoret",
                            "org": "8efbd074-ad2a-4e6a-afec-1d0b1891f566",
                            "parent": "01e479c4-66ef-42aa-877e-15f0512f792c",
                            "parent-object": None,
                            "type": {
                                "name": "Kontor",
                                "user-key": "Kontor",
                                "userKey": "Kontor",
                                "uuid": "333b3660-438b-4a5a-9982-2790ed4626d8",
                            },
                            "user-key": "MAGENTA-AAR",
                            "uuid": "8a32549b-458e-4ff3-814d-9155963c519a",
                            "valid-from": "07-08-2014",
                            "valid-to": "infinity",
                        },
                        "person": "cd2dcfad-6d34-4553-9fee-a7023139a9e8",
                        "person-name": "Joe User",
                        "role-type": "engagement",
                        "type": {
                            "name": "Ceremonimester",
                            "user-key": "Ceremonimester",
                            "userKey": "Ceremonimester",
                            "uuid": "66ba8830-9faa-467e-8723-0c256c196273",
                        },
                        "uuid": "a0324d15-5317-45b0-a320-7466670463b1",
                        "valid-from": "15-02-2016",
                        "valid-to": "infinity",
                    },
                ],
            )

            self.assertRequestResponse(
                '/mo/e/f715a2c9-a425-4cc9-b69b-7d89aaedece4'
                '/role-types/engagement/',
                [],
            )

        with self.subTest('get unit engagements'):
            expected = [
                {
                    'job-title': {
                        'name': 'Hest',
                        'user-key': '398538',
                        'uuid': 'a0324d15-5317-45b0-a320-7466670463b1',
                    },
                    'org': None,
                    'org-unit': {
                        'activeName': 'Aarhuskontoret',
                        'name': 'Aarhuskontoret',
                        'org': '8efbd074-ad2a-4e6a-afec-1d0b1891f566',
                        'parent': '01e479c4-66ef-42aa-877e-15f0512f792c',
                        'parent-object': None,
                        'type': {
                            'name': 'Kontor',
                            'user-key': 'Kontor',
                            'userKey': 'Kontor',
                            'uuid': '333b3660-438b-4a5a-9982-2790ed4626d8',
                        },
                        'user-key': 'MAGENTA-AAR',
                        'uuid': '8a32549b-458e-4ff3-814d-9155963c519a',
                        'valid-from': '07-08-2014',
                        'valid-to': 'infinity',
                    },
                    'person': 'cd2dcfad-6d34-4553-9fee-a7023139a9e8',
                    'person-name': 'Joe User',
                    'role-type': 'engagement',
                    'type': {
                        'name': 'Ceremonimester',
                        'user-key': 'Ceremonimester',
                        'userKey': 'Ceremonimester',
                        'uuid': '66ba8830-9faa-467e-8723-0c256c196273',
                    },
                    'uuid': 'a0324d15-5317-45b0-a320-7466670463b1',
                    'valid-from': '15-02-2016',
                    'valid-to': 'infinity',
                },
            ]

            self.assertRequestResponse(
                '/mo/o/8efbd074-ad2a-4e6a-afec-1d0b1891f566'
                '/org-unit/8a32549b-458e-4ff3-814d-9155963c519a'
                '/role-types/engagement/',
                expected,
            )

            self.assertRequestResponse(
                '/mo/org-unit/8a32549b-458e-4ff3-814d-9155963c519a'
                '/role-types/engagement/',
                expected,
            )

        with self.subTest('get user contact channels'):
            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact-channel/',
                [
                    {
                        'contact-info': 'bruger@example.com',
                        'location': {'name': '—'},
                        'name': 'Mail',
                        'phone-type': {
                            'name': 'Mail',
                            'prefix': 'urn:mailto:',
                            'user-key': 'Email',
                        },
                        'type': {
                            'name': 'Mail',
                            'prefix': 'urn:mailto:',
                            'user-key': 'Email',
                        },
                        'valid-from': '14-02-2016',
                        'valid-to': 'infinity',
                        'visibility': {
                            'name': 'Må vises internt',
                            'user-key': 'internal',
                            'uuid': 'ab68b2c2-8ffb-4292-a938-60e3afe0cad0',
                        }
                    },
                ],
            )

            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact-channel/?validity=past',
                [],
            )

            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact-channel/?validity=future',
                [],
            )

        with self.subTest('get user locations'):
            # FIXME: add some user locations to the import
            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/location/',
                [],
            )

        with self.subTest('write user contact channel'):
            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact',
                '9917e91c-e3ee-41bf-9a60-b024c23b5fe3',
                json={
                    "phone-type": {
                        "name": "Mail",
                        "prefix": "urn:mailto:",
                        "uuid": "c88aca96-eab9-42e9-ba6d-4f3868234573"
                    },
                    "contact-info": "test@example.com",
                    "properties": {
                        "name": "Må vises internt",
                        "user-key": "internal",
                        "uuid": "internal"
                    },
                    "valid-from": "01-01-2018",
                    "person": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3",
                    "role-type": "contact",
                    "user-key": "NULL",
                    "$$hashKey": "1L5"
                }
            )

            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact-channel/?validity=present',
                [
                    {
                        'contact-info': 'bruger@example.com',
                        'location': {'name': '—'},
                        'name': 'Mail',
                        'phone-type': {
                            'name': 'Mail',
                            'prefix': 'urn:mailto:',
                            'user-key': 'Email',
                        },
                        'type': {
                            'name': 'Mail',
                            'prefix': 'urn:mailto:',
                            'user-key': 'Email',
                        },
                        'valid-from': '14-02-2016',
                        'valid-to': 'infinity',
                        'visibility': {
                            'name': 'Må vises internt',
                            'user-key': 'internal',
                            'uuid': 'ab68b2c2-8ffb-4292-a938-60e3afe0cad0',
                        }
                    },
                ],
            )

            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact-channel/?validity=past',
                [],
            )

            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact',
                '9917e91c-e3ee-41bf-9a60-b024c23b5fe3',
                json={
                    "valid-from": "01-01-2017",
                    "valid-to": "01-05-2017",
                    "phone-type": {
                        "name": "Telefonnummer",
                        "prefix": "urn:magenta.dk:telefon:",
                        "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
                    },
                    "contact-info": "88888888",
                    "properties": {
                        "name": "Må vises eksternt",
                        "user-key": "external",
                        "uuid": "external"
                    },
                    "person": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3",
                    "role-type": "contact",
                    "user-key": "NULL",
                    "$$hashKey": "1KF"
                },
            )

            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact-channel/?validity=past',
                [
                    {
                        'contact-info': '88888888',
                        'location': {
                            'name': '—',
                        },
                        'name': 'Telefonnummer',
                        'phone-type': {
                            'name': 'Telefonnummer',
                            'prefix': 'urn:magenta.dk:telefon:',
                            'user-key': 'Telephone_number',
                        },
                        'type': {
                            'name': 'Telefonnummer',
                            'prefix': 'urn:magenta.dk:telefon:',
                            'user-key': 'Telephone_number',
                        },
                        'valid-from': '01-01-2017',
                        'valid-to': '01-05-2017',
                        'visibility': {
                            'name': 'Må vises eksternt',
                            'user-key': 'external',
                            'uuid': 'c67d7315-a0a2-4238-a883-f33aa7ddabc2',
                        },
                    },
                ],
            )

            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact-channel/?validity=present',
                [
                    {
                        'contact-info': 'bruger@example.com',
                        'location': {'name': '—'},
                        'name': 'Mail',
                        'phone-type': {
                            'name': 'Mail',
                            'prefix': 'urn:mailto:',
                            'user-key': 'Email',
                        },
                        'type': {
                            'name': 'Mail',
                            'prefix': 'urn:mailto:',
                            'user-key': 'Email',
                        },
                        'valid-from': '14-02-2016',
                        'valid-to': 'infinity',
                        'visibility': {
                            'name': 'Må vises internt',
                            'user-key': 'internal',
                            'uuid': 'ab68b2c2-8ffb-4292-a938-60e3afe0cad0',
                        }
                    },
                ],
            )

            # FIXME: adding an old address deletes future ones?!
            self.assertRequestResponse(
                '/mo/e/9917e91c-e3ee-41bf-9a60-b024c23b5fe3'
                '/role-types/contact-channel/?validity=future',
                [],
            )

    @freezegun.freeze_time('2018-06-01')
    def test_service_with_ballerup(self):
        util.import_fixture('BALLERUP.xlsx')

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/',
            [{'name': 'address',
              'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/'
              '0b4a9cae-5e01-4694-ae92-a1c07d5f2ab2/',
              'user_key': 'Adressetype',
              'uuid': '0b4a9cae-5e01-4694-ae92-a1c07d5f2ab2'},
             {'name': 'job-title',
              'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/'
              '51774dde-bf2c-4100-9059-70d1a1fb1d1f/',
              'user_key': 'Stillingsbetegnelse',
              'uuid': '51774dde-bf2c-4100-9059-70d1a1fb1d1f'},
             {'name': 'ou',
              'path': '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/'
              'd2a8b57a-5913-47c9-8ead-99b9822e27fa/',
              'user_key': 'Enhedstype',
              'uuid': 'd2a8b57a-5913-47c9-8ead-99b9822e27fa'}],
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/children',
            [{'child_count': 0,
              'name': 'Ballerup Kommune',
              'user_key': 'BALLERUP',
              'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'}],
        )

        self.assertRequestResponse(
            '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4/children',
            [],
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/ou/',
            [{'name': 'Ballerup Kommune',
              'user_key': 'BALLERUP',
              'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'}],
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/address/',
            [{'example': 'Besvares indenfor to hverdage.',
              'name': 'Bemærkninger om email',
              'scope': 'TEXT',
              'user_key': 'Email bemærkninger',
              'uuid': 'e86c1e6f-934c-42b2-8a6b-20d1b7ea79a5'},
             {'example': '5790001969370',
              'name': 'EAN',
              'scope': 'INTEGER',
              'user_key': 'EAN',
              'uuid': 'a88aa93b-8edc-46ab-bad7-6535f9b765e5'},
             {'example': 'hpe@korsbaek.dk',
              'name': 'Emailadresse',
              'scope': 'EMAIL',
              'user_key': 'Email',
              'uuid': '80764a2f-6a7b-492c-92d9-96d24ac845ea'},
             {'example': '<UUID>',
              'name': 'Henvendelsessted',
              'scope': 'DAR',
              'user_key': 'AdresseHenvendelsesSted',
              'uuid': 'ff4ed3b4-18fc-42cf-af12-51ac7b9a069a'},
             {'example': 'http://www.korsbaek.dk/',
              'name': 'Hjemmeside',
              'scope': 'WWW',
              'user_key': 'URL',
              'uuid': '160ecaed-50b0-4800-bebc-0d0289a4f624'},
             {'example': '<UUID>',
              'name': 'Lokation',
              'scope': 'DAR',
              'user_key': 'AdresseLokation',
              'uuid': '031f93c3-6bab-462e-a998-87cad6db3128'},
             {'example': '<UUID>',
              'name': 'Postadresse',
              'scope': 'DAR',
              'user_key': 'AdressePost',
              'uuid': 'a8c8fe66-2ab1-46ed-ba99-ed05e855d65f'},
             {'example': 'Postboks 29, 4260 Korsbæk',
              'name': 'Returadresse',
              'scope': 'DAR',
              'user_key': 'AdressePostRetur',
              'uuid': '2c4d87bd-ad26-4580-982f-7ea90c4512d3'},
             {'example': None,
              'name': 'Skolekode',
              'scope': 'INTEGER',
              'user_key': 'Skolekode',
              'uuid': '9ee2a20b-2687-406b-b658-55a5f4b5287b'},
             {'example': None,
              'name': 'Telefax',
              'scope': 'PHONE',
              'user_key': 'Fax',
              'uuid': '26d0da83-f43f-4feb-a7b1-d7c28d56daae'},
             {'example': '+45 3334 9400',
              'name': 'Telefonnummer',
              'scope': 'PHONE',
              'user_key': 'Telefon',
              'uuid': 'eb520fe5-eb72-4110-b81d-9c1a129dc22a'},
             {'example': 'Onsdag 10:30-11:00 Torsdag 16:00-18:00',
              'name': 'Åbningstid, henvendelse',
              'scope': 'TEXT',
              'user_key': 'Åbningstid, henvendelse',
              'uuid': '08857eb8-a2c4-4337-836f-19332f991362'},
             {'example': 'Mandag 10:00-12:00 Tirsdag 14:00-16:00',
              'name': 'Åbningstid, telefon',
              'scope': 'TEXT',
              'user_key': 'Åbningstid Telefon',
              'uuid': '0836ffbf-3b3e-410f-8cbf-face7e6844ef'}],
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/job-title/',
            [{'example': None,
              'name': 'Administrativ leder',
              'scope': None,
              'user_key': 'Administrativ leder',
              'uuid': 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee'},
             {'example': None,
              'name': 'Afdelingschef',
              'scope': None,
              'user_key': 'Afdelingschef',
              'uuid': 'cc9e7333-5031-45f2-b123-d83cbda4b9d5'},
             {'example': None,
              'name': 'Afdelingssygeplejerske',
              'scope': None,
              'user_key': 'Afdelingssygeplejerske',
              'uuid': 'fdfa8984-1b78-4014-8c35-f2a59b758bcb'},
             {'example': None,
              'name': '… (≈400 flere)',
              'scope': None,
              'user_key': '… (≈400 flere)',
              'uuid': 'f5b8f156-fa4e-46e2-b9e6-51a953166273'}],
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/f/ou/',
            [{'example': None,
              'name': 'Afsnit',
              'scope': None,
              'user_key': 'Afsnit',
              'uuid': '3498dd38-5cb5-4c19-a43d-c63ecaefacaf'},
             {'example': None,
              'name': 'Andre',
              'scope': None,
              'user_key': 'Andre',
              'uuid': '72e01813-495b-47f7-a71c-4e41dfe82813'},
             {'example': None,
              'name': 'Direktørområde',
              'scope': None,
              'user_key': 'Direktørområde',
              'uuid': '26d94be8-e164-4405-b2b3-a73807703b94'},
             {'example': None,
              'name': 'Fagligt Center',
              'scope': None,
              'user_key': 'Fagligt Center',
              'uuid': '59f10075-88f6-4758-bf61-454858170776'},
             {'example': None,
              'name': 'Institution',
              'scope': None,
              'user_key': 'Institution',
              'uuid': '547e6946-abdb-4dc2-ad99-b6042e05a7e4'},
             {'example': None,
              'name': 'Institutionsafsnit',
              'scope': None,
              'user_key': 'Institutionsafsnit',
              'uuid': '04c310a3-42a0-437b-a27c-f9ba41b65e55'},
             {'example': None,
              'name': 'Institutionsunderafsnit',
              'scope': None,
              'user_key': 'Institutionsunderafsnit',
              'uuid': '1de0c88a-dca9-4c90-931b-c60c1a0efab4'},
             {'example': None,
              'name': 'Kommune',
              'scope': None,
              'user_key': 'Kommune',
              'uuid': 'f2f93f92-d08f-4b76-904f-af9144e23195'},
             {'example': None,
              'name': 'Konsulentfunktion',
              'scope': None,
              'user_key': 'Konsulentfunktion',
              'uuid': '225342e1-7ad3-463c-9aa0-1b0341e9e316'},
             {'example': None,
              'name': 'Ledelsessekretariat',
              'scope': None,
              'user_key': 'Ledelsessekretariat',
              'uuid': '18d124f1-19c8-4401-a8ed-cdb5e90accf2'},
             {'example': None,
              'name': 'Supportcenter',
              'scope': None,
              'user_key': 'Supportcenter',
              'uuid': '7c0f22a0-e942-4333-ab69-d716de2ff8ee'},
             {'example': None,
              'name': 'Team',
              'scope': None,
              'user_key': 'Team',
              'uuid': '56cfc7f4-2e54-45e2-af27-90591fb7c664'}],
        )

        self.assertRequestResponse(
            '/service/o/3a87187c-f25a-40a1-8d42-312b2e2b43bd/e/',
            [{'name': 'Sanne Schäff',
              'uuid': '1ce40e25-6238-4202-9e93-526b348ec745'},
             {'name': 'Sune Skriver',
              'uuid': '34705881-8af9-4254-ac3f-31738eae0be8'}],
        )

        self.assertRequestResponse(
            '/service/e/1ce40e25-6238-4202-9e93-526b348ec745/',
            {
                "cpr_no": "1011101010",
                "name": "Sanne Sch\u00e4ff",
                "uuid": "1ce40e25-6238-4202-9e93-526b348ec745",
            },
        )

        self.assertRequestResponse(
            '/service/e/34705881-8af9-4254-ac3f-31738eae0be8/',
            {
                "cpr_no": "0101001010",
                "name": "Sune Skriver",
                "uuid": "34705881-8af9-4254-ac3f-31738eae0be8",
            },
        )

        self.assertRequestResponse(
            '/service/e/34705881-8af9-4254-ac3f-31738eae0be8'
            '/details/engagement',
            [{'job_function': {'example': None,
                               'name': 'Administrativ leder',
                               'scope': None,
                               'user_key': 'Administrativ leder',
                               'uuid': 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee'},
              'org_unit': {'name': 'Ballerup Kommune',
                           'user_key': 'BALLERUP',
                           'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'},
              'person': {'cpr_no': '0101001010',
                         'name': 'Sune Skriver',
                         'uuid': '34705881-8af9-4254-ac3f-31738eae0be8'},
              'type': {'example': None,
                       'name': 'Ansat',
                       'scope': None,
                       'user_key': 'Ansat',
                       'uuid': '39dd14ed-faa9-40bf-9fc9-13c440078458'},
              'uuid': 'dd30c279-8bba-43a9-b4b7-6ac96e722f86',
              'valid_from': '2018-01-01T00:00:00+01:00',
              'valid_to': None}],
        )

        self.assertRequestResponse(
            '/service/e/1ce40e25-6238-4202-9e93-526b348ec745'
            '/details/engagement',
            [{'job_function': None,
              'org_unit': {'name': 'Ballerup Kommune',
                           'user_key': 'BALLERUP',
                           'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'},
              'person': {'cpr_no': '1011101010',
                         'name': 'Sanne Schäff',
                         'uuid': '1ce40e25-6238-4202-9e93-526b348ec745'},
              'type': {'example': None,
                       'name': 'Ansat',
                       'scope': None,
                       'user_key': 'Ansat',
                       'uuid': '39dd14ed-faa9-40bf-9fc9-13c440078458'},
              'uuid': '7eadc1d9-19f5-46c7-a6db-f661c3a8fbb9',
              'valid_from': '2018-01-01T00:00:00+01:00',
              'valid_to': None}],
        )

        self.assertRequestResponse(
            '/service/ou/9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'
            '/details/engagement',
            [{'job_function': None,
              'org_unit': {'name': 'Ballerup Kommune',
                           'user_key': 'BALLERUP',
                           'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'},
              'person': {'cpr_no': '1011101010',
                         'name': 'Sanne Schäff',
                         'uuid': '1ce40e25-6238-4202-9e93-526b348ec745'},
              'type': {'example': None,
                       'name': 'Ansat',
                       'scope': None,
                       'user_key': 'Ansat',
                       'uuid': '39dd14ed-faa9-40bf-9fc9-13c440078458'},
              'uuid': '7eadc1d9-19f5-46c7-a6db-f661c3a8fbb9',
              'valid_from': '2018-01-01T00:00:00+01:00',
              'valid_to': None},
             {'job_function': {'example': None,
                               'name': 'Administrativ leder',
                               'scope': None,
                               'user_key': 'Administrativ leder',
                               'uuid': 'ee8dd627-9ff1-47c2-b900-aa3c214a31ee'},
              'org_unit': {'name': 'Ballerup Kommune',
                           'user_key': 'BALLERUP',
                           'uuid': '9f42976b-93be-4e0b-9a25-0dcb8af2f6b4'},
              'person': {'cpr_no': '0101001010',
                         'name': 'Sune Skriver',
                         'uuid': '34705881-8af9-4254-ac3f-31738eae0be8'},
              'type': {'example': None,
                       'name': 'Ansat',
                       'scope': None,
                       'user_key': 'Ansat',
                       'uuid': '39dd14ed-faa9-40bf-9fc9-13c440078458'},
              'uuid': 'dd30c279-8bba-43a9-b4b7-6ac96e722f86',
              'valid_from': '2018-01-01T00:00:00+01:00',
              'valid_to': None}],
        )
