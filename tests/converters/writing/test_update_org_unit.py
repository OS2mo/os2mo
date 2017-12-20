#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from mora.converters import writing
from tests.util import jsonfile_to_dict
from mora.exceptions import IllegalArgumentException

from ... import util


class TestSetup(util.TestCase):
    def setUp(self):
        self.org_unit = jsonfile_to_dict(
            'tests/mocking/mo/org_unit_registrering_virkning_infinity.json')
        self.location = {
            'UUID_EnhedsAdresse': '0a3f50c3-df71-32b8-e044-0003ba298018',
            'postdistrikt': 'Risskov',
            'postnr': '8240',
            'vejnavn': 'Pilevej 5, 8240 Risskov'
        }


class TestExtendAddressesWithContactChannels(TestSetup):
    maxDiff = None

    def test_should_add_zero_contact_channels_correctly(self):
        self.assertEqual(
            self.org_unit['relationer']['adresser'].copy(),
            writing._add_contact_channels(self.org_unit, None, []),
            'Extending incorrectly with an empty list of channels')

    def test_should_handle_contact_channels_is_none(self):
        self.assertEqual(
            self.org_unit['relationer']['adresser'].copy(),
            writing._add_contact_channels(self.org_unit, None, None),
            'Extending incorrectly when contact channels is None')

    @freezegun.freeze_time('2017-01-01', tz_offset=2)
    def test_should_add_two_contact_channels_correctly(self):
        contact_channels = [
            {
                'contact-info': '12345678',
                'type': {
                    'name': 'Telefonnummer',
                    'prefix': 'urn:magenta.dk:telefon:',
                    'uuid': 'b7ccfb21-f623-4e8f-80ce-89731f726224'
                },
                'valid-from': '20-06-2017',
                'valid-to': 'infinity',
                'visibility': {
                    'name': 'N/A',
                    'user-key': 'N/A',
                    'uuid': '00000000-0000-0000-0000-000000000000'
                }
            },
            {
                'contact-info': '87654321',
                'type': {
                    'name': 'Telefonnummer',
                    'prefix': 'urn:magenta.dk:telefon:',
                    'uuid': '00ccfb21-f623-4e8f-80ce-89731f726224'
                },
                'valid-from': '20-06-2017',
                'valid-to': 'infinity',
                'visibility': {
                    'name': 'N/A',
                    'user-key': 'N/A',
                    'uuid': '00000000-0000-0000-0000-000000000000'
                }
            }
        ]
        addresses = [{'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                      'virkning': {'from': '2017-04-30 22:00:00+00',
                                   'from_included': True,
                                   'to': 'infinity',
                                   'to_included': False}},
                     {'urn': 'urn:magenta.dk:telefon:12345678',
                      'virkning': {'from': '2017-04-30 22:00:00+00',
                                   'from_included': True,
                                   'to': 'infinity',
                                   'to_included': False}},
                     {'urn': 'urn:magenta.dk:telefon:12345678',
                      'objekttype': 'v0:N/A:1337',
                      'virkning': {'from': '2017-06-20T00:00:00+02:00',
                                   'from_included': True,
                                   'to': 'infinity',
                                   'to_included': False}},
                     {'urn': 'urn:magenta.dk:telefon:87654321',
                      'objekttype': 'v0:N/A:1337',
                      'virkning': {'from': '2017-06-20T00:00:00+02:00',
                                   'from_included': True,
                                   'to': 'infinity',
                                   'to_included': False}}]
        self.assertEqual(
            addresses,
            writing._add_contact_channels(
                self.org_unit,
                {
                    'uuid': '1337',
                },
                contact_channels
            ),
            'Extending incorrectly with two contact channels',
        )


