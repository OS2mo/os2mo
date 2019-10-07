#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest.mock import patch

from mora import exceptions
from mora.service.address_handler import phone
from . import base


@patch('mora.service.facet.get_one_class', new=lambda x, y: {'uuid': y})
class PhoneAddressHandlerTests(base.AddressHandlerTestCase):
    handler = phone.PhoneAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = '+4512345678'

    def test_from_effect(self):
        # Arrange
        visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
        value = '+4512345678'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:magenta.dk:telefon:+4512345678'
                }],
                'opgaver': [{
                    'objekttype': 'synlighed',
                    'uuid': visibility
                }]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler._value
        actual_visibility = address_handler.visibility

        # Assert
        self.assertEqual(value, actual_value)
        self.assertEqual(visibility, actual_visibility)

    def test_from_request(self):
        # Arrange
        visibility = '0261fdd3-4aa3-4c9b-9542-8163a1184738'
        request = {
            'value': '12345678',
            'visibility': {
                'uuid': visibility
            }
        }
        address_handler = self.handler.from_request(request)

        expected_value = '12345678'

        # Act
        actual_value = address_handler._value
        actual_visibility = address_handler.visibility

        # Assert
        self.assertEqual(expected_value, actual_value)
        self.assertEqual(visibility, actual_visibility)

    def test_get_mo_address(self):
        # Arrange
        value = '12345678'
        visibility = 'd99b500c-34b4-4771-9381-5c989eede969'
        address_handler = self.handler(value, visibility)

        expected = {
            'href': 'tel:12345678',
            'name': '12345678',
            'value': '12345678',
            'visibility': {
                'uuid': visibility
            }
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = '12345678'
        visibility = 'd99b500c-34b4-4771-9381-5c989eede969'
        address_handler = self.handler(value, visibility)

        expected = {
            'objekttype': 'PHONE',
            'urn': 'urn:magenta.dk:telefon:12345678'
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_fails_on_invalid_value(self):
        # Arrange
        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            # Not a valid phone number
            self.handler.validate_value('asdasd')

    def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = [
            '+4520931217'
            '12341234'
            '123'
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid phone number

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)
