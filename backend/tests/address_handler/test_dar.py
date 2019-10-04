#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora import exceptions
from mora.service.address_handler import dar
from . import base
from .. import util


@util.mock('dawa-addresses.json', allow_mox=True)
class DarAddressHandlerTests(base.AddressHandlerTestCase):
    handler = dar.DARAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = '0a3f50a0-23c9-32b8-e044-0003ba298018'

    def test_from_effect(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:dar:{}'.format(value)
                }]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_from_request(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'

        request = {
            'value': value
        }
        address_handler = self.handler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_get_mo_address(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'
        request = {
            'value': value
        }
        address_handler = self.handler.from_request(request)

        expected = {
            'href': None,
            'name': '0a3f50a0-23c9-32b8-e044-0003ba298018',
            'value': '0a3f50a0-23c9-32b8-e044-0003ba298018'
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'
        visibility = 'd99b500c-34b4-4771-9381-5c989eede969'
        address_handler = self.handler(value, visibility)

        expected = {
            'objekttype': 'DAR',
            'urn': 'urn:dar:{}'.format(value)
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_validation_fails_on_invalid_value(self, mock):
        # Arrange
        value = '1234'  # Not a valid DAR UUID

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            self.handler.validate_value(value)

    def test_validation_fails_on_unknown_uuid(self, mock):
        # Arrange
        value = 'e30645d3-2c2b-4b9f-9b7a-3b7fc0b4b80d'  # Not a valid DAR UUID

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_uuid(self, mock):
        # Arrange
        value = '0a3f50a0-23c9-32b8-e044-0003ba298018'

        # Act & Assert
        # Assert that no exception is raised
        self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_values(self, mock):
        # Arrange
        valid_values = [
            '0a3f50a0-23c9-32b8-e044-0003ba298018'
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self, mock):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid DAR UUID

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)

    def test_failed_lookup_from_request(self, mock):
        """Ensure that invalid DAR UUIDs fail validation on request"""
        # Arrange
        # Nonexisting DAR UUID should fail
        value = '300f16fd-fb60-4fec-8a2a-8d391e86bf3f'

        # Act & Assert
        with self.assertRaisesRegex(exceptions.HTTPException,
                                    "Invalid address"):
            request = {
                'value': value
            }
            self.handler.from_request(request)

    def test_lookup_from_request_with_force_succeeds(self, mock):
        """Ensure that validation is skipped when force is True"""
        # Arrange
        # Nonexisting DAR UUID
        value = '00000000-0000-0000-0000-000000000000'

        expected = {
            'href': None,
            'name': '00000000-0000-0000-0000-000000000000',
            'value': '00000000-0000-0000-0000-000000000000'
        }

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            request = {
                'value': value
            }
            handler = self.handler.from_request(request)
            actual = handler.get_mo_address_and_properties()
            self.assertEqual(expected, actual)

    def test_failed_lookup_from_effect(self, mock):
        """Ensure that failed effect lookups are handled appropriately"""
        # Arrange
        # Nonexisting DAR UUID should fail
        value = '300f16fd-fb60-4fec-8a2a-8d391e86bf3f'

        expected = {
            'href': None,
            'name': 'Ukendt',
            'value': '300f16fd-fb60-4fec-8a2a-8d391e86bf3f'
        }

        # Act
        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:dar:{}'.format(value)
                }]
            }
        }
        address_handler = self.handler.from_effect(effect)

        self.assertEqual(expected,
                         address_handler.get_mo_address_and_properties())