class TestUpdateExistingAddressesForLocations(TestSetup):
    maxDiff = None

    def test_nothing_should_happen_when_uuid_is_not_found_in_addr_list(self):
        new_addr_list = writing._update_existing_address(self.org_unit,
                                                         'dummy',
                                                         self.location,
                                                         '01-01-2017',
                                                         '01-01-2020'
                                                         )
        self.assertEqual(
            self.org_unit['relationer']['adresser'],
            new_addr_list, 'Nothing should happen when UUID is not found'
        )

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    def test_should_set_addr_uuid_to_000(self):
        actual_addresses = writing._update_existing_address(
            self.org_unit,
            '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
            self.location,
            '01-01-2017',
            'infinity',
            name='The name',
            primary=True,
        )
        expected_addresses = [{'uuid': '0a3f50c3-df71-32b8-e044-0003ba298018',
                               'objekttype': 'v0:1:The name',
                               'virkning': {
                                   'from': '2017-01-01T00:00:00+01:00',
                                   'from_included': True,
                                   'to': 'infinity',
                                   'to_included': False}},
                              {'urn': 'urn:magenta.dk:telefon:12345678',
                               'virkning': {'from': '2017-04-30 22:00:00+00',
                                            'from_included': True,
                                            'to': 'infinity',
                                            'to_included': False}},
                              ]

        self.assertEqual(expected_addresses, actual_addresses,
                         'Should change addr UUID correctly')


class TestAddNewLocations(TestSetup):
    maxDiff = None

    @freezegun.freeze_time(tz_offset=+1)
    def test_should_add_new_location_correctly(self):
        actual_addresses = writing._add_location(
            self.org_unit, self.location, '01-01-2020', 'infinity',
            name='The name', primary=True,
        )
        expected_addresses = [
            {'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
             'virkning': {'from': '2017-04-30 22:00:00+00',
                          'from_included': True,
                          'to': 'infinity',
                          'to_included': False}},
            {'urn': 'urn:magenta.dk:telefon:12345678',
             'virkning': {'from': '2017-04-30 22:00:00+00',
                          'from_included': True,
                          'to': 'infinity',
                          'to_included': False}},
            {'uuid': '0a3f50c3-df71-32b8-e044-0003ba298018',
             'objekttype': 'v0:1:The name',
             'virkning': {'from': '2020-01-01T00:00:00+01:00',
                          'from_included': True,
                          'to': 'infinity',
                          'to_included': False}},
        ]
        self.assertEqual(expected_addresses, actual_addresses,
                         'Should add a new location correctly')


