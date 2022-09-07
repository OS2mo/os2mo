# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import pytest

from mora import exceptions
from mora.service.address_handler.ean import EANAddressHandler
from tests import util


@pytest.fixture
def value_fixed():
    return "1234567890123"


@pytest.fixture()
def visibility_fixed():
    return "1f6295e8-9000-43ec-b694-4d288fa158bb"


async def test_from_effect(value_fixed, visibility_fixed):
    # Arrange
    effect = {
        "relationer": {
            "adresser": [{"urn": f"urn:magenta.dk:ean:{value_fixed}"}],
            "opgaver": [{"objekttype": "synlighed", "uuid": visibility_fixed}],
        }
    }

    address_handler = await EANAddressHandler.from_effect(effect)

    # Act
    actual_value = address_handler._value
    actual_visibility = address_handler.visibility

    # Assert
    assert value_fixed == actual_value
    assert visibility_fixed == actual_visibility


async def test_from_request(value_fixed, visibility_fixed):
    # Arrange
    request = {"value": value_fixed}
    address_handler = await EANAddressHandler.from_request(request)

    # Act
    actual_value = address_handler.value

    # Assert
    assert value_fixed == actual_value


async def test_get_mo_address(value_fixed, visibility_fixed):
    async def async_facet_get_one_class(x, y, *args, **kwargs):
        return {"uuid": y}

    # Arrange
    address_handler = EANAddressHandler(value_fixed, visibility_fixed)

    expected = {
        "href": None,
        "name": value_fixed,
        "value": value_fixed,
        "value2": None,
        "visibility": {"uuid": "1f6295e8-9000-43ec-b694-4d288fa158bb"},
    }

    # Act
    with patch("mora.service.facet.get_one_class", new=async_facet_get_one_class):
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        assert expected == actual


def test_get_lora_address(value_fixed):
    # Arrange
    address_handler = EANAddressHandler(value_fixed, None)

    expected = {
        "objekttype": "EAN",
        "urn": f"urn:magenta.dk:ean:{value_fixed}",
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
    with util.patch_query_args({"force": "1"}):
        await EANAddressHandler.validate_value(value)
