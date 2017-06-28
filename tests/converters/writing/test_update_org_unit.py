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
from mora.converters import writing
from tests.util import jsonfile_to_dict
from mora.exceptions import IllegalArgumentException
from mora import lora
from pprint import pprint

from ... import util


class TestSetup(unittest.TestCase):
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
            writing._add_contact_channels(self.org_unit, []),
            'Extending incorrectly with an empty list of channels')

    def test_should_handle_contact_channels_is_none(self):
        self.assertEqual(
            self.org_unit['relationer']['adresser'].copy(),
            writing._add_contact_channels(self.org_unit, None),
            'Extending incorrectly when contact channels is None')

    @freezegun.freeze_time('2017-01-01', tz_offset=2)
    def test_should_add_two_contact_channels_correctly(self):
        contact_channels = [
            {
                'contact-info': '12345678',
                'type': {
                    'name': 'Phone Number',
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
                    'name': 'Phone Number',
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
                      'virkning': {'from': '2017-06-20T00:00:00+02:00',
                                   'from_included': True,
                                   'to': 'infinity',
                                   'to_included': False}},
                     {'urn': 'urn:magenta.dk:telefon:87654321',
                      'virkning': {'from': '2017-06-20T00:00:00+02:00',
                                   'from_included': True,
                                   'to': 'infinity',
                                   'to_included': False}}]
        self.assertEqual(
            addresses,
            writing._add_contact_channels(self.org_unit,
                                          contact_channels),
            'Extending incorrectly with two contact channels')


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
            'infinity'
        )
        expected_addresses = [{'uuid': '0a3f50c3-df71-32b8-e044-0003ba298018',
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
            self.org_unit, self.location, '01-01-2020', 'infinity')
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
            '&virkningfra=2017-01-01'
            '&virkningtil=2017-01-02'
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
                    'name': 'Phone Number',
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
                    'name': 'Phone Number',
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
                              'virkning': {'from': '2017-06-20T00:00:00+02:00',
                                           'from_included': True,
                                           'to': 'infinity',
                                           'to_included': False}},
                             {'urn': 'urn:magenta.dk:telefon:87654321',
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
                contact_channels=contact_channels),
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
            From='31-12-2016',
            to='infinity'
        )
        expected_addresses = {
            'note': 'Ret adresse',
            'relationer': {
                'adresser': [
                    {'uuid': '0a3f50c3-df71-32b8-e044-0003ba298018',
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
        print(self.std_mock_org_unit)
        mock.get(self.std_mock_org_unit, json=self.json)
        actual_addresses = writing.update_org_unit_addresses(
            '00000000-0000-0000-0000-000000000000',
            None,
            location=self.location,
            From='01-01-2020',
            to='infinity'
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
            contact_channels=None)
        self.assertRaises(IllegalArgumentException)

        # TODO: add more exception tests