class TestUpdateOrgUnitAddresses(TestSetup):
    maxDiff = None

    def setUp(self):
        super().setUp()
        self.std_mock_org_unit = (
            'http://mox/organisation/organisationenhed?'
            'uuid=00000000-0000-0000-0000-000000000000'
            '&virkningfra=-infinity'
            '&virkningtil=infinity'
        )
        self.json = jsonfile_to_dict(
            'tests/mocking/lora/organisation/organisationenhed/' +
            'get_org_unit_from_uuid.json')

    @freezegun.freeze_time('2017-01-01', tz_offset=2)
    @util.mock()
    def test_should_update_add_contact_channels_correctly(self, mock):
        contact_channels = [
            {
                'contact-info': '12345678',
                'type': {
                    'name': 'Telefonnummer',
                    'prefix': 'urn:magenta.dk:telefon:',
                    'uuid': 'b7ccfb21-f623-4e8f-80ce-89731f726224'
                },
                'valid-from': '20-06-2017',
                'valid-to': 'infinity',
                'visibility': {
                    'name': 'N/A',
                    'user-key': 'N/A',
                    'uuid': '00000000-0000-0000-0000-000000000000'
                }
            },
            {
                'contact-info': '87654321',
                'type': {
                    'name': 'Telefonnummer',
                    'prefix': 'urn:magenta.dk:telefon:',
                    'uuid': '00ccfb21-f623-4e8f-80ce-89731f726224'
                },
                'valid-from': '20-06-2017',
                'valid-to': 'infinity',
                'visibility': {
                    'name': 'N/A',
                    'user-key': 'N/A',
                    'uuid': '00000000-0000-0000-0000-000000000000'
                }
            }
        ]
        addresses = {
            'note': 'Tilføj kontaktkanal',
            'relationer': {
                'adresser': [{'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                              'virkning': {'from': '2017-05-08T00:00:00+0200',
                                           'from_included': True,
                                           'to': 'infinity',
                                           'to_included': False}},
                             {'urn': 'urn:magenta.dk:telefon:12345678',
                              'virkning': {'from': '2017-05-08T00:00:00+0200',
                                           'from_included': True,
                                           'to': 'infinity',
                                           'to_included': False}},
                             {'urn': 'urn:magenta.dk:telefon:12345678',
                              'objekttype': 'v0:N/A:1337',
                              'virkning': {'from': '2017-06-20T00:00:00+02:00',
                                           'from_included': True,
                                           'to': 'infinity',
                                           'to_included': False}},
                             {'urn': 'urn:magenta.dk:telefon:87654321',
                              'objekttype': 'v0:N/A:1337',
                              'virkning': {'from': '2017-06-20T00:00:00+02:00',
                                           'from_included': True,
                                           'to': 'infinity',
                                           'to_included': False}}]
            }
        }
        mock.get(self.std_mock_org_unit, json=self.json)
        self.assertEqual(
            addresses,
            writing.update_org_unit_addresses(
                '00000000-0000-0000-0000-000000000000',
                'contact-channel',
                contact_channels=contact_channels,
                location={
                    'uuid': '1337',
                },
            ),
            'Extending incorrectly with two contact channels'
        )

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    @util.mock()
    def test_should_update_location_correctly(self, mock):
        mock.get(self.std_mock_org_unit, json=self.json)
        actual_addresses = writing.update_org_unit_addresses(
            '00000000-0000-0000-0000-000000000000',
            'location',
            address_uuid='98001816-a7cc-4115-a9e6-2c5c06c79e5d',
            location=self.location,
            name='Null Location',
            primary=True,
            From='31-12-2016',
            to='infinity'
        )
        expected_addresses = {
            'note': 'Ret adresse',
            'relationer': {
                'adresser': [
                    {'uuid': '0a3f50c3-df71-32b8-e044-0003ba298018',
                     'objekttype': 'v0:1:Null Location',
                     'virkning': {
                         'from': '2016-12-31T00:00:00+01:00',
                         'from_included': True,
                         'to': 'infinity',
                         'to_included': False}},
                    {'urn': 'urn:magenta.dk:telefon:12345678',
                     'virkning': {'from': '2017-05-08T00:00:00+0200',
                                  'from_included': True,
                                  'to': 'infinity',
                                  'to_included': False}},
                ]
            }
        }
        self.assertEqual(expected_addresses, actual_addresses,
                         'Should change addr UUID correctly')

    @freezegun.freeze_time('2017-01-01', tz_offset=1)
    @util.mock()
    def test_should_add_new_location_correctly(self, mock):
        mock.get(self.std_mock_org_unit, json=self.json)
        actual_addresses = writing.update_org_unit_addresses(
            '00000000-0000-0000-0000-000000000000',
            None,
            location=self.location,
            From='01-01-2020',
            to='infinity',
            name='Null Location',
            primary=False,
        )
        expected_addresses = {
            'note': 'Tilføj addresse',
            'relationer': {
                'adresser': [
                    {'uuid': '98001816-a7cc-4115-a9e6-2c5c06c79e5d',
                     'virkning': {'from': '2017-05-08T00:00:00+0200',
                                  'from_included': True,
                                  'to': 'infinity',
                                  'to_included': False}},
                    {'urn': 'urn:magenta.dk:telefon:12345678',
                     'virkning': {'from': '2017-05-08T00:00:00+0200',
                                  'from_included': True,
                                  'to': 'infinity',
                                  'to_included': False}},
                    {'uuid': '0a3f50c3-df71-32b8-e044-0003ba298018',
                     'objekttype': 'v0:0:Null Location',
                     'virkning': {'from': '2020-01-01T00:00:00+01:00',
                                  'from_included': True,
                                  'to': 'infinity',
                                  'to_included': False}},
                ]
            }
        }
        self.assertEqual(expected_addresses, actual_addresses,
                         'Should add a new location correctly')

    @freezegun.freeze_time('2017-01-01', tz_offset=2)
    @util.mock()
    def test_should_raise_exception_if_contact_channel_not_given(self, mock):
        mock.get(self.std_mock_org_unit, json=self.json)
        writing.update_org_unit_addresses(
            '00000000-0000-0000-0000-000000000000',
            'contact-channel',
            contact_channels=None,
            location=None,
        )
        self.assertRaises(IllegalArgumentException)

    @freezegun.freeze_time('2017-01-01', tz_offset=2)
    @util.mock()
    def test_should_handle_case_where_contact_channel_already_exists(self,
                                                                     mock):
        mock.get(self.std_mock_org_unit, json=self.json)
        expected = {
            'note': 'Tilføj eksisterende kontaktkanal',
            'relationer': {
                'adresser': []
            }
        }
        self.assertEqual(expected, writing.update_org_unit_addresses(
            '00000000-0000-0000-0000-000000000000',
            'contact-channel',
            location=None,
        ))

    @freezegun.freeze_time('2017-01-01', tz_offset=2)
    @util.mock()
    def test_should_add_first_location(self, mock):
        org = {
            "attributter": {
                "organisationenhedegenskaber": [
                    {
                        "brugervendtnoegle": "MAGENTA",
                        "enhedsnavn": "Magenta ApS",
                        "virkning": {
                            "from": "1999-11-15 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ]
            },
            "brugerref": "42c432e8-9c4a-11e6-9f62-873cf34a735f",
            "fratidspunkt": {
                "graenseindikator": True,
                "tidsstempeldatotid": "2017-12-06T13:05:37.03371+01:00"
            },
            "livscykluskode": "Importeret",
            "note": "Dette er en note.",
            "relationer": {
                "enhedstype": [
                    {
                        "uuid": "5b6d3b8c-7047-4c32-8fde-5d6e0e6c972f",
                        "virkning": {
                            "from": "1999-11-15 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ],
                "overordnet": [
                    {
                        "uuid": "8efbd074-ad2a-4e6a-afec-1d0b1891f566",
                        "virkning": {
                            "from": "1999-11-15 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ],
                "tilhoerer": [
                    {
                        "uuid": "8efbd074-ad2a-4e6a-afec-1d0b1891f566",
                        "virkning": {
                            "from": "1999-11-15 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "from": "1999-11-15 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ]
            },
            "tilstande": {
                "organisationenhedgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": "1999-11-15 00:00:00+01",
                            "from_included": True,
                            "to": "infinity",
                            "to_included": False
                        }
                    }
                ]
            },
            "tiltidspunkt": {
                "tidsstempeldatotid": "infinity"
            }
        }

        mock.get('http://mox/organisation/organisationenhed?'
                 'uuid=01e479c4-66ef-42aa-877e-15f0512f792c&'
                 'virkningtil=infinity&virkningfra=-infinity',
                 json={
                     "results": [
                         [
                             {
                                 "id": "01e479c4-66ef-42aa-877e-15f0512f792c",
                                 "registreringer": [
                                     org
                                 ]
                             }
                         ]
                     ]
                 })
        mock.put('http://mox/organisation/organisationenhed'
                 '/01e479c4-66ef-42aa-877e-15f0512f792c',
                 json={
                     'uuid': '01e479c4-66ef-42aa-877e-15f0512f792c',
                 })

        self.assertRequestResponse(
            '/o/8efbd074-ad2a-4e6a-afec-1d0b1891f566/org-unit'
            '/01e479c4-66ef-42aa-877e-15f0512f792c/role-types/location',
            {
                'uuid': '01e479c4-66ef-42aa-877e-15f0512f792c',
            },
            json={
                "valid-from": "10-04-2017",
                "location": {
                    "UUID_EnhedsAdresse":
                    "0a3f50a0-23c9-32b8-e044-0003ba298018",
                    "postdistrikt": "København K",
                    "postnr": "1112",
                    "vejnavn": "Pilestræde 43, 3., 1112 København K"
                },
                "primaer": True,
                "name": "Hovedkontoret",
                "valid-to": "infinity",
                "$$hashKey": "1TG"
            },
        )
