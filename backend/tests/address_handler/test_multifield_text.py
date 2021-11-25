# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import mora.async_util
from mora.service.address_handler.multifield_text import MultifieldTextAddressHandler
from tests.cases import TestCase


async def async_facet_get_one_class(x, y, *args, **kwargs):
    return {"uuid": y}


@patch("mora.service.facet.get_one_class", new=async_facet_get_one_class)
class TextAddressHandlerTests(TestCase):
    handler = MultifieldTextAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = "Test text whatever"

    def test_from_effect(self):
        # Arrange
        value = "Test text whatever"
        value2 = "Test text whatever2"

        effect = {
            "relationer": {
                "adresser": [
                    {"urn": "urn:multifield_text:%54est%20text%20whatever"},
                    {"urn": "urn:multifield_text2:%54est%20text%20whatever2"},
                ]
            }
        }

        address_handler = self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value
        actual_value2 = address_handler.value2

        # Assert
        self.assertEqual(value, actual_value)
        self.assertEqual(value2, actual_value2)

    def test_from_request(self):
        # Arrange
        value = "Test text whatever"
        value2 = "Test text whatever2"

        request = {"value": value, "value2": value2}
        address_handler = self.handler.from_request(request)

        # Act
        actual_value = address_handler.value
        actual_value2 = address_handler.value2

        # Assert
        self.assertEqual(value, actual_value)
        self.assertEqual(value2, actual_value2)

    @mora.async_util.async_to_sync
    async def test_get_mo_address(self):
        # Arrange
        value = "Test text whatever"
        value2 = "Test text whatever2"
        address_handler = self.handler(value, self.visibility, value2)

        expected = {
            "href": None,
            "name": "Test text whatever :: Test text whatever2",
            "value": "Test text whatever",
            "value2": "Test text whatever2",
            "visibility": {"uuid": "dd5699af-b233-44ef-9107-7a37016b2ed1"},
        }

        # Act
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    @mora.async_util.async_to_sync
    async def test_get_mo_address_w_default(self):
        # Arrange
        value = "Test text whatever"
        address_handler = self.handler(value, self.visibility)

        expected = {
            "href": None,
            "name": "Test text whatever",
            "value": "Test text whatever",
            "value2": None,
            "visibility": {"uuid": "dd5699af-b233-44ef-9107-7a37016b2ed1"},
        }

        # Act
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = "Test text whatever"
        value2 = "Test text whatever2"
        address_handler = self.handler(value, None, value2)

        expected = [
            {
                "objekttype": "MULTIFIELD_TEXT",
                "urn": "urn:multifield_text:%54est%20text%20whatever",
            },
            {
                "objekttype": "MULTIFIELD_TEXT",
                "urn": "urn:multifield_text2:%54est%20text%20whatever2",
            },
        ]

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)
