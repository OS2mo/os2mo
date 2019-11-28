#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest.mock import patch

from mora import exceptions
from mora.service.address_handler import ean
from . import base


@patch('mora.service.facet.get_one_class', new=lambda x, y: {'uuid': y})
class EANAddressHandlerTests(base.AddressHandlerTestCase):
    handler = ean.EANAddressHandler
    value = '1234567890123'
    visibility = '1f6295e8-9000-43ec-b694-4d288fa158bb'

    def test_from_effect(self):
        # Arrange
        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:magenta.dk:ean:{}'.format(self.value)
                }],
                'opgaver': [{
                    'objekttype': 'synlighed',
                    'uuid': self.visibility
                }]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler._value
        actual_visibility = address_handler.visibility

        # Assert
        self.assertEqual(self.value, actual_value)
        self.assertEqual(self.visibility, actual_visibility)

    def test_from_request(self):
        # Arrange
        value = '1234567890123'

        request = {
            'value': value
        }
        address_handler = self.handler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_get_mo_address(self):
        # Arrange
        value = '1234567890123'
        address_handler = self.handler(self.value, self.visibility)

        expected = {
            'href': None,
            'name': value,
            'value': value,
            'visibility': {'uuid': '1f6295e8-9000-43ec-b694-4d288fa158bb'}
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = '1234567890123'
        address_handler = self.handler(self.value, None)

        expected = {
            'objekttype': 'EAN',
            'urn': 'urn:magenta.dk:ean:{}'.format(value)
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_fails_on_invalid_value(self):
        # Arrange
        invalid_values = [
            '1234',
            '12341234123412341234'
        ]  # Not a valid EAN

        # Act & Assert
        for value in invalid_values:
            with self.assertRaises(exceptions.HTTPException):
                self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = [
            "1234123412341"
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self):
        # Arrange
        value = 'GARBAGEGARBAGE'  # Not a valid EAN

        # Act & Assert
        with self.create_app().test_request_context('?force=1'):
            self.handler.validate_value(value)
