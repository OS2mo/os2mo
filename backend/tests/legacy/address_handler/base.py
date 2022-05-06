# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import tests.legacy.cases


class AsyncAddressHandlerTestCase(tests.legacy.cases.AsyncMockRequestContextTestCase):
    handler = None
    value = None
    visibility = None

    def test_get_lora_properties(self, *args):
        # Arrange
        address_handler = self.handler(self.value, self.visibility)

        expected = [{"objekttype": "synlighed", "uuid": self.visibility}]

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)


class AddressHandlerTestCase(tests.legacy.cases.MockRequestContextTestCase):
    handler = None
    value = None
    visibility = None

    def test_get_lora_properties(self, *args):
        # Arrange
        address_handler = self.handler(self.value, self.visibility)

        expected = [{"objekttype": "synlighed", "uuid": self.visibility}]

        # Act
        actual = address_handler.get_lora_properties()

        # Assert
        self.assertEqual(expected, actual)
