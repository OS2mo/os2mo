# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from tests import util
from unittest.mock import patch

from mora.async_util import async_to_sync
import tests.cases
from mora import exceptions
from mora.service.address_handler import email


async def async_facet_get_one_class(x, y, *args, **kwargs):
    return {"uuid": y}


@patch("mora.service.facet.get_one_class", new=async_facet_get_one_class)
class EmailAddressHandlerTests(tests.cases.MockRequestContextTestCase):
    handler = email.EmailAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = "mail@mail.dk"

    @async_to_sync
    async def test_from_effect(self):
        # Arrange
        value = "mail@mail.dk"

        effect = {"relationer": {"adresser": [{"urn": "urn:mailto:{}".format(value)}]}}

        address_handler = await self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    @async_to_sync
    async def test_from_request(self):
        # Arrange
        value = "mail@mail.dk"

        request = {"value": value}
        address_handler = await self.handler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    @async_to_sync
    async def test_get_mo_address(self):
        # Arrange
        address_handler = self.handler(self.value, self.visibility)

        expected = {
            "href": "mailto:mail@mail.dk",
            "name": "mail@mail.dk",
            "value": "mail@mail.dk",
            "value2": None,
            "visibility": {"uuid": "dd5699af-b233-44ef-9107-7a37016b2ed1"},
        }

        # Act
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = "mail@mail.dk"
        address_handler = self.handler(value, None)

        expected = {"objekttype": "EMAIL", "urn": "urn:mailto:{}".format(value)}

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    @async_to_sync
    async def test_fails_on_invalid_value(self):
        # Arrange
        value = "asdasd"  # Not a valid email address

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            await self.handler.validate_value(value)

    @async_to_sync
    async def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = ["test@test.com", "test+hest@test.com", "t.e.s.t@test.com"]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            await self.handler.validate_value(value)

    @async_to_sync
    async def test_validation_succeeds_with_force(self):
        # Arrange
        value = "GARBAGEGARBAGE"  # Not a valid email address

        # Act & Assert
        with util.patch_query_args({"force": "1"}):
            await self.handler.validate_value(value)
