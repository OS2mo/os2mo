# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from tests import util
from unittest.mock import patch

import mora.async_util
import tests.cases
from mora import exceptions
from mora.service.address_handler import pnumber


async def async_facet_get_one_class(x, y, *args, **kwargs):
    return {"uuid": y}


@patch("mora.service.facet.get_one_class", new=async_facet_get_one_class)
class PNumberAddressHandlerTests(tests.cases.MockRequestContextTestCase):
    handler = pnumber.PNumberAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = "1234567890"

    def test_from_effect(self):
        # Arrange
        value = "1234567890"

        effect = {
            "relationer": {
                "adresser": [{"urn": "urn:dk:cvr:produktionsenhed:{}".format(value)}]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    def test_from_request(self):
        # Arrange
        value = "1234567890"

        request = {"value": value}
        address_handler = self.handler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    @mora.async_util.async_to_sync
    async def test_get_mo_address(self):
        # Arrange
        value = "1234567890"
        address_handler = self.handler(value, self.visibility)

        expected = {
            "href": None,
            "name": "1234567890",
            "value": "1234567890",
            "value2": None,
            "visibility": {"uuid": "dd5699af-b233-44ef-9107-7a37016b2ed1"},
        }

        # Act
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = "1234567890"
        address_handler = self.handler(value, None)

        expected = {
            "objekttype": "PNUMBER",
            "urn": "urn:dk:cvr:produktionsenhed:{}".format(value),
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    def test_fails_on_invalid_value(self):
        # Arrange
        invalid_values = ["1234", "12341234123412341234"]  # Not a valid P-number

        # Act & Assert
        for value in invalid_values:
            with self.assertRaises(exceptions.HTTPException):
                self.handler.validate_value(value)

    def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = ["1234123412"]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            self.handler.validate_value(value)

    def test_validation_succeeds_with_force(self):
        # Arrange
        value = "GARBAGEGARBAGE"  # Not a valid P-number

        # Act & Assert
        with util.patch_query_args({"force": "1"}):
            self.handler.validate_value(value)
