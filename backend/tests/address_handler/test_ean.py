# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import pytest

from mora import exceptions
from mora.service.address_handler.ean import EANAddressHandler
from tests import util


async def async_facet_get_one_class(x, y, *args, **kwargs):
    return {"uuid": y}


def give_value():
    return "1234567890123"


def give_visibility():
    return "1f6295e8-9000-43ec-b694-4d288fa158bb"


async def test_from_effect():
    # Arrange
    effect = {
        "relationer": {
            "adresser": [{"urn": "urn:magenta.dk:ean:{}".format(give_value())}],
            "opgaver": [{"objekttype": "synlighed", "uuid": give_visibility()}],
        }
    }

    address_handler = await EANAddressHandler.from_effect(effect)

    # Act
    actual_value = address_handler._value
    actual_visibility = address_handler.visibility

    # Assert
    assert give_value() == actual_value
    assert give_visibility() == actual_visibility


async def test_from_request():
    # Arrange
    request = {"value": give_value()}
    address_handler = await EANAddressHandler.from_request(request)

    # Act
    actual_value = address_handler.value

    # Assert
    assert give_value() == actual_value


@patch("mora.service.facet.get_one_class", new=async_facet_get_one_class)
async def test_get_mo_address():
    # Arrange
    address_handler = EANAddressHandler(give_value(), give_visibility())

    expected = {
        "href": None,
        "name": give_value(),
        "value": give_value(),
        "value2": None,
        "visibility": {"uuid": "1f6295e8-9000-43ec-b694-4d288fa158bb"},
    }

    # Act
    actual = await address_handler.get_mo_address_and_properties()

    # Assert
    assert expected == actual


def test_get_lora_address():
    # Arrange
    address_handler = EANAddressHandler(give_value(), None)

    expected = {
        "objekttype": "EAN",
        "urn": "urn:magenta.dk:ean:{}".format(give_value()),
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
