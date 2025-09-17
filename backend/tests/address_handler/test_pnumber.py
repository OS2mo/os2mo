# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch
from uuid import UUID

import pytest
from mora import exceptions
from mora.service.address_handler.pnumber import PNumberAddressHandler

from tests import util

VISIBILITY_UUID = UUID("dd5699af-b233-44ef-9107-7a37016b2ed1")
VALUE_STRING = "1234567890"


async def test_from_effect():
    # Arrange

    effect = {
        "relationer": {
            "adresser": [{"urn": f"urn:dk:cvr:produktionsenhed:{VALUE_STRING}"}]
        }
    }

    address_handler = await PNumberAddressHandler.from_effect(effect)

    # Act
    actual_value = address_handler.value

    # Assert
    assert VALUE_STRING == actual_value


async def test_from_request():
    # Arrange
    request = {"value": VALUE_STRING}
    address_handler = await PNumberAddressHandler.from_request(request)

    # Act
    actual_value = address_handler.value

    # Assert
    assert VALUE_STRING == actual_value


async def test_get_mo_address():
    async def async_facet_get_one_class(x, y, *args, **kwargs):
        return {"uuid": y}

    # Arrange
    address_handler = PNumberAddressHandler(VALUE_STRING, VISIBILITY_UUID)

    expected = {
        "href": None,
        "name": "1234567890",
        "value": "1234567890",
        "value2": None,
        "visibility": {"uuid": UUID("dd5699af-b233-44ef-9107-7a37016b2ed1")},
    }
    with patch("mora.service.facet.get_one_class", new=async_facet_get_one_class):
        # Act
        actual = await address_handler.get_mo_address_and_properties()

    # Assert
    assert expected == actual


def test_get_lora_address() -> None:
    # Arrange
    address_handler = PNumberAddressHandler(VALUE_STRING, None)

    expected = {
        "objekttype": "PNUMBER",
        "urn": f"urn:dk:cvr:produktionsenhed:{VALUE_STRING}",
    }

    # Act
    actual = address_handler.get_lora_address()

    # Assert
    assert expected == actual


async def test_fails_on_invalid_value():
    # Arrange
    invalid_values = ["1234", "12341234123412341234"]  # Not a valid P-number

    # Act & Assert
    for value in invalid_values:
        with pytest.raises(exceptions.HTTPException):
            await PNumberAddressHandler.validate_value(value)


async def test_validation_succeeds_on_correct_values():
    # Arrange
    valid_values = ["1234123412"]

    # Act & Assert
    for value in valid_values:
        # Shouldn't raise exception
        await PNumberAddressHandler.validate_value(value)


async def test_validation_succeeds_with_force():
    # Arrange
    value = "GARBAGEGARBAGE"  # Not a valid P-number

    # Act & Assert
    async with util.patch_query_args({"force": "1"}):
        await PNumberAddressHandler.validate_value(value)
