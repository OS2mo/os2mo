import unittest
import freezegun

from mora.converters import writing
from tests.util import jsonfile_to_dict

from pprint import pprint


class TestExtendAddressesWithContactChannels(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.org_unit = jsonfile_to_dict(
            'tests/mocking/mo/org_unit_registrering_virkning_infinity.json')

    def test_should_add_zero_contact_channels_correctly(self):
        self.assertEqual(
            self.org_unit['relationer']['adresser'].copy(),
            writing._extend_addresses_with_contact_channels(self.org_unit,
                                                            []),
            'Extending incorrectly with an empty list of channels')

    @freezegun.freeze_time(tz_offset=2)
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
            writing._extend_addresses_with_contact_channels(self.org_unit,
                                                            contact_channels),
            'Extending incorrectly with two contact channels')


class TestExtendAddressesWithLocations(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.org_unit = jsonfile_to_dict(
            'tests/mocking/mo/org_unit_registrering_virkning_infinity.json')
        self.location = {
            'UUID_EnhedsAdresse': '0a3f50c3-df71-32b8-e044-0003ba298018',
            'postdistrikt': 'Risskov',
            'postnr': '8240',
            'vejnavn': 'Pilevej 5, 8240 Risskov'
        }

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

    @freezegun.freeze_time(tz_offset=1)
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
