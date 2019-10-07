#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from unittest.mock import patch

from mora.service.address_handler import text
from .. import util


@patch('mora.service.facet.get_one_class', new=lambda x, y: {'uuid': y})
class TextAddressHandlerTests(util.TestCase):
    handler = text.TextAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = 'Test text whatever'

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
        address_handler = self.handler(value, self.visibility)

        expected = {
            'href': None,
            'name': 'Test text whatever',
            'value': 'Test text whatever',
            'visibility': {'uuid': 'dd5699af-b233-44ef-9107-7a37016b2ed1'}
        }

        # Act
        actual = address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = 'Test text whatever'
        address_handler = self.handler(value, None)

        expected = {
            'objekttype': 'TEXT',
            'urn': 'urn:text:%54est%20text%20whatever'
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)
