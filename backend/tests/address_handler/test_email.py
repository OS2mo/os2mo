# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import patch

import pytest
from mora import exceptions
from mora.service.address_handler.email import EmailAddressHandler

from tests import util


async def async_facet_get_one_class(x, y, *args, **kwargs):
    return {"uuid": y}


VISIBILITY = "dd5699af-b233-44ef-9107-7a37016b2ed1"

VALUE = "mail@mail.dk"


async def test_from_effect():
    # Arrange
    effect = {"relationer": {"adresser": [{"urn": f"urn:mailto:{VALUE}"}]}}

    address_handler = await EmailAddressHandler.from_effect(effect)

    # Act
    actual_value = address_handler.value

    # Assert
    assert VALUE == actual_value


async def test_from_request():
    # Arrange
    request = {"value": VALUE}
    address_handler = await EmailAddressHandler.from_request(request)

    # Act
    actual_value = address_handler.value

    # Assert
    assert VALUE == actual_value


@patch("mora.service.facet.get_one_class", new=async_facet_get_one_class)
async def test_get_mo_address():
    # Arrange
    address_handler = EmailAddressHandler(VALUE, VISIBILITY)

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
    assert expected == actual


def test_get_lora_address() -> None:
    # Arrange
    address_handler = EmailAddressHandler(VALUE, None)

    expected = {"objekttype": "EMAIL", "urn": f"urn:mailto:{VALUE}"}

    # Act
    actual = address_handler.get_lora_address()

    # Assert
    assert expected == actual


async def test_fails_on_invalid_value():
    # Arrange
    value = "asdasd"  # Not a valid email address

    # Act & Assert
    with pytest.raises(exceptions.HTTPException):
        await EmailAddressHandler.validate_value(value)


async def test_validation_succeeds_on_correct_values():
    # Arrange
    valid_values = ["test@test.com", "test+hest@test.com", "t.e.s.t@test.com"]

    # Act & Assert
    for value in valid_values:
        # Shouldn't raise exception
        await EmailAddressHandler.validate_value(value)


async def test_validation_succeeds_with_force():
    # Arrange
    value = "GARBAGEGARBAGE"  # Not a valid email address

    # Act & Assert
    async with util.patch_query_args({"force": "1"}):
        await EmailAddressHandler.validate_value(value)
