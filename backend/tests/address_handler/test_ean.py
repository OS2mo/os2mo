# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import pytest
from mora import exceptions
from mora.service.address_handler.ean import EANAddressHandler

from tests import util

VALUE_FIXED = "1234567890123"
VISIBILITY_FIXED = "1f6295e8-9000-43ec-b694-4d288fa158bb"


async def test_from_effect():
    # Arrange
    effect = {
        "relationer": {
            "adresser": [{"urn": f"urn:magenta.dk:ean:{VALUE_FIXED}"}],
            "opgaver": [{"objekttype": "synlighed", "uuid": VISIBILITY_FIXED}],
        }
    }

    address_handler = await EANAddressHandler.from_effect(effect)

    # Act
    actual_value = address_handler._value
    actual_visibility = address_handler.visibility

    # Assert
    assert VALUE_FIXED == actual_value
    assert VISIBILITY_FIXED == actual_visibility


async def test_from_request():
    # Arrange
    request = {"value": VALUE_FIXED}
    address_handler = await EANAddressHandler.from_request(request)

    # Act
    actual_value = address_handler.value

    # Assert
    assert VALUE_FIXED == actual_value


async def test_get_mo_address():
    async def async_facet_get_one_class(x, y, *args, **kwargs):
        return {"uuid": y}

    # Arrange
    address_handler = EANAddressHandler(VALUE_FIXED, VISIBILITY_FIXED)

    expected = {
        "href": None,
        "name": VALUE_FIXED,
        "value": VALUE_FIXED,
        "value2": None,
        "visibility": {"uuid": "1f6295e8-9000-43ec-b694-4d288fa158bb"},
    }

    # Act
    with patch("mora.service.facet.get_one_class", new=async_facet_get_one_class):
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        assert expected == actual


def test_get_lora_address() -> None:
    # Arrange
    address_handler = EANAddressHandler(VALUE_FIXED, None)

    expected = {
        "objekttype": "EAN",
        "urn": f"urn:magenta.dk:ean:{VALUE_FIXED}",
    }

    # Act
    actual = address_handler.get_lora_address()

    # Assert
    assert expected == actual


async def test_fails_on_invalid_value():
    # Arrange
    invalid_values = ["1234", "12341234123412341234"]  # Not a valid EAN

    # Act & Assert
    for value in invalid_values:
        with pytest.raises(exceptions.HTTPException):
            await EANAddressHandler.validate_value(value)


async def test_validation_succeeds_on_correct_values():
    # Arrange
    valid_values = ["1234123412341"]

    # Act & Assert
    for value in valid_values:
        # Shouldn't raise exception
        await EANAddressHandler.validate_value(value)


async def test_validation_succeeds_with_force():
    # Arrange
    value = "GARBAGEGARBAGE"  # Not a valid EAN

    # Act & Assert
    async with util.patch_query_args({"force": "1"}):
        await EANAddressHandler.validate_value(value)
