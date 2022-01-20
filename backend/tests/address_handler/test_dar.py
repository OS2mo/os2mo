# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from mora.async_util import async_to_sync
from mora import exceptions
from mora.service.address_handler import dar

from . import base
from .. import util
from ..util import dar_loader


class DarAddressHandlerTests(base.AddressHandlerTestCase):
    handler = dar.DARAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = "0a3f50a0-23c9-32b8-e044-0003ba298018"

    @dar_loader()
    @async_to_sync
    @util.darmock("dawa-addresses.json", real_http=True)
    async def test_from_effect(self, mock):
        # Arrange
        value = "0a3f50a0-23c9-32b8-e044-0003ba298018"

        effect = {"relationer": {"adresser": [{"urn": "urn:dar:{}".format(value)}]}}

        address_handler = await self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    @dar_loader()
    @async_to_sync
    @util.darmock("dawa-addresses.json", real_http=True)
    async def test_from_request(self, mock):
        # Arrange
        value = "0a3f50a0-23c9-32b8-e044-0003ba298018"

        request = {"value": value}
        address_handler = await self.handler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    @dar_loader()
    @async_to_sync
    @util.darmock("dawa-addresses.json", real_http=True)
    async def test_get_mo_address(self, mock):
        # Arrange
        value = "0a3f50a0-23c9-32b8-e044-0003ba298018"
        request = {"value": value}
        address_handler = await self.handler.from_request(request)

        expected = {
            "href": None,
            "name": "0a3f50a0-23c9-32b8-e044-0003ba298018",
            "value": "0a3f50a0-23c9-32b8-e044-0003ba298018",
            "value2": None,
        }

        # Act
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = "0a3f50a0-23c9-32b8-e044-0003ba298018"
        visibility = "d99b500c-34b4-4771-9381-5c989eede969"
        address_handler = self.handler(value, visibility)

        expected = {"objekttype": "DAR", "urn": "urn:dar:{}".format(value)}

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    @dar_loader()
    @async_to_sync
    async def test_validation_fails_on_invalid_value(self):
        # Arrange
        value = "1234"  # Not a valid DAR UUID

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            await self.handler.validate_value(value)

    @dar_loader()
    @async_to_sync
    async def test_validation_fails_on_unknown_uuid(self):
        # Arrange
        value = "e30645d3-2c2b-4b9f-9b7a-3b7fc0b4b80d"  # Not a valid DAR UUID

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            await self.handler.validate_value(value)

    @dar_loader()
    @async_to_sync
    async def test_validation_succeeds_on_correct_uuid(self):
        # Arrange
        value = "0a3f50a0-23c9-32b8-e044-0003ba298018"

        # Act & Assert
        # Assert that no exception is raised
        await self.handler.validate_value(value)

    @dar_loader()
    @async_to_sync
    async def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = ["0a3f50a0-23c9-32b8-e044-0003ba298018"]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            await self.handler.validate_value(value)

    @async_to_sync
    async def test_validation_succeeds_with_force(self):
        # Arrange
        value = "GARBAGEGARBAGE"  # Not a valid DAR UUID

        # Act & Assert
        with util.patch_query_args({"force": "1"}):
            await self.handler.validate_value(value)

    @dar_loader()
    @async_to_sync
    async def test_failed_lookup_from_request(self):
        """Ensure that invalid DAR UUIDs fail validation on request"""
        # Arrange
        # Nonexisting DAR UUID should fail
        value = "300f16fd-fb60-4fec-8a2a-8d391e86bf3f"

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException) as err:
            request = {"value": value}
            await self.handler.from_request(request)
        self.assertEqual(
            {
                "description": "Invalid address",
                "error": True,
                "error_key": "V_INVALID_ADDRESS_DAR",
                "status": 400,
                "value": "300f16fd-fb60-4fec-8a2a-8d391e86bf3f",
            },
            err.exception.detail,
        )

    @async_to_sync
    async def test_lookup_from_request_with_force_succeeds(self):
        """Ensure that validation is skipped when force is True"""
        # Arrange
        # Nonexisting DAR UUID
        value = "00000000-0000-0000-0000-000000000000"

        expected = {
            "href": None,
            "name": "00000000-0000-0000-0000-000000000000",
            "value": "00000000-0000-0000-0000-000000000000",
            "value2": None,
        }

        # Act & Assert

        with util.patch_query_args({"force": "1"}):
            request = {"value": value}
            handler = await self.handler.from_request(request)
            actual = await handler.get_mo_address_and_properties()
            self.assertEqual(expected, actual)

    @dar_loader()
    @async_to_sync
    @util.darmock("dawa-addresses.json", real_http=True)
    async def test_failed_lookup_from_effect(self, mock):
        """Ensure that failed effect lookups are handled appropriately"""
        # Arrange
        # Nonexisting DAR UUID should fail
        value = "300f16fd-fb60-4fec-8a2a-8d391e86bf3f"

        expected = {
            "href": None,
            "name": "Ukendt",
            "value": "300f16fd-fb60-4fec-8a2a-8d391e86bf3f",
            "value2": None,
        }

        # Act
        effect = {"relationer": {"adresser": [{"urn": "urn:dar:{}".format(value)}]}}
        address_handler = await self.handler.from_effect(effect)

        self.assertEqual(expected, await address_handler.get_mo_address_and_properties())
