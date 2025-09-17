# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from mora import exceptions
from mora.service.address_handler.uuidaddr import UUIDAddressHandler

VALUE_FIXED = "2a3c2eb4-088b-4386-b2fd-ac152b203f05"
VISIBILITY_FIXED = "1f6295e8-9000-43ec-b694-4d288fa158bb"


async def test_from_effect():
    # Arrange
    effect = {
        "relationer": {
            "adresser": [{"urn": f"urn:magenta.dk:uuid:{VALUE_FIXED}"}],
            "opgaver": [{"objekttype": "synlighed", "uuid": VISIBILITY_FIXED}],
        }
    }

    address_handler = await UUIDAddressHandler.from_effect(effect)

    # Act
    actual_value = address_handler._value
    actual_visibility = address_handler.visibility

    # Assert
    assert VALUE_FIXED == actual_value
    assert VISIBILITY_FIXED == actual_visibility


async def test_from_request():
    # Arrange
    request = {"value": VALUE_FIXED}
    address_handler = await UUIDAddressHandler.from_request(request)

    # Act
    actual_value = address_handler.value

    # Assert
    assert VALUE_FIXED == actual_value


def test_get_lora_address() -> None:
    # Arrange
    address_handler = UUIDAddressHandler(VALUE_FIXED, None)

    expected = {
        "objekttype": "UUID",
        "urn": f"urn:magenta.dk:uuid:{VALUE_FIXED}",
    }

    # Act
    actual = address_handler.get_lora_address()

    # Assert
    assert expected == actual


async def test_fails_on_invalid_value():
    # Arrange
    invalid_values = [
        "{c4dbf00d-7224-4596-8104-9d7859d64651}",
        "3a97-aac46fc9-417f8b96-9d1ed6d5-27ec",
        "uuid:3a97-aac46fc9-417f8b96-9d1ed6d5-27ec",
        "urn:uuid:3a97-aac46fc9-417f8b96-9d1ed6d5-27ec",
    ]

    # Act & Assert
    for value in invalid_values:
        with pytest.raises(exceptions.HTTPException):
            await UUIDAddressHandler.validate_value(value)


async def test_validation_succeeds_on_correct_values():
    # Arrange
    valid_values = [
        "25d7e8f1-1ca6-4829-b567-d2c0c283ea07",
        "f45f2f2a-a780-47d6-97c7-dA6d639dbde7",
    ]

    # Act & Assert
    for value in valid_values:
        # Shouldn't raise exception
        await UUIDAddressHandler.validate_value(value)
