# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from .. import util


class AddressHandlerTestCase(util.TestCase):
    handler = None
    value = None
    visibility = None

    def test_get_lora_properties(self, *args):
        # Arrange
        address_handler = self.handler(self.value, self.visibility)

        expected = [{
            'objekttype': 'synlighed',
            'uuid': self.visibility
        }]

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)
