#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from mora.service.address_handler import text
from .. import util


class TextAddressHandlerTests(util.TestCase):
    handler = text.TextAddressHandler

    def test_from_effect(self):
        # Arrange
        value = 'Test text whatever'

        effect = {
            'relationer': {
                'adresser': [{
                    'urn': 'urn:text:%54est%20text%20whatever'
                }]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_from_request(self):
        # Arrange
        value = 'Test text whatever'

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
        value = 'Test text whatever'
        address_handler = self.handler(value)

        expected = {
            'href': None,
            'name': value,
            'value': value
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = 'Test text whatever'
        address_handler = self.handler(value)

        expected = {
            'objekttype': 'TEXT',
            'urn': 'urn:text:%54est%20text%20whatever'
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_properties(self):
        # Arrange
        value = 'Test text whatever'
        address_handler = self.handler(value)

        expected = []

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)
