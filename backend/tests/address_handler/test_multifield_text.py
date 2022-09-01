# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import pytest

from mora.service.address_handler.multifield_text import MultifieldTextAddressHandler


@pytest.fixture
def text_value_one() -> str:
    return "Test text whatever"


@pytest.fixture
def text_value_two() -> str:
    return "Test text whatever2"


async def test_from_effect(text_value_one, text_value_two):
    # Arrange
    effect = {
        "relationer": {
            "adresser": [
                {"urn": "urn:multifield_text:%54est%20text%20whatever"},
                {"urn": "urn:multifield_text2:%54est%20text%20whatever2"},
            ]
        }
    }

    address_handler = await MultifieldTextAddressHandler.from_effect(effect)

    # Act
    actual_value = address_handler.value
    actual_value2 = address_handler.value2

    # Assert
    assert text_value_one == actual_value
    assert text_value_two == actual_value2


async def test_from_request(text_value_one, text_value_two):
    # Arrange

    request = {"value": text_value_one, "value2": text_value_two}
    address_handler = await MultifieldTextAddressHandler.from_request(request)

    # Act
    actual_value = address_handler.value
    actual_value2 = address_handler.value2

    # Assert
    assert text_value_one == actual_value
    assert text_value_two == actual_value2


async def test_get_mo_address(text_value_one, text_value_two):
    async def async_facet_get_one_class(x, y, *args, **kwargs):
        return {"uuid": y}

    # Arrange
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    address_handler = MultifieldTextAddressHandler(
        text_value_one, visibility, text_value_two
    )

    expected = {
        "href": None,
        "name": "Test text whatever :: Test text whatever2",
        "value": "Test text whatever",
        "value2": "Test text whatever2",
        "visibility": {"uuid": "dd5699af-b233-44ef-9107-7a37016b2ed1"},
    }

    # Act
    with patch("mora.service.facet.get_one_class", new=async_facet_get_one_class):
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        assert expected == actual


async def test_get_mo_address_w_default(text_value_one):
    async def async_facet_get_one_class(x, y, *args, **kwargs):
        return {"uuid": y}

    # Arrange
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    address_handler = MultifieldTextAddressHandler(text_value_one, visibility)

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


def test_get_lora_address(text_value_one, text_value_two):
    # Arrange
    address_handler = MultifieldTextAddressHandler(text_value_one, None, text_value_two)

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
    assert expected == actual
