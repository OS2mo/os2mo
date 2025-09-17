# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

from mora.service.address_handler.text import TextAddressHandler


async def test_from_effect():
    # Arrange
    value = "Test text whatever"

    effect = {
        "relationer": {"adresser": [{"urn": "urn:text:%54est%20text%20whatever"}]}
    }

    address_handler = await TextAddressHandler.from_effect(effect)

    # Act
    actual_value = address_handler.value

    # Assert
    assert value == actual_value


async def test_from_request():
    # Arrange
    value = "Test text whatever"

    request = {"value": value}
    address_handler = await TextAddressHandler.from_request(request)

    # Act
    actual_value = address_handler.value

    # Assert
    assert value == actual_value


async def test_get_mo_address():
    async def async_facet_get_one_class(x, y, *args, **kwargs):
        return {"uuid": y}

    # Arrange
    value = "Test text whatever"
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    address_handler = TextAddressHandler(value, visibility)

    expected = {
        "href": None,
        "name": "Test text whatever",
        "value": "Test text whatever",
        "value2": None,
        "visibility": {"uuid": "dd5699af-b233-44ef-9107-7a37016b2ed1"},
    }

    # Act
    with patch("mora.service.facet.get_one_class", new=async_facet_get_one_class):
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        assert expected == actual


def test_get_lora_address() -> None:
    # Arrange
    value = "Test text whatever"
    address_handler = TextAddressHandler(value, None)

    expected = {"objekttype": "TEXT", "urn": "urn:text:%54est%20text%20whatever"}

    # Act
    actual = address_handler.get_lora_address()

    # Assert
    assert expected == actual
