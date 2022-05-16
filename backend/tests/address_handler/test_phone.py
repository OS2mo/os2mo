# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

from . import base
from mora import exceptions
from mora.service.address_handler import phone
from tests import util


async def async_facet_get_one_class(x, y, *args, **kwargs):
    return {"uuid": y}


@patch("mora.service.facet.get_one_class", new=async_facet_get_one_class)
class PhoneAddressHandlerTests(base.AsyncAddressHandlerTestCase):
    handler = phone.PhoneAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = "+4512345678"

    async def test_from_effect(self):
        # Arrange
        visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
        value = "+4512345678"

        effect = {
            "relationer": {
                "adresser": [{"urn": "urn:magenta.dk:telefon:+4512345678"}],
                "opgaver": [{"objekttype": "synlighed", "uuid": visibility}],
            }
        }

        address_handler = await self.handler.from_effect(effect)

        # Act
        actual_value = address_handler._value
        actual_visibility = address_handler.visibility

        # Assert
        self.assertEqual(value, actual_value)
        self.assertEqual(visibility, actual_visibility)

    async def test_from_request(self):
        # Arrange
        visibility = "0261fdd3-4aa3-4c9b-9542-8163a1184738"
        request = {"value": "12345678", "visibility": {"uuid": visibility}}
        address_handler = await self.handler.from_request(request)

        expected_value = "12345678"

        # Act
        actual_value = address_handler._value
        actual_visibility = address_handler.visibility

        # Assert
        self.assertEqual(expected_value, actual_value)
        self.assertEqual(visibility, actual_visibility)

    async def test_get_mo_address(self):
        # Arrange
        value = "12345678"
        visibility = "d99b500c-34b4-4771-9381-5c989eede969"
        address_handler = self.handler(value, visibility)

        expected = {
            "href": "tel:12345678",
            "name": "12345678",
            "value": "12345678",
            "value2": None,
            "visibility": {"uuid": visibility},
        }

        # Act
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = "12345678"
        visibility = "d99b500c-34b4-4771-9381-5c989eede969"
        address_handler = self.handler(value, visibility)

        expected = {"objekttype": "PHONE", "urn": "urn:magenta.dk:telefon:12345678"}

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    async def test_fails_on_invalid_value(self):
        # Arrange
        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            # Not a valid phone number
            await self.handler.validate_value("asdasd")

    async def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = ["+4520931217" "12341234" "123"]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            await self.handler.validate_value(value)

    async def test_validation_succeeds_with_force(self):
        # Arrange
        value = "GARBAGEGARBAGE"  # Not a valid phone number

        # Act & Assert
        with util.patch_query_args({"force": "1"}):
            await self.handler.validate_value(value)
