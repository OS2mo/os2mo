import unittest

from mora.converters import writing
from tests.util import jsonfile_to_dict

from pprint import pprint


class TestExtendContactChannels(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.org_unit = jsonfile_to_dict(
            'tests/mocking/mo/org_unit_registrering_virkning_infinity.json')

    def test_should_add_zero_contact_channels_correctly(self):
        self.assertEqual(
            self.org_unit['relationer']['adresser'].copy(),
            writing._extend_contact_channel_adresses(self.org_unit,
                                                     []),
            'Extending incorrectly with an empty list of channels')

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
            writing._extend_contact_channel_adresses(self.org_unit,
                                                     contact_channels),
            'Extending incorrectly with two contact channels')
